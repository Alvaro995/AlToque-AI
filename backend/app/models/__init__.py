"""Modelos ORM de SQLAlchemy consolidados para la aplicación y migraciones."""

from app.models.user import User, PatientProfile, UserPairing
from app.models.ingestion import UploadedDocument, ClinicalRecord, ClinicalParameter, ScheduleBlock
from app.models.scheduling import MetabolicWindow, SleepTarget
from app.models.glycemic import FoodLog, FoodItem, BufferEvaluation, GlucoseSimulation
from app.models.physical import ExerciseTrigger, StrengthPlan, ExerciseLog
from app.models.care_network import NudgeEvent
from app.models.assistant import ChatSession, ChatMessage
from app.models.reporting import MedicalReport
from app.models.risk import RiskAssessment

__all__ = [
    "User", "PatientProfile", "UserPairing",
    "UploadedDocument", "ClinicalRecord", "ClinicalParameter", "ScheduleBlock",
    "MetabolicWindow", "SleepTarget",
    "FoodLog", "FoodItem", "BufferEvaluation", "GlucoseSimulation",
    "ExerciseTrigger", "StrengthPlan", "ExerciseLog",
    "NudgeEvent",
    "ChatSession", "ChatMessage",
    "MedicalReport",
    "RiskAssessment",
]
