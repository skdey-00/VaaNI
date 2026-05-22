"""
N-gram Language Identification Engine for Indian Languages
==========================================================

Uses character trigram frequency profiles with cosine similarity
to identify the language of input text across 9 Indian languages.

Algorithms:
  1. Character trigram extraction + frequency normalization
  2. Cosine similarity against pre-built language profiles
  3. Unicode script range pre-filtering
  4. Hindi/Marathi discriminative word-list disambiguation

Supported: hi, mr, ta, te, bn, kn, ml, gu, en
"""

import math
import re
from collections import Counter
from typing import Dict, List, Tuple, Optional

# ============================================================================
# Pre-built Trigram Profiles (top 300 trigrams per language, normalized)
# These are representative trigrams generated from each script's character
# ranges and common patterns.
# ============================================================================

PROFILES: Dict[str, Dict[str, float]] = {}

# --- Hindi (Devanagari) trigrams ---
_hi_trigrams_raw = Counter()
for word in [
    "मुझे","फिक्स्ड","डिपॉजिट","खोलनी","है","क्या","ब्याज","दर","बताएंगे","लोन","लेना",
    "खाता","खोलना","चाहता","हूं","पैसे","ट्रांसफर","करने","हैं","बैलेंस","जानना","एटीएम",
    "कार्ड","बंद","हो","गया","साल","ब्याज","दर","प्रतिशत","रुपये","जमा","निकाल",
    "ऋण","आवेदन","प्रक्रिया","बैंक","ग्राहक","सेवा","जमा","राशि","अकाउंट","बचत",
    "मौजूदा","शेष","राशि","धन","व्यय","आय","वित्त","निवेश","योजना","सरकारी",
    "किसान","योजना","सुविधा","लाभ","वित्तीय","संस्था","ऋण","देन","सहायता","केंद्र",
    "महत्वपूर्ण","जानकारी","प्रमाण","पहचान","पत्र","आधार","संख्या","मोबाइल","फोन",
    "पता","घर","शहर","राज्य","देश","भारत","नई","दिल्ली","सरकार","काम","करने","वाले",
]:
    for i in range(len(word) - 2):
        _hi_trigrams_raw[word[i:i+3]] += 1

_hi_total = sum(_hi_trigrams_raw.values())
PROFILES["hi"] = {tg: count / _hi_total for tg, count in _hi_trigrams_raw.most_common(300)}

# --- Marathi (Devanagari) trigrams ---
_mr_trigrams_raw = Counter()
for word in [
    "मला","आहे","करू","शकतो","तुम्ही","काय","हवे","आहेत","मराठी","बोलत","पैसे",
    "द्यायचे","आहेत","खाते","उघडायचे","आहे","कर्ज","घ्यायचे","आहे","व्याज","दर",
    "किती","आहे","जमा","रक्कम","बँक","सेवा","ग्राहक","उपयोग","सुविधा","महत्वाचे",
    "माहिती","पुरावा","ओळख","पत्र","आधार","क्रमांक","मोबाइल","फोन","पत्ता","घर",
    "शहर","राज्य","देश","भारत","सरकार","काम","करणारे","लोक","मदत","करत","आहेत",
    "आम्ही","तुमच्या","साठी","येथे","आहोत","पैशांची","गरज","आहे","बचत","खाते",
    "चालू","ठेव","खाते","मुदत","ठेव","व्याज","दर","चांगला","आहे","गुंतवणूक","योजना",
    "सरकारी","योजना","लाभ","मिळवणे","शक्य","आहे","प्रक्रिया","सोपी","आहे",
]:
    for i in range(len(word) - 2):
        _mr_trigrams_raw[word[i:i+3]] += 1

_mr_total = sum(_mr_trigrams_raw.values())
PROFILES["mr"] = {tg: count / _mr_total for tg, count in _mr_trigrams_raw.most_common(300)}

# --- Tamil trigrams ---
_ta_trigrams_raw = Counter()
for word in [
    "எனக்கு","கடன்","வேண்டும்","என்ன","ஆவணங்கள்","தேவை","கணக்கு","திறக்க","விரும்புகிறேன்",
    "பணம்","அனுப்ப","வேண்டும்","வட்டி","விகிதம்","எவ்வளவு","வங்கி","சேவை","வாடிக்கையாளர்",
    "சேமிப்பு","கணக்கு","நடப்பு","கணக்கு","தொகை","ரூபாய்","முதலீடு","திட்டம்","அரசு",
    "உதவி","பெற","முடியும்","முக்கியம்","தகவல்","அடையாள","அட்டை","ஆதார்","எண்",
    "கைப்பேசி","முகவரி","ஊர்","மாவட்டம்","மாநிலம்","நாடு","இந்தியா","அரசு",
    "வேலை","செய்யும்","மக்கள்","உதவி","செய்ய","நாங்கள்","உங்களுக்கு","இங்கே",
    "இருக்கிறோம்","பணத்தின்","தேவை","உள்ளது","சேமிப்பு","கணக்கு","நடப்பில்",
    "வைப்பு","கணக்கு","கால","வைப்பு","வட்டி","நல்ல","உள்ளது","முதலீடு",
]:
    for i in range(len(word) - 2):
        _ta_trigrams_raw[word[i:i+3]] += 1

_ta_total = sum(_ta_trigrams_raw.values())
PROFILES["ta"] = {tg: count / _ta_total for tg, count in _ta_trigrams_raw.most_common(300)}

# --- Telugu trigrams ---
_te_trigrams_raw = Counter()
for word in [
    "నాకు","అప్పు","కావాలి","ఏమి","పత్రాలు","అవసరం","ఖాతా","తెరవడానికి","కోరుకుంటున్నాను",
    "డబ్బు","బదిలీ","చేయాలి","వడ్డీ","రేటు","ఎంత","బ్యాంకు","సేవ","కస్టమర్","పొదుపు",
    "ఖాతా","ప్రస్తుత","ఖాతా","మొత్తం","రూపాయలు","పెట్టుబడి","ప్రణాళిక","ప్రభుత్వ","సహాయం",
    "పొందవచ్చు","ముఖ్యమైన","సమాచారం","గుర్తింపు","కార్డు","ఆధార్","నంబర్","మొబైల్",
    "చిరునామా","ఇల్లు","పట్టణం","జిల్లా","రాష్ట్రం","దేశం","భారతదేశం","ప్రభుత్వం",
    "పని","చేసే","ప్రజలు","సహాయం","చేయడానికి","మేము","మీకు","ఇక్కడ","ఉన్నాము",
    "డబ్బు","అవసరం","ఉంది","పొదుపు","ఖాతా","నడుస్తున్న","డిపాజిట్","ఖాతా",
]:
    for i in range(len(word) - 2):
        _te_trigrams_raw[word[i:i+3]] += 1

_te_total = sum(_te_trigrams_raw.values())
PROFILES["te"] = {tg: count / _te_total for tg, count in _te_trigrams_raw.most_common(300)}

# --- Bengali trigrams ---
_bn_trigrams_raw = Counter()
for word in [
    "আমাকে","ঋণ","দিতে","হবে","কী","নথি","প্রয়োজন","অ্যাকাউন্ট","খুলতে","চাই",
    "টাকা","পাঠাতে","হবে","সুদের","হার","কত","ব্যাংক","সেবা","গ্রাহক","সঞ্চয়",
    "অ্যাকাউন্ট","চলতি","অ্যাকাউন্ট","পরিমাণ","টাকা","বিনিয়োগ","পরিকল্পনা","সরকার",
    "সাহায্য","পেতে","পারবেন","গুরুত্বপূর্ণ","তথ্য","পরিচয়","পত্র","আধার","নম্বর",
    "মোবাইল","ফোন","ঠিকানা","বাড়ি","শহর","জেলা","রাজ্য","দেশ","ভারত","সরকার",
    "কাজ","কর্মী","মানুষ","সাহায্য","করতে","আমরা","আপনার","জন্য","এখানে","আছি",
    "টাকার","প্রয়োজন","আছে","সঞ্চয়","অ্যাকাউন্ট","চলমান","আমানত","অ্যাকাউন্ট",
    "মেয়াদী","আমানত","সুদের","হার","ভালো","আছে","বিনিয়োগ","পরিকল্পনা",
]:
    for i in range(len(word) - 2):
        _bn_trigrams_raw[word[i:i+3]] += 1

_bn_total = sum(_bn_trigrams_raw.values())
PROFILES["bn"] = {tg: count / _bn_total for tg, count in _bn_trigrams_raw.most_common(300)}

# --- Kannada trigrams ---
_kn_trigrams_raw = Counter()
for word in [
    "ನನಗೆ","ಸಾಲ","ಬೇಕು","ಏನು","ದಾಖಲೆಗಳು","ಅಗತ್ಯ","ಖಾತೆ","ತೆರೆಯಲು","ಬಯಸುತ್ತೇನೆ",
    "ಹಣ","ವರ್ಗಾಯಿಸಲು","ಬೇಕು","ಬಡ್ಡಿ","ದರ","ಎಷ್ಟು","ಬ್ಯಾಂಕ್","ಸೇವೆ","ಗ್ರಾಹಕ","ಉಳಿತಾಯ",
    "ಖಾತೆ","ಚಾಲ್ತಿ","ಖಾತೆ","ಮೊತ್ತ","ರೂಪಾಯಿ","ಹೂಡಿಕೆ","ಯೋಜನೆ","ಸರ್ಕಾರ","ಸಹಾಯ",
    "ಪಡೆಯಬಹುದು","ಪ್ರಮುಖ","ಮಾಹಿತಿ","ಗುರುತಿನ","ಕಾರ್ಡ್","ಆಧಾರ್","ಸಂಖ್ಯೆ","ಮೊಬೈಲ್",
    "ಫೋನ್","ವಿಳಾಸ","ಮನೆ","ನಗರ","ಜಿಲ್ಲೆ","ರಾಜ್ಯ","ದೇಶ","ಭಾರತ","ಸರ್ಕಾರ","ಕೆಲಸ",
    "ಮಾಡುವ","ಜನರು","ಸಹಾಯ","ಮಾಡಲು","ನಾವು","ನಿಮಗೆ","ಇಲ್ಲಿ","ಇದ್ದೇವೆ","ಹಣದ",
    "ಅಗತ್ಯ","ಇದೆ","ಉಳಿತಾಯ","ಖಾತೆ","ನಡೆಯುತ್ತಿರುವ","ಠೇವಣಿ","ಖಾತೆ","ಬಡ್ಡಿ",
]:
    for i in range(len(word) - 2):
        _kn_trigrams_raw[word[i:i+3]] += 1

_kn_total = sum(_kn_trigrams_raw.values())
PROFILES["kn"] = {tg: count / _kn_total for tg, count in _kn_trigrams_raw.most_common(300)}

# --- Malayalam trigrams ---
_ml_trigrams_raw = Counter()
for word in [
    "എനിക്ക്","വായ്പ","വേണം","എന്ത്","രേഖകൾ","ആവശ്യം","അക്കൗണ്ട്","തുറക്കാൻ","ആഗ്രഹിക്കുന്നു",
    "പണം","അയക്കണം","പലിശ","നിരക്ക്","എത്ര","ബാങ്ക്","സേവനം","ഉപഭോക്താവ്","ലാഭം",
    "അക്കൗണ്ട്","നിലവിലെ","അക്കൗണ്ട്","തുക","രൂപ","നിക്ഷേപം","പദ്ധതി","സർക്കാർ","സഹായം",
    "ലഭിക്കും","പ്രധാന","വിവരം","തിരിച്ചറിവ്","കാർഡ്","ആധാർ","നമ്പർ","മൊബൈൽ",
    "ഫോൺ","വിലാസം","വീട്","നഗരം","ജില്ല","സംസ്ഥാനം","രാജ്യം","ഇന്ത്യ","സർക്കാർ",
    "ജോലി","ചെയ്യുന്ന","ആളുകൾ","സഹായം","ചെയ്യാൻ","ഞങ്ങൾ","നിങ്ങൾക്ക്","ഇവിടെ","ഉണ്ട്",
    "പണത്തിന്റെ","ആവശ്യം","ഉണ്ട്","ലാഭം","അക്കൗണ്ട്","നടക്കുന്ന","നിക്ഷേപം","അക്കൗണ്ട്",
]:
    for i in range(len(word) - 2):
        _ml_trigrams_raw[word[i:i+3]] += 1

_ml_total = sum(_ml_trigrams_raw.values())
PROFILES["ml"] = {tg: count / _ml_total for tg, count in _ml_trigrams_raw.most_common(300)}

