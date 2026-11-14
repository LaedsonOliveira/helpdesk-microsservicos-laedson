import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SEGREDO"] = "segredo-de-teste-com-mais-de-trinta-e-dois-caracteres"
os.environ["ADMIN_EMAIL"] = "admin@empresa.com"
os.environ["ADMIN_PASSWORD"] = "Helpdesk2026"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
