import httpx
import asyncio
from typing import Optional, Dict, Any
from utils import prompt_builder
from utils.prompt_builder import build_prompt_payload

prompt_payload = build_prompt_payload()
prompt = prompt_payload.get("content")
# Constants
BASE_IMAGE_URL = "https://image.pollinations.ai"
BASE_TEXT_URL = "https://text.pollinations.ai"
DEFAULT_VOICE = "nova"
FALLBACK_VOICE = "echo"

# Retry settings
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 1.5


async def fetch_with_retries(url: str, client: httpx.AsyncClient) -> Optional[httpx.Response]:
    for attempt in range(MAX_RETRIES):
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return response
            print(f"⚠️ Attempt {attempt + 1} failed ({response.status_code}), retrying...")
        except httpx.RequestError as e:
            print(f"🚨 Request error on attempt {attempt + 1}: {e}")
        await asyncio.sleep(RETRY_BACKOFF_SECONDS)
    print("❌ All retries failed.")
    return None


async def generate_image(prompt: str) -> Optional[str]:
    url = f"{BASE_IMAGE_URL}/prompt/{prompt}"
    async with httpx.AsyncClient() as client:
        response = await fetch_with_retries(url, client)
        return url if response else None


async def list_image_models() -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_IMAGE_URL}/models")
            return response.json()
        except Exception as e:
            print(f"Error fetching image models: {e}")
            return None


async def generate_text(prompt: str) -> Optional[str]:
    url = f"{BASE_TEXT_URL}/{prompt}"
    async with httpx.AsyncClient() as client:
        response = await fetch_with_retries(url, client)
        return response.text if response else None


async def generate_text_advanced(payload: dict) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(BASE_TEXT_URL, json=payload)
            return response.json()
        except Exception as e:
            print(f"Advanced text generation failed: {e}")
            return None


async def generate_audio(prompt: str, voice: str = DEFAULT_VOICE) -> Optional[str]:
    url = f"{BASE_TEXT_URL}/{prompt}?model=openai-audio&voice={voice}"
    async with httpx.AsyncClient() as client:
        response = await fetch_with_retries(url, client)
        if response:
            return url
        # Try fallback voice
        print(f"⚠️ Trying fallback voice: {FALLBACK_VOICE}")
        fallback_url = f"{BASE_TEXT_URL}/{prompt}?model=openai-audio&voice={FALLBACK_VOICE}"
        response = await fetch_with_retries(fallback_url, client)
        return fallback_url if response else None


async def list_text_models() -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_TEXT_URL}/models")
            return response.json()
        except Exception as e:
            print(f"Error fetching text models: {e}")
            return None


async def fetch_image_feed() -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_IMAGE_URL}/feed")
            return response.json()
        except Exception as e:
            print(f"Error fetching image feed: {e}")
            return None


async def fetch_text_feed() -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_TEXT_URL}/feed")
            return response.json()
        except Exception as e:
            print(f"Error fetching text feed: {e}")
            return None
