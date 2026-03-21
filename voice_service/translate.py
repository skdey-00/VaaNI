"""
Translation Module using IndicTrans2
Supports English <-> Indian Language translation
"""
import time
import logging
from typing import Dict, Optional
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from config import settings
from banking_glossary import (
    get_glossary_terms,
    get_domain_forced_tokens,
    inject_glossary_context
)

logger = logging.getLogger(__name__)


class TranslationModel:
    """IndicTrans2 Translation Model Handler"""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = settings.DEVICE

        if not settings.MOCK_MODE:
            self._load_model()

    def _load_model(self):
        """Load the translation model"""
        try:
            logger.info(f"Loading Translation model on {self.device}...")
            start_time = time.time()

            # IndicTrans2 model
            model_name = "ai4bharat/indictrans2-indic-en-dist-200M"

            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to(self.device)

            logger.info(f"Loaded IndicTrans2 model in {time.time() - start_time:.2f}s")

        except Exception as e:
            logger.error(f"Failed to load translation model: {e}")
            self.model = None

    def _normalize_direction(self, src: str, tgt: str) -> tuple:
        """
        Normalize language codes for IndicTrans2
        Returns (src, tgt, direction)
        """
        indic_codes = ["hi", "mr", "ta", "bn", "te", "kn", "ml", "gu", "or", "pa", "as"]

        # English to Indic
        if src == "en" and tgt in indic_codes:
            return "en", tgt, "en-indic"

        # Indic to English
        elif src in indic_codes and tgt == "en":
            return src, "en", "indic-en"

        # Indic to Indic (via English)
        elif src in indic_codes and tgt in indic_codes:
            return src, tgt, "indic-indic"

        else:
            # Default to treating as en-indic
            return "en", tgt, "en-indic"

    def translate(
        self,
        text: str,
        src: str = "en",
        tgt: str = "hi",
        use_banking_glossary: bool = True
    ) -> Dict[str, any]:
        """
        Translate text from source to target language

        Args:
            text: Source text
            src: Source language code
            tgt: Target language code
            use_banking_glossary: Use banking glossary for better accuracy

        Returns:
            Dictionary with translation and metadata
        """
        start_time = time.time()

        if settings.MOCK_MODE:
            return self._mock_translate(text, src, tgt)

        if self.model is None:
            raise RuntimeError("Translation model not loaded")

        try:
            # Inject banking context if enabled
            if use_banking_glossary:
                text = inject_glossary_context(text, src, tgt)

            # Normalize direction
            src_norm, tgt_norm, direction = self._normalize_direction(src, tgt)

            # Prepare inputs
            # IndicTrans2 uses special prefix format
            if direction == "indic-en":
                prefix = ""
                # For indic-en, we might need to use a different model
                model_name = "ai4bharat/indictrans2-indic-en-dist-200M"
            elif direction == "en-indic":
                prefix = ""
                model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
            else:
                # Indic to Indic - handle via English
                # First translate to English, then to target
                mid_result = self.translate(text, src, "en", use_banking_glossary)
                return self.translate(
                    mid_result["translation"],
                    "en",
                    tgt,
                    use_banking_glossary
                )

            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=settings.MAX_TEXT_LENGTH
            )

            if self.device == "cuda":
                inputs = inputs.to(self.device)

            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    max_length=settings.MAX_TEXT_LENGTH,
                    num_beams=5,
                    length_penalty=1.0,
                    early_stopping=True
                )

            # Decode
            with self.tokenizer.as_target_tokenizer():
                translation = self.tokenizer.decode(
                    generated_tokens[0],
                    skip_special_tokens=True
                )

            # Clean up banking domain prefix
            if translation.startswith("[Banking Domain] "):
                translation = translation.replace("[Banking Domain] ", "", 1)

            latency_ms = (time.time() - start_time) * 1000

            logger.info(
                f"Translation completed in {latency_ms:.0f}ms "
                f"(target: <{settings.TRANSLATE_MAX_LATENCY_MS}ms)"
            )

            return {
                "translation": translation.strip(),
                "source_language": src,
                "target_language": tgt,
                "direction": direction,
                "latency_ms": round(latency_ms, 2),
                "model": "indictrans2"
            }

        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise

    def _mock_translate(self, text: str, src: str, tgt: str) -> Dict[str, any]:
        """Generate mock translation for development"""

        # Simple mock translations for demo
        mock_translations = {
            ("en", "hi"): {
                "What is my account balance?": "मेरे खाते का बैलेंस क्या है?",
                "I want to check my balance": "मैं अपना बैलेंस चेक करना चाहता हूं",
                "Transfer money to": "पैसे ट्रांसफर करें",
                "loan": "ऋण",
                "interest rate": "ब्याज दर",
                "default": "[अनुवादित पाठ]",
            },
            ("hi", "en"): {
                "मेरे खाते का बैलेंस क्या है?": "What is my account balance?",
                "मैं अपना बैलेंस चेक करना चाहता हूं": "I want to check my balance",
                "ऋण": "loan",
                "ब्याज दर": "interest rate",
                "default": "[Translated text]",
            },
            ("en", "ta"): {
                "What is my account balance?": "என் கணக்கு இருப்பு என்ன?",
                "I want to check my balance": "எனது இருப்பை சரிபார்க்க விரும்புகிறேன்",
                "default": "[மொழிபெயர்க்கப்பட்ட உரை]",
            }
        }

        key = (src, tgt)
        if key in mock_translations:
            for source, target in mock_translations[key].items():
                if source.lower() in text.lower() or source == "default":
                    translation = target if source != "default" else mock_translations[key]["default"]
                    break
            else:
                translation = mock_translations[key]["default"]
        else:
            translation = f"[Translated from {src} to {tgt}]: {text}"

        return {
            "translation": translation,
            "source_language": src,
            "target_language": tgt,
            "direction": f"{src}-{tgt}",
            "latency_ms": 25.0,
            "model": "mock"
        }


# Global model instance
translation_model = TranslationModel()
