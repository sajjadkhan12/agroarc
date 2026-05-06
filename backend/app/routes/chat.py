"""
General Chat API Routes
Gemini-powered conversational endpoint for AgroArc Command Tester.
"""

from fastapi import APIRouter
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

from ..core.schemas import GeneralChatRequest, GeneralChatResponse

logger = logging.getLogger(__name__)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
SYSTEM_PROMPT = (
    "You are AgroArc AI, an intelligent agricultural assistant helping farmers. "
    "Give practical, accurate, and simple advice about crops, fertilizers, soil, and weather."
)
FALLBACK_REPLY = (
    "I am temporarily unable to reach the AI model. "
    "Please try again in a moment. For now, check soil moisture, crop stage, and local weather before irrigation or fertilizer use."
)

router = APIRouter(tags=["General Chat"])


@router.post(
    "/chat",
    response_model=GeneralChatResponse,
    summary="General Gemini chat",
    description="Get general conversational response for Command Tester."
)
async def general_chat(request: GeneralChatRequest) -> GeneralChatResponse:
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY missing; returning fallback reply.")
        return GeneralChatResponse(reply=FALLBACK_REPLY)

    user_message = request.message.strip()
    if not user_message:
        return GeneralChatResponse(reply="Please provide a message.")

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = f"{SYSTEM_PROMPT}\nUser: {user_message}\nAssistant:"
        response = model.generate_content(prompt)

        reply = getattr(response, "text", "") or ""
        reply = reply.strip()
        if not reply:
            return GeneralChatResponse(reply=FALLBACK_REPLY)

        return GeneralChatResponse(reply=reply)
    except Exception as e:
        logger.error(f"Gemini chat failed: {str(e)}", exc_info=True)
        return GeneralChatResponse(reply=FALLBACK_REPLY)
