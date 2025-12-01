import os
import sys
import wave
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from manimlib import log

from manim_voiceover.helper import (
    create_dotenv_file,
    remove_bookmarks,
)
from manim_voiceover.services.base import SpeechService

try:
    from google import genai
    from google.genai import types
except ImportError:
    log.error(
        "Missing packages. " "Run `pip install google-genai` to use GeminiTTSService."
    )

load_dotenv(find_dotenv(usecwd=True))


def create_dotenv_gemini():
    log.info("You need a Gemini API key from https://makersuite.google.com/app/apikey")
    if not create_dotenv_file(["GOOGLE_API_KEY"]):
        raise ValueError(
            "The environment variable GOOGLE_API_KEY is not set. "
            "Please add it to your .env file."
        )
    log.info("The .env file has been created. Please restart Manim.")
    sys.exit()


class GeminiTTSService(SpeechService):
    """
    Gemini-based TTS service using Google's Gemini 2.5 SDK.
    """

    def __init__(
        self,
        model: str = "gemini-2.5-flash-preview-tts",
        voice_name: str = "Kore",
        transcription_model: str = "base",
        **kwargs,
    ):
        self.model = model
        self.voice_name = voice_name

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            create_dotenv_gemini()

        self.client = genai.Client(api_key=api_key)

        super().__init__(transcription_model=transcription_model, **kwargs)

    def generate_from_text(
        self, text: str, cache_dir: str = None, path: str = None, **kwargs
    ) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir

        clean_text = remove_bookmarks(text)

        input_data = {
            "input_text": clean_text,
            "service": "gemini",
            "config": {
                "model": self.model,
                "voice": self.voice_name,
            },
        }

        cached = self.get_cached_result(input_data, cache_dir)
        if cached:
            return cached

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=clean_text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=self.voice_name,
                            )
                        )
                    ),
                ),
            )
        except Exception as e:
            log.error(f"Gemini TTS generation failed: {e}")
            raise

        audio_data = response.candidates[0].content.parts[0].inline_data.data

        audio_path = path or self.get_audio_basename(input_data) + ".wav"
        full_path = Path(cache_dir) / audio_path

        # Save audio
        with wave.open(str(full_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)

        return {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }
