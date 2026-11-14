"""Conexão com o banco de dados exclusivo do microserviço de Usuários."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import DATABASE_URL

opcoes_engine = {}
if DATABASE_URL.startswith("sqlite"):
    opcoes_engine["connect_args"] = {"check_same_thread": False}
    if DATABASE_URL in {"sqlite://", "sqlite:///:memory:"}:
        opcoes_engine["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **opcoes_engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Abre uma sessão por requisição e fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def inicializar_banco() -> None:
    from app import model  # Registra as tabelas no metadata antes de criá-las.

    Base.metadata.create_all(bind=engine)
