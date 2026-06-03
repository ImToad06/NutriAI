from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    documento = Column(String(50), nullable=True, index=True)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(10), nullable=False)
    grado = Column(String(20), nullable=False)
    colegio = Column(String(150), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    evaluations = relationship(
        "Evaluation",
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="Evaluation.created_at",
    )

    __table_args__ = (
        Index("ix_students_colegio_grado", "colegio", "grado"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(150), nullable=False)
    rol = Column(String(30), nullable=False, default="nutricionista")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edad_meses = Column(Float, nullable=False)
    peso_kg = Column(Float, nullable=False)
    estatura_cm = Column(Float, nullable=False)
    muac_cm = Column(Float, nullable=False)
    imc = Column(Float, nullable=False)
    zscore_imc = Column(Float, nullable=True)
    prediccion = Column(String(50), nullable=False)
    alerta = Column(String(20), nullable=False, index=True)
    accion = Column(String(255), nullable=True)
    evaluador_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    student = relationship("Student", back_populates="evaluations")
    evaluador = relationship("User", foreign_keys=[evaluador_id])
    notes_history = relationship(
        "EvaluationNote",
        back_populates="evaluation",
        cascade="all, delete-orphan",
        order_by="EvaluationNote.created_at",
    )


class EvaluationNote(Base):
    __tablename__ = "evaluation_notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    evaluation_id = Column(
        Integer,
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    autor_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    nota = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    evaluation = relationship("Evaluation", back_populates="notes_history")
    autor = relationship("User", foreign_keys=[autor_id])
