from dotenv import load_dotenv
import os

load_dotenv(override=True)

IS_DEVELOPMENT = os.environ.get("DEVELOPMENT", "false").lower() == "true"

PATH = os.environ.get("PATH")
PATH += f";{os.path.realpath('./driver')}"
os.environ.setdefault("PATH", PATH)

CHARTS_DIR = os.path.realpath("./output/charts")
TITLE = os.environ.get("TITLE", "Reporte")
CLIENT = os.environ.get("CLIENT", "Cliente")

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]

DEFAULT_SIGNATURE = {
    "title": "Monthly Report",
    "author": "Netready Solutions",
    "subject": "Netready Solutions - LogRhythm",
    "keywords": ["LogRhythm", "Netready Solutions", "Report", "Confidential"],
    # Static
    "producer": "LogRhythm Report Tool - github.com/Undead34",
    "creator": "LogRhythm Report Tool - @Undead34"
}
