"""
Clasificador de documentos usando PyTorch con Transformer fine-tuned.

Implementa custom training loop con AdamW, warmup scheduler,
gradient clipping y early stopping para clasificacion de
documentos medicos.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

from app.utils.logger import get_logger

logger = get_logger(__name__)

LABELS: dict[int, str] = {
    0: "receta",
    1: "laboratorio",
    2: "nota_medica",
    3: "referencia",
    4: "consentimiento",
    5: "otro",
}


class MedicalDocDataset(Dataset):
    """Dataset custom para documentos medicos.

    Tokeniza textos y los prepara como tensores PyTorch para
    entrenamiento del clasificador Transformer.
    """

    def __init__(
        self,
        texts: list[str],
        labels: list[int],
        tokenizer: Any,
        max_length: int = 512,
    ) -> None:
        """Inicializa el dataset.

        Args:
            texts: Lista de textos.
            labels: Lista de labels enteros.
            tokenizer: HuggingFace tokenizer.
            max_length: Longitud maxima de secuencia.
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        encoding = self.tokenizer(
            self.texts[idx],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label": torch.tensor(self.labels[idx], dtype=torch.long),
        }


class TransformerDocClassifier(nn.Module):
    """Clasificador de documentos con BERT/RoBERTa encoder.

    Arquitectura:
    BERT encoder -> Mean pooling -> Dropout(0.3)
    -> Linear(hidden_size, 256) -> ReLU -> Dropout(0.2)
    -> Linear(256, num_classes)
    """

    def __init__(
        self,
        model_name: str = "dccuchile/bert-base-spanish-wwm-cased",
        num_classes: int = 6,
        dropout: float = 0.3,
    ) -> None:
        """Inicializa el clasificador.

        Args:
            model_name: Nombre del modelo base de HuggingFace.
            num_classes: Numero de clases de salida.
            dropout: Tasa de dropout.
        """
        super().__init__()
        self.model_name = model_name
        self.num_classes = num_classes

        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size

        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(dropout * 0.67),
            nn.Linear(256, num_classes),
        )

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass.

        Args:
            input_ids: Token IDs (batch_size, seq_len).
            attention_mask: Attention mask (batch_size, seq_len).

        Returns:
            Logits (batch_size, num_classes).
        """
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden = outputs.last_hidden_state  # (batch, seq_len, hidden)

        # Mean pooling over non-padding tokens
        mask_expanded = attention_mask.unsqueeze(-1).float()
        sum_hidden = (last_hidden * mask_expanded).sum(dim=1)
        count = mask_expanded.sum(dim=1).clamp(min=1e-9)
        pooled = sum_hidden / count  # (batch, hidden)

        return self.classifier(pooled)


@dataclass
class TrainingHistory:
    """Historial de entrenamiento."""

    train_losses: list[float] = field(default_factory=list)
    val_losses: list[float] = field(default_factory=list)
    train_f1s: list[float] = field(default_factory=list)
    val_f1s: list[float] = field(default_factory=list)
    best_val_f1: float = 0.0
    best_epoch: int = 0
    total_time_seconds: float = 0.0


class TransformerTrainer:
    """Custom training loop con metricas detalladas."""

    def __init__(
        self,
        model: TransformerDocClassifier,
        device: Optional[torch.device] = None,
    ) -> None:
        """Inicializa el trainer.

        Args:
            model: Modelo a entrenar.
            device: Dispositivo (cuda/cpu).
        """
        self.model = model
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 10,
        lr: float = 2e-5,
        weight_decay: float = 0.01,
        warmup_steps: int = 0,
        max_grad_norm: float = 1.0,
        patience: int = 3,
        save_path: Optional[str] = None,
    ) -> TrainingHistory:
        """Training loop completo.

        Incluye:
        - AdamW optimizer con weight decay
        - Linear warmup + cosine annealing scheduler
        - Gradient clipping
        - Early stopping en val F1
        - Guardado del mejor modelo

        Args:
            train_loader: DataLoader de entrenamiento.
            val_loader: DataLoader de validacion.
            epochs: Numero de epochs.
            lr: Learning rate.
            weight_decay: Weight decay para AdamW.
            warmup_steps: Steps de warmup.
            max_grad_norm: Norma maxima para gradient clipping.
            patience: Epochs sin mejora para early stopping.
            save_path: Directorio para guardar mejor modelo.

        Returns:
            TrainingHistory con metricas por epoch.
        """
        start_time = time.perf_counter()

        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=lr,
            weight_decay=weight_decay,
        )

        total_steps = len(train_loader) * epochs
        if warmup_steps == 0:
            warmup_steps = int(total_steps * 0.1)

        scheduler = torch.optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=lr,
            total_steps=total_steps,
            pct_start=warmup_steps / max(total_steps, 1),
            anneal_strategy="cos",
        )

        criterion = nn.CrossEntropyLoss()
        history = TrainingHistory()
        epochs_no_improve = 0

        for epoch in range(epochs):
            train_loss, train_f1 = self._train_epoch(
                train_loader, optimizer, scheduler, criterion, max_grad_norm
            )
            val_loss, val_f1, val_report = self._evaluate(val_loader, criterion)

            history.train_losses.append(train_loss)
            history.val_losses.append(val_loss)
            history.train_f1s.append(train_f1)
            history.val_f1s.append(val_f1)

            logger.info(
                "epoch_completed",
                epoch=epoch + 1,
                train_loss=f"{train_loss:.4f}",
                val_loss=f"{val_loss:.4f}",
                train_f1=f"{train_f1:.4f}",
                val_f1=f"{val_f1:.4f}",
            )

            if val_f1 > history.best_val_f1:
                history.best_val_f1 = val_f1
                history.best_epoch = epoch + 1
                epochs_no_improve = 0
                if save_path:
                    self._save_checkpoint(save_path, epoch, val_f1)
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    logger.info("early_stopping", epoch=epoch + 1, patience=patience)
                    break

        history.total_time_seconds = time.perf_counter() - start_time
        return history

    def evaluate(self, dataloader: DataLoader) -> dict[str, Any]:
        """Evaluacion completa con metricas detalladas.

        Args:
            dataloader: DataLoader de evaluacion.

        Returns:
            Diccionario con accuracy, F1, precision, recall, confusion matrix.
        """
        from sklearn.metrics import (
            accuracy_score,
            classification_report,
            confusion_matrix,
            f1_score,
            precision_score,
            recall_score,
        )

        criterion = nn.CrossEntropyLoss()
        _, _, report_data = self._evaluate(dataloader, criterion)

        all_preds = report_data["predictions"]
        all_labels = report_data["labels"]

        accuracy = accuracy_score(all_labels, all_preds)
        f1_macro = f1_score(all_labels, all_preds, average="macro", zero_division=0)
        f1_per_class = f1_score(all_labels, all_preds, average=None, zero_division=0)
        precision = precision_score(all_labels, all_preds, average="macro", zero_division=0)
        recall = recall_score(all_labels, all_preds, average="macro", zero_division=0)
        cm = confusion_matrix(all_labels, all_preds)
        report = classification_report(
            all_labels, all_preds,
            target_names=[LABELS.get(i, f"class_{i}") for i in range(self.model.num_classes)],
            zero_division=0,
        )

        return {
            "accuracy": accuracy,
            "f1_macro": f1_macro,
            "f1_per_class": f1_per_class.tolist(),
            "precision": precision,
            "recall": recall,
            "confusion_matrix": cm.tolist(),
            "classification_report": report,
        }

    def predict(self, texts: list[str], tokenizer: Any, max_length: int = 512) -> list[dict]:
        """Predice clases para una lista de textos.

        Args:
            texts: Textos a clasificar.
            tokenizer: HuggingFace tokenizer.
            max_length: Longitud maxima.

        Returns:
            Lista de dicts con predicted_class, confidence, probabilities.
        """
        self.model.eval()
        results: list[dict] = []

        with torch.no_grad():
            for text in texts:
                encoding = tokenizer(
                    text,
                    max_length=max_length,
                    padding="max_length",
                    truncation=True,
                    return_tensors="pt",
                ).to(self.device)

                logits = self.model(
                    encoding["input_ids"],
                    encoding["attention_mask"],
                )
                probs = torch.nn.functional.softmax(logits, dim=-1)[0]
                pred_idx = int(torch.argmax(probs))

                results.append({
                    "predicted_class": LABELS.get(pred_idx, f"class_{pred_idx}"),
                    "confidence": float(probs[pred_idx]),
                    "probabilities": {
                        LABELS.get(i, f"class_{i}"): float(probs[i])
                        for i in range(len(probs))
                    },
                })

        return results

    def _train_epoch(
        self,
        dataloader: DataLoader,
        optimizer: torch.optim.Optimizer,
        scheduler: Any,
        criterion: nn.Module,
        max_grad_norm: float,
    ) -> tuple[float, float]:
        """Una epoch de entrenamiento."""
        from sklearn.metrics import f1_score

        self.model.train()
        total_loss = 0.0
        all_preds: list[int] = []
        all_labels: list[int] = []

        for batch in dataloader:
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["label"].to(self.device)

            optimizer.zero_grad()
            logits = self.model(input_ids, attention_mask)
            loss = criterion(logits, labels)
            loss.backward()

            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
            optimizer.step()
            scheduler.step()

            total_loss += loss.item()
            preds = torch.argmax(logits, dim=-1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

        avg_loss = total_loss / max(len(dataloader), 1)
        f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
        return avg_loss, f1

    @torch.no_grad()
    def _evaluate(
        self,
        dataloader: DataLoader,
        criterion: nn.Module,
    ) -> tuple[float, float, dict[str, Any]]:
        """Evaluacion sin gradientes."""
        from sklearn.metrics import f1_score

        self.model.eval()
        total_loss = 0.0
        all_preds: list[int] = []
        all_labels: list[int] = []

        for batch in dataloader:
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["label"].to(self.device)

            logits = self.model(input_ids, attention_mask)
            loss = criterion(logits, labels)
            total_loss += loss.item()

            preds = torch.argmax(logits, dim=-1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

        avg_loss = total_loss / max(len(dataloader), 1)
        f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)

        return avg_loss, f1, {"predictions": all_preds, "labels": all_labels}

    def _save_checkpoint(self, path: str, epoch: int, val_f1: float) -> None:
        """Guarda checkpoint del modelo."""
        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)

        torch.save({
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "val_f1": val_f1,
            "model_name": self.model.model_name,
            "num_classes": self.model.num_classes,
        }, save_dir / "best_model.pt")

        logger.info("checkpoint_saved", epoch=epoch, val_f1=f"{val_f1:.4f}")
