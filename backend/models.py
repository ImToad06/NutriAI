from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Estudiante(Base):
    """
    Representa a un estudiante dentro del sistema NutriPAE IA.
    Guarda información básica y demográfica del alumno.
    """
    __tablename__ = "estudiantes"

    id_estudiante = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(10), nullable=False)
    grado = Column(String(20), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)

    # Relación bidireccional de 1 a N con Evaluacion
    # Si se elimina un estudiante, se eliminan todas sus evaluaciones en cascada
    evaluaciones = relationship("Evaluacion", back_populates="estudiante", cascade="all, delete-orphan")


class Evaluacion(Base):
    """
    Representa una evaluación clínica y nutricional realizada a un estudiante.
    Contiene mediciones biométricas, IMC y el resultado de la clasificación.
    """
    __tablename__ = "evaluaciones"

    id_evaluacion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"), nullable=False)
    fecha_evaluacion = Column(DateTime, server_default=func.now(), nullable=False)
    peso = Column(Float, nullable=False)
    altura = Column(Float, nullable=False)
    imc = Column(Float, nullable=False)
    clasificacion = Column(String(50), nullable=False)
    observaciones = Column(Text, nullable=True)

    # Relación inversa apuntando al Estudiante
    estudiante = relationship("Estudiante", back_populates="evaluaciones")
