from dotenv import load_dotenv
import os

load_dotenv()

IS_DEVELOPMENT = os.environ.get("DEVELOPMENT", "false").lower() == "true"
CHARTS_DIR = os.path.realpath("./output/charts")
FONTS = [
    ["OpenSans-Regular", "./assets/fonts/OpenSans-Regular.ttf"],
    ["OpenSans-Bold", "./assets/fonts/OpenSans-Bold.ttf"],
    ["Arial-Narrow", "./assets/fonts/Arial Narrow.ttf"],
    ["Conthrax", "./assets/fonts/Conthrax.ttf"],
]
