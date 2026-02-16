"""
Repositorios de acceso a datos.
"""

from app.db.repositories.alert_repo import AlertRepository
from app.db.repositories.document_repo import DocumentRepository
from app.db.repositories.patient_repo import PatientRepository

__all__ = [
    "AlertRepository",
    "DocumentRepository",
    "PatientRepository",
]
