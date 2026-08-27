import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
HANDOFF_MODEL = os.getenv("GROQ_HANDOFF_MODEL", MODEL_NAME)

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing from the environment")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

__all__ = ["client","MODEL_NAME","HANDOFF_MODEL"]
