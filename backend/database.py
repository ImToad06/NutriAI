import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ruta de la base de datos SQLite local
DATABASE_URL = "sqlite:///./nutripae.db"

# Creación del engine de SQLAlchemy
# check_same_thread=False es necesario solo para SQLite en aplicaciones multihilo como FastAPI
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creación de la fábrica de sesiones locales
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para definir los modelos ORM
Base = declarative_base()

def get_db():
    """
    Generador que inicializa una sesión de base de datos para cada petición,
    asegurando que se cierre correctamente una vez completada la operación.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
