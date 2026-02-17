"""
Clasificador de documentos medicos usando HuggingFace Transformers.

Fine-tunea modelo BERT/RoBERTa en espanol para clasificar
tipo de documento medico (receta, laboratorio, nota_medica, etc.).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    Trainer,
    TrainingArguments,
)

from app.utils.logger import get_logger

logger = get_logger(__name__)


DOCUMENT_LABELS: dict[int, str] = {
    0: "receta",
    1: "laboratorio",
    2: "nota_medica",
    3: "referencia",
    4: "consentimiento",
    5: "otro",
}

LABEL_TO_ID: dict[str, int] = {v: k for k, v in DOCUMENT_LABELS.items()}


@dataclass
class ClassificationResult:
    """Resultado de clasificacion de documento."""

    document_type: str
    confidence: float
    all_probabilities: dict[str, float] = field(default_factory=dict)
    model_used: str = ""
    processing_time_ms: int = 0


class DocumentClassifier:
    """Clasificador de tipo de documento medico con Transformers."""

    BASE_MODEL = "PlanTL-GOB-ES/roberta-base-biomedical-clinical-es"
    FALLBACK_MODEL = "dccuchile/bert-base-spanish-wwm-cased"
    MAX_LENGTH = 512

    def __init__(self, model_path: Optional[str] = None) -> None:
        """Inicializa el clasificador.

        Args:
            model_path: Ruta al modelo fine-tuned. Si None, usa modelo base
                con clasificacion heuristica hasta que se entrene.
        """
        self.model_path = model_path
        self._model: Optional[PreTrainedModel] = None
        self._tokenizer: Optional[PreTrainedTokenizerBase] = None
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._is_fine_tuned = False

    @property
    def model(self) -> PreTrainedModel:
        """Lazy-load del modelo."""
        if self._model is None:
            self._load_model()
        return self._model  # type: ignore[return-value]

    @property
    def tokenizer(self) -> PreTrainedTokenizerBase:
        """Lazy-load del tokenizer."""
        if self._tokenizer is None:
            self._load_model()
        return self._tokenizer  # type: ignore[return-value]

    def _load_model(self) -> None:
        """Carga modelo y tokenizer."""
        if self.model_path and Path(self.model_path).exists():
            logger.info("loading_fine_tuned_classifier", path=self.model_path)
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path,
            ).to(self._device)
            self._is_fine_tuned = True
            return

        logger.info("no_fine_tuned_model_using_heuristic_classifier")
        self._is_fine_tuned = False

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.BASE_MODEL)
        except Exception:
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(self.FALLBACK_MODEL)
            except Exception:
                self._tokenizer = None

    def classify(self, text: str) -> ClassificationResult:
        """Clasifica el tipo de documento.

        Si hay un modelo fine-tuned disponible, lo usa.
        Si no, usa clasificacion heuristica basada en keywords.

        Args:
            text: Texto del documento a clasificar.

        Returns:
            ClassificationResult con label y probabilidades.
        """
        start_time = time.perf_counter()

        if not text or not text.strip():
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ClassificationResult(
                document_type="otro",
                confidence=0.0,
                all_probabilities={v: 0.0 for v in DOCUMENT_LABELS.values()},
                model_used="empty_input",
                processing_time_ms=elapsed_ms,
            )

        if self._is_fine_tuned and self._model is not None:
            result = self._classify_with_model(text)
        else:
            result = self._classify_heuristic(text)

        result.processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        return result

    def _classify_with_model(self, text: str) -> ClassificationResult:
        """Clasifica usando modelo fine-tuned."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=self.MAX_LENGTH,
            truncation=True,
            padding=True,
        ).to(self._device)

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]

        probs_np = probs.cpu().numpy()
        predicted_idx = int(np.argmax(probs_np))
        confidence = float(probs_np[predicted_idx])

        all_probs = {
            DOCUMENT_LABELS.get(i, f"class_{i}"): float(p)
            for i, p in enumerate(probs_np)
        }

        return ClassificationResult(
            document_type=DOCUMENT_LABELS.get(predicted_idx, "otro"),
            confidence=confidence,
            all_probabilities=all_probs,
            model_used=self.model_path or self.BASE_MODEL,
        )

    def _classify_heuristic(self, text: str) -> ClassificationResult:
        """Clasificacion heuristica basada en keywords cuando no hay modelo."""
        text_lower = text.lower()
        scores: dict[str, float] = {label: 0.0 for label in DOCUMENT_LABELS.values()}

        # Receta keywords
        receta_keywords = [
            ("rx:", 3.0), ("receta", 2.5), ("medicamento", 2.0),
            ("tableta", 2.0), ("capsula", 2.0), ("cada 8 horas", 2.5),
            ("cada 12 horas", 2.5), ("cada 24 horas", 2.5),
            ("via oral", 1.5), ("por 30 dias", 2.0), ("por 15 dias", 2.0),
            ("dosis", 1.5), ("mg ", 1.0), ("jarabe", 1.5),
        ]
        for keyword, weight in receta_keywords:
            if keyword in text_lower:
                scores["receta"] += weight

        # Laboratorio keywords
        lab_keywords = [
            ("resultado", 2.0), ("laboratorio", 3.0), ("mg/dl", 2.5),
            ("g/dl", 2.5), ("glucosa", 2.0), ("hemoglobina", 2.0),
            ("colesterol", 2.0), ("trigliceridos", 2.0), ("creatinina", 2.0),
            ("biometria", 2.5), ("quimica sanguinea", 3.0), ("urea", 1.5),
            ("rango", 1.5), ("referencia", 1.0), ("muestra", 1.5),
            ("hematica", 2.0), ("eritrocitos", 2.0), ("leucocitos", 2.0),
        ]
        for keyword, weight in lab_keywords:
            if keyword in text_lower:
                scores["laboratorio"] += weight

        # Nota medica keywords
        nota_keywords = [
            ("nota medica", 3.0), ("nota de evolucion", 3.0),
            ("exploracion fisica", 2.5), ("signos vitales", 2.5),
            ("plan:", 2.0), ("subjetivo", 2.0), ("objetivo", 1.5),
            ("interrogatorio", 2.0), ("motivo de consulta", 2.5),
            ("antecedentes", 2.0), ("padecimiento actual", 2.5),
        ]
        for keyword, weight in nota_keywords:
            if keyword in text_lower:
                scores["nota_medica"] += weight

        # Referencia keywords
        ref_keywords = [
            ("referencia", 2.5), ("contrareferencia", 3.0),
            ("motivo de envio", 3.0), ("hospital de referencia", 3.0),
            ("unidad de referencia", 2.5), ("se refiere", 2.0),
            ("segundo nivel", 2.5), ("tercer nivel", 2.5),
            ("tratamiento previo", 2.0),
        ]
        for keyword, weight in ref_keywords:
            if keyword in text_lower:
                scores["referencia"] += weight

        # Consentimiento keywords
        consent_keywords = [
            ("consentimiento", 3.0), ("informado", 2.5),
            ("autorizo", 2.5), ("acepto", 2.0),
            ("riesgos", 1.5), ("procedimiento", 1.5),
            ("firma del paciente", 2.5),
        ]
        for keyword, weight in consent_keywords:
            if keyword in text_lower:
                scores["consentimiento"] += weight

        total = sum(scores.values())
        if total == 0:
            return ClassificationResult(
                document_type="otro",
                confidence=0.5,
                all_probabilities={k: 1.0 / len(scores) for k in scores},
                model_used="heuristic",
            )

        probabilities = {k: v / total for k, v in scores.items()}
        best_label = max(probabilities, key=probabilities.get)  # type: ignore[arg-type]
        confidence = probabilities[best_label]

        return ClassificationResult(
            document_type=best_label,
            confidence=min(confidence, 0.95),
            all_probabilities=probabilities,
            model_used="heuristic",
        )

    @staticmethod
    def fine_tune(
        train_dataset_path: str,
        eval_dataset_path: Optional[str] = None,
        output_dir: str = "./models/document_classifier",
        base_model: str = "PlanTL-GOB-ES/roberta-base-biomedical-clinical-es",
        epochs: int = 5,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        max_length: int = 512,
    ) -> dict[str, Any]:
        """Fine-tunea el modelo con datos de documentos medicos.

        Args:
            train_dataset_path: Ruta al JSON de entrenamiento.
            eval_dataset_path: Ruta al JSON de evaluacion. Si None, split auto.
            output_dir: Directorio de salida del modelo.
            base_model: Modelo base de HuggingFace.
            epochs: Numero de epochs.
            batch_size: Tamano de batch.
            learning_rate: Tasa de aprendizaje.
            max_length: Longitud maxima de secuencia.

        Returns:
            Diccionario con metricas de entrenamiento.
        """
        from datasets import Dataset
        from sklearn.metrics import accuracy_score, f1_score

        logger.info(
            "fine_tuning_classifier",
            base_model=base_model,
            epochs=epochs,
            batch_size=batch_size,
        )

        with open(train_dataset_path, "r", encoding="utf-8") as f:
            train_raw = json.load(f)

        texts = [item["text"] for item in train_raw]
        labels = [LABEL_TO_ID.get(item["label"], 5) for item in train_raw]

        if eval_dataset_path:
            with open(eval_dataset_path, "r", encoding="utf-8") as f:
                eval_raw = json.load(f)
            eval_texts = [item["text"] for item in eval_raw]
            eval_labels = [LABEL_TO_ID.get(item["label"], 5) for item in eval_raw]
        else:
            split_idx = int(len(texts) * 0.8)
            eval_texts = texts[split_idx:]
            eval_labels = labels[split_idx:]
            texts = texts[:split_idx]
            labels = labels[:split_idx]

        try:
            tokenizer = AutoTokenizer.from_pretrained(base_model)
        except Exception:
            base_model = "dccuchile/bert-base-spanish-wwm-cased"
            tokenizer = AutoTokenizer.from_pretrained(base_model)

        def tokenize_function(examples: dict) -> dict:
            return tokenizer(
                examples["text"],
                max_length=max_length,
                truncation=True,
                padding="max_length",
            )

        train_dataset = Dataset.from_dict({"text": texts, "label": labels})
        eval_dataset = Dataset.from_dict({"text": eval_texts, "label": eval_labels})

        train_dataset = train_dataset.map(tokenize_function, batched=True)
        eval_dataset = eval_dataset.map(tokenize_function, batched=True)

        model = AutoModelForSequenceClassification.from_pretrained(
            base_model,
            num_labels=len(DOCUMENT_LABELS),
            id2label=DOCUMENT_LABELS,
            label2id=LABEL_TO_ID,
        )

        def compute_metrics(eval_pred: Any) -> dict[str, float]:
            logits, label_ids = eval_pred
            predictions = np.argmax(logits, axis=-1)
            acc = accuracy_score(label_ids, predictions)
            f1 = f1_score(label_ids, predictions, average="macro", zero_division=0)
            return {"accuracy": acc, "f1": f1}

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            fp16=torch.cuda.is_available(),
            logging_steps=50,
            warmup_ratio=0.1,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=compute_metrics,
        )

        train_result = trainer.train()
        eval_result = trainer.evaluate()

        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)

        return {
            "base_model": base_model,
            "training_samples": len(texts),
            "eval_samples": len(eval_texts),
            "epochs": epochs,
            "train_loss": train_result.training_loss,
            "eval_metrics": eval_result,
            "model_path": output_dir,
        }
