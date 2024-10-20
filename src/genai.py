import google.generativeai as genai

from src.config import settings

genai.configure(api_key=settings.AI_API_KEY)

model = genai.GenerativeModel(
    "gemini-1.5-flash", generation_config={"response_mime_type": "application/json"}
)


def make_request_to_model(content: str):
    prompt = (
        f'Using this JSON schema: response = {{ "contain_bad_words": <bool> }} \n'
        f"Return a response - analysis if content has presence "
        f"of obscene language, insults, etc\n"
        f"content: {content}"
    )

    return model.generate_content(prompt).text