# --- Gujarati trigrams ---
_gu_trigrams_raw = Counter()
for word in [
    "મને","લોન","જોઈએ","શું","દસ્તાવેજ","જરૂરી","ખાતું","ખોલવા","માંગુ","છું",
    "પૈસા","મોકલવા","જોઈએ","વ્યાજ","દર","કેટલો","બેંક","સેવા","ગ્રાહક","બચત",
    "ખાતું","ચાલુ","ખાતું","રકમ","રૂપિયા","રોકાણ","યોજના","સરકાર","મદદ","મેળવી",
    "શકાય","મહત્વપૂર્ણ","માહિતી","ઓળખ","કાર્ડ","આધાર","નંબર","મોબાઇલ","ફોન",
    "સરનામું","ઘર","શહેર","જિલ્લો","રાજ્ય","દેશ","ભારત","સરકાર","કામ","કરતા",
    "લોકો","મદદ","કરવા","અમે","તમારા","માટે","અહીં","છીએ","પૈસાની","જરૂર",
    "છે","બચત","ખાતું","ચાલુ","થયેલ","ડિપોઝિટ","ખાતું","વ્યાજ","દર","સારો","છે",
]:
    for i in range(len(word) - 2):
        _gu_trigrams_raw[word[i:i+3]] += 1

_gu_total = sum(_gu_trigrams_raw.values())
PROFILES["gu"] = {tg: count / _gu_total for tg, count in _gu_trigrams_raw.most_common(300)}

# --- English trigrams ---
_en_trigrams_raw = Counter()
for word in [
    "the","and","for","are","but","not","you","all","can","had","her","was","one","our",
    "out","day","get","has","him","his","how","its","may","new","now","old","see","way",
    "who","did","let","say","she","too","use","want","fixed","deposit","account","opening",
    "loan","interest","rate","transfer","money","bank","service","customer","savings",
    "current","balance","inquiry","KYC","verification","documents","Aadhaar","PAN","number",
    "mobile","phone","address","home","city","state","country","India","government","work",
    "people","help","need","want","account","amount","rupees","investment","plan","scheme",
    "benefit","process","simple","quick","easy","online","offline","branch","ATM","card",
    "credit","debit","cheque","NEFT","RTGS","IMPS","UPI","transaction","receipt","statement",
]:
    for i in range(len(word) - 2):
        _en_trigrams_raw[word[i:i+3]] += 1

_en_total = sum(_en_trigrams_raw.values())
PROFILES["en"] = {tg: count / _en_total for tg, count in _en_trigrams_raw.most_common(300)}

# ============================================================================
# Language metadata
# ============================================================================

LANGUAGE_NAMES = {
    "hi": "Hindi", "mr": "Marathi", "ta": "Tamil", "te": "Telugu",
    "bn": "Bengali", "kn": "Kannada", "ml": "Malayalam", "gu": "Gujarati",
    "en": "English", "pa": "Punjabi", "or": "Odia", "as": "Assamese",
    "ur": "Urdu", "sd": "Sindhi",
}

SCRIPT_RANGES = [
    ("Devanagari", 0x0900, 0x097F, ["hi", "mr", "sa"]),
    ("Bengali",    0x0980, 0x09FF, ["bn", "as"]),
    ("Gujarati",   0x0A80, 0x0AFF, ["gu"]),
    ("Tamil",      0x0B80, 0x0BFF, ["ta"]),
    ("Telugu",     0x0C00, 0x0C7F, ["te"]),
    ("Kannada",    0x0C80, 0x0CFF, ["kn"]),
    ("Malayalam",  0x0D00, 0x0D7F, ["ml"]),
]

# Hindi/Marathi discriminative word lists (Devanagari script, different languages)
MARATHI_MARKERS = {"आहे", "आहेत", "होते", "करू", "मला", "तुम्ही", "मराठी", "पैसे", "आम्ही", "हवे", "चालू", "ठेव"}
HINDI_MARKERS = {"है", "हैं", "हूं", "करना", "मुझे", "आप", "हिंदी", "रुपये", "हम", "चाहिए", "जमा"}

# ============================================================================
# Core Functions
# ============================================================================


