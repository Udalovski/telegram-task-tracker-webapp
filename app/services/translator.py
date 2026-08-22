import re
import asyncio
import logging
import httpx
from deep_translator import GoogleTranslator
from app.config import settings

logger = logging.getLogger(__name__)


TRANSLATION_CACHE: dict[str, str] = {}


GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-pro"
]
WORKING_GEMINI_MODEL: str | None = None
MODELS_CHECKED: bool = False


VERB_REPLACEMENTS = {

    r"\bumyłam\b": "umyto",
    r"\bumyłem\b": "umyto",
    r"\bumyć\b": "umyto",

    r"\bzrobiłam\b": "zrobiono",
    r"\bzrobiłem\b": "zrobiono",
    r"\bzrobić\b": "wykonano",

    r"\bwykonałam\b": "wykonano",
    r"\bwykonałem\b": "wykonano",
    r"\bwykonać\b": "wykonano",

    r"\bprzeprowadziłam\b": "przeprowadzono",
    r"\bprzeprowadziłem\b": "przeprowadzono",
    r"\bprzeprowadzić\b": "przeprowadzono",

    r"\bsprawdziłam\b": "sprawdzono",
    r"\bsprawdziłem\b": "sprawdzono",
    r"\bsprawdzić\b": "sprawdzono",
    r"\bzweryfikowałam\b": "zweryfikowano",
    r"\bzweryfikowałem\b": "zweryfikowano",

    r"\bprzygotowałam\b": "przygotowano",
    r"\bprzygotowałem\b": "przygotowano",
    r"\bprzygotować\b": "przygotowano",

    r"\bnapisałam\b": "napisano",
    r"\bnapisałem\b": "napisano",
    r"\bsporządziłam\b": "sporządzono",
    r"\bsporządenłem\b": "sporządzono",

    r"\bwysłałam\b": "wysłano",
    r"\bwysłałem\b": "wysłano",

    r"\bodpowiedziałam\b": "odpowiedziano",
    r"\bodpowiedziałem\b": "odpowiedziano",

    r"\buporządkowałam\b": "uporządkowano",
    r"\buporządkowałem\b": "uporządkowano",
    r"\bposprzątałam\b": "posprzątano",
    r"\bposprząenłem\b": "posprzątano",

    r"\bzorganizowałam\b": "zorganizowano",
    r"\bzorganizowałem\b": "zorganizowano",

    r"\bzaktualizowałam\b": "zaktualizowano",
    r"\bzaktualizowałem\b": "zaktualizowano",

    r"\bwprowadziłam\b": "wprowadzono",
    r"\bwprowadziłem\b": "wprowadzono",

    r"\bdodałam\b": "dodano",
    r"\bdodałem\b": "dodano",

    r"\busunęłam\b": "usunięto",
    r"\busunąłem\b": "usunięto",

    r"\bprzeczytałam\b": "przeczytano",
    r"\bprzeczytałem\b": "przeczytano",
    r"\bprzejrzałam\b": "przejrzano",
    r"\bprzejrzałem\b": "przejrzano",
}


def post_process_polish_text(text: str) -> str:
    """Format and polish the translation to sound professional and impersonal."""
    if not text:
        return ""

    cleaned = text.strip()


    cleaned = re.sub(r"^[\-\•\*\d\.\)\s\"']+", "", cleaned).strip()
    cleaned = re.sub(r"[\"']+$", "", cleaned).strip()


    for pattern, replacement in VERB_REPLACEMENTS.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)


    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]


    if cleaned.endswith("."):
        cleaned = cleaned[:-1]

    return cleaned


async def discover_working_gemini_model(gemini_key: str, client: httpx.AsyncClient) -> str:
    """Dynamically query Google API for available models."""
    global WORKING_GEMINI_MODEL, MODELS_CHECKED
    if WORKING_GEMINI_MODEL:
        return WORKING_GEMINI_MODEL

    if not MODELS_CHECKED:
        MODELS_CHECKED = True
        try:
            res = await client.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                headers={"x-goog-api-key": gemini_key},
                timeout=5.0
            )
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name", "").replace("models/", "") for m in data.get("models", [])]
                logger.info(f"Available Gemini models for current key: {models}")
                for preferred in GEMINI_MODELS:
                    if preferred in models:
                        WORKING_GEMINI_MODEL = preferred
                        return preferred
                if models:
                    WORKING_GEMINI_MODEL = models[0]
                    return models[0]
            else:
                logger.warning(f"Google Models list returned {res.status_code}: {res.text}")
        except Exception as e:
            logger.warning(f"Error fetching Google models: {e}")

    return "gemini-1.5-flash"


