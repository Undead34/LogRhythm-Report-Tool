from dotenv import load_dotenv
import os

load_dotenv()

IS_DEVELOPMENT = os.environ.get("DEVELOPMENT", "false").lower() == "true"

PATH = os.environ.get("PATH")
PATH += f";{os.path.realpath('./driver')}"
os.environ.setdefault("PATH", PATH)

CHARTS_DIR = os.path.realpath("./output/charts")
FONTS = [
    ["OpenSans-Regular", "./assets/fonts/OpenSans-Regular.ttf"],
    ["OpenSans-Bold", "./assets/fonts/OpenSans-Bold.ttf"],
    ["Conthrax", "./assets/fonts/Conthrax.ttf"],

    # Arial Narrow Font
    ["Arial-Narrow", "./assets/fonts/Arial Narrow.ttf"],
    ["Arial-Narrow-Italic", "./assets/fonts/Arial Narrow Italic.ttf"],
    ["Arial-Narrow-Bold", "./assets/fonts/Arial Narrow Bold.ttf"],
    ["Arial-Narrow-Bold-Italic", "./assets/fonts/Arial Narrow Bold Italic.ttf"]
]

TITLE = os.environ.get("TITLE", "Reporte")
CLIENT = os.environ.get("CLIENT", "Cliente")

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