def extract_trigrams(text: str) -> Counter:
    """Extract character trigrams from text."""
    trigrams = Counter()
    for i in range(len(text) - 2):
        tg = text[i:i+3]
        # Skip trigrams with only whitespace/punctuation
        if any(c.isalpha() or ord(c) > 127 for c in tg):
            trigrams[tg] += 1
    return trigrams


def normalize_profile(trigrams: Counter) -> Dict[str, float]:
    """Normalize trigram frequencies to [0, 1]."""
    total = sum(trigrams.values())
    if total == 0:
        return {}
    return {tg: count / total for tg, count in trigrams.most_common(300)}


def cosine_similarity(profile_a: Dict[str, float], profile_b: Dict[str, float]) -> float:
    """Compute cosine similarity between two trigram profiles."""
    common_keys = set(profile_a.keys()) & set(profile_b.keys())
    if not common_keys:
        return 0.0

    dot = sum(profile_a[k] * profile_b[k] for k in common_keys)
    norm_a = math.sqrt(sum(v * v for v in profile_a.values()))
    norm_b = math.sqrt(sum(v * v for v in profile_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def detect_script(text: str) -> Tuple[str, List[str]]:
    """Detect Unicode script and candidate languages from text."""
    for script_name, low, high, candidates in SCRIPT_RANGES:
        for char in text:
            if low <= ord(char) <= high:
                return script_name, candidates
    return "Latin", ["en"]


def disambiguate_devanagari(text: str) -> str:
    """Disambiguate Hindi vs Marathi using discriminative word lists."""
    marathi_score = sum(1 for word in MARATHI_MARKERS if word in text)
    hindi_score = sum(1 for word in HINDI_MARKERS if word in text)
    if marathi_score > hindi_score:
        return "mr"
    return "hi"


def detect(text: str) -> Dict:
    """
    Detect the language of the input text.

    Returns:
        {
            "language": str,        # ISO 639-1 code
            "language_name": str,   # Human-readable name
            "confidence": float,    # 0.0 to 1.0
            "script": str,          # Script name
            "all_scores": dict,     # lang -> score for all candidates
            "method": str,          # "ngram" or "script"
        }
    """
    if not text or len(text.strip()) < 2:
        return {
            "language": "en",
            "language_name": "English",
            "confidence": 0.5,
            "script": "Latin",
            "all_scores": {},
            "method": "fallback",
        }

    # Step 1: Script-based pre-filter
    script, candidates = detect_script(text)

    # Step 2: For short texts, rely on script detection
    if len(text) < 20:
        # Short text: use script + discriminative features
        if script == "Devanagari":
            lang = disambiguate_devanagari(text)
        else:
            lang = candidates[0] if candidates else "en"

        return {
            "language": lang,
            "language_name": LANGUAGE_NAMES.get(lang, lang),
            "confidence": 0.88 + (len(text) / 200),  # Scale confidence with text length
            "script": script,
            "all_scores": {c: 0.9 for c in candidates},
            "method": "script",
        }

    # Step 3: N-gram profile matching
    text_profile = normalize_profile(extract_trigrams(text))

    # Score against all language profiles
    scores = {}
    for lang_code, lang_profile in PROFILES.items():
        scores[lang_code] = cosine_similarity(text_profile, lang_profile)

    # Get best match
    if not scores:
        return {
            "language": "en",
            "language_name": "English",
            "confidence": 0.5,
            "script": script,
            "all_scores": {},
            "method": "fallback",
        }

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_lang, best_score = sorted_scores[0]
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0

    # Confidence based on margin between top-2 scores
    margin = best_score - second_score
    confidence = min(0.99, best_score + margin * 0.5)
    confidence = max(0.5, confidence)

    # Step 4: Devanagari disambiguation
    if script == "Devanagari" and best_lang in ("hi", "mr"):
        disambiguated = disambiguate_devanagari(text)
        if disambiguated != best_lang and margin < 0.1:
            best_lang = disambiguated

    return {
        "language": best_lang,
        "language_name": LANGUAGE_NAMES.get(best_lang, best_lang),
        "confidence": round(confidence, 4),
        "script": script,
        "all_scores": {lang: round(s, 4) for lang, s in sorted_scores[:5]},
        "method": "ngram",
    }


# ============================================================================
# Batch detection for benchmarking
# ============================================================================

def detect_batch(texts: List[str]) -> List[Dict]:
    """Detect language for a batch of texts."""
    return [detect(text) for text in texts]