async def translate_with_ai(text: str) -> str | None:
    """Translate and format task using OpenAI or Gemini if API key is provided."""
    global WORKING_GEMINI_MODEL

    openai_key = settings.effective_openai_api_key
    if openai_key:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a professional Polish translator and work report formatter. "
                                    "Translate the user's short informal work log note into a clean, concise, "
                                    "professional Polish daily work report bullet item. "
                                    "Use impersonal past tense (e.g., 'Umyto okna', 'Przeprowadzono inwentaryzację książek', 'Przygotowano raport') "
                                    "or concise noun phrases. Output ONLY the translated bullet text with no quotes, markdown bullets, or explanations."
                                )
                            },
                            {"role": "user", "content": text}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 100
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    res = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"OpenAI translated: '{text}' -> '{res}'")
                    return post_process_polish_text(res)
                else:
                    logger.warning(f"OpenAI returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"OpenAI translation failed, falling back: {e}")

    gemini_key = settings.effective_gemini_api_key
    if gemini_key:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:

                model_to_use = await discover_working_gemini_model(gemini_key, client)


                prompt = (
                    "You are a professional Polish business translator for daily work reports. "
                    "Translate the following informal work task note into a clean, professional Polish daily work report entry. "
                    "Use impersonal past form (e.g., 'Umyto okna', 'Przeprowadzono inwentaryzację', 'Sporządzono raport', 'Wysłano dokumenty'). "
                    f"Input task: \"{text}\"\n"
                    "Output ONLY the translated line in Polish, without markdown formatting, bullets, or explanations."
                )


                candidates_to_try = [model_to_use] + [m for m in GEMINI_MODELS if m != model_to_use]
                for model in candidates_to_try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                    headers = {
                        "Content-Type": "application/json",
                        "x-goog-api-key": gemini_key
                    }
                    response = await client.post(
                        url,
                        headers=headers,
                        json={
                            "contents": [{
                                "parts": [{"text": prompt}]
                            }],
                            "generationConfig": {
                                "temperature": 0.2,
                                "maxOutputTokens": 80
                            }
                        }
                    )

                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                res = parts[0]["text"].strip()
                                WORKING_GEMINI_MODEL = model
                                logger.info(f"✨ Gemini ({model}) translated: '{text}' -> '{res}'")
                                return post_process_polish_text(res)
                    else:
                        logger.warning(f"Gemini API ({model}) returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Gemini translation failed: {e}")

    return None


async def translate_to_polish(text: str) -> str:
    """Translate raw task note to polished work-report Polish with in-memory caching."""
    if not text or not text.strip():
        return ""

    cleaned_input = text.strip()


    if cleaned_input in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[cleaned_input]


    ai_result = await translate_with_ai(cleaned_input)
    if ai_result:
        TRANSLATION_CACHE[cleaned_input] = ai_result
        return ai_result


    try:
        def _sync_translate():
            translator = GoogleTranslator(source='auto', target='pl')
            return translator.translate(cleaned_input)

        raw_translated = await asyncio.to_thread(_sync_translate)
        final_result = post_process_polish_text(raw_translated)
        TRANSLATION_CACHE[cleaned_input] = final_result
        return final_result
    except Exception as e:
        logger.error(f"Error in deep_translator: {e}")
        final_result = post_process_polish_text(cleaned_input)
        TRANSLATION_CACHE[cleaned_input] = final_result
        return final_result


def format_daily_report_message(date_str: str, tasks: list[dict], user_name: str = "") -> str:
    """Format full Polish report message for Telegram chat."""
    if not tasks:
        return f"📋 *Raport dzienny ({date_str})*\n\n_Brak zarejestrowanych zadań na dzisiaj._"

    lines = [f"📋 *Raport dzienny ({date_str})*"]
    if user_name:
        lines[0] += f" — _{user_name}_"
    lines.append("")

    for idx, t in enumerate(tasks, 1):
        polish_task = t.get("polish_text") or t.get("raw_text")
        lines.append(f"• {polish_task}")

    lines.append("")
    lines.append(f"✅ *Łącznie zadań:* {len(tasks)}")
    return "\n".join(lines)
