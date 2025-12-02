import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------
# DEMO MODE FLAG
# ----------------------------------------------------
DEMO_MODE  = False


# ----------------------------------------------------
# GROQ / LLM CONFIG
# ----------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = 0.2

# ----------------------------------------------------
# PATHS
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Firebase credential (required only for real mode)
FIREBASE_CRED_PATH = os.path.join(BASE_DIR, "config", "shonali-desh-19ead-firebase-adminsdk-fbsvc-befee90074.json")

# Flood model path
FLOOD_MODEL_PATH = os.path.join(BASE_DIR, "models", "flood_model.pkl")

# ----------------------------------------------------
# Carbon factors
# ----------------------------------------------------
CARBON_FACTORS = {
    "urea_kg": 5.5,
    "electric_pumping_hour": 2.0,
    "diesel_pumping_hour": 10.0,
}
