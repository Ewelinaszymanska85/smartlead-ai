import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_lead_summary(message: str) -> str:
    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": (
                    "Jesteś asystentem sprzedażowym. "
                    "Przeanalizuj wiadomość potencjalnego klienta "
                    "i przygotuj krótkie, konkretne podsumowanie dla handlowca."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
    )

    return response.output_text