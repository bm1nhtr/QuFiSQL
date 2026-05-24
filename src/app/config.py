import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "quant_finance"),
    "charset": "utf8mb4",
}

VALID_RISK_PROFILES = ("prudent", "équilibré", "dynamique", "agressif")

RISK_PROFILE_DESCRIPTIONS = {
    "prudent": "Low risk — focus on capital preservation",
    "équilibré": "Balanced mix of growth and stability",
    "dynamique": "Growth-oriented with moderate risk",
    "agressif": "High risk / high return (requires AUM >= 100,000)",
}

ALLOWED_CLIENT_COLUMNS = frozenset(
    {"nom", "prenom", "email", "aum", "profil_risque", "date_entree", "id_gestionnaire"}
)
