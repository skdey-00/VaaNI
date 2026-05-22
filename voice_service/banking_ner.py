"""
Banking Named Entity Recognition (NER) for Indian Languages
============================================================

Extracts banking-specific entities from multilingual text using:
  1. Regex patterns for amounts, rates, time periods
  2. Gazetteer lookup for account types, documents, transaction types
  3. Multilingual term dictionaries (Hindi, Tamil, Telugu, Bengali, Kannada, Malayalam, Gujarati)

Entity Types: AMOUNT, ACCOUNT_TYPE, DOCUMENT, TRANSACTION_TYPE,
              LOAN_TYPE, INTEREST_RATE, TIME_PERIOD, BANK_PRODUCT
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple


@dataclass
class Entity:
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float
    normalized_value: Optional[str] = None


# ============================================================================
# Gazetteers (multilingual banking term lists)
# ============================================================================

ACCOUNT_TYPES = {
    "savings", "current", "salary", "NRI", "NRO", "NRE", "FCNR",
    "FD", "fixed deposit", "term deposit", "recurring deposit",
    "PPF", "public provident fund", "NPS", "national pension system",
    "demat", "joint account", "zero balance",
    # Hindi
    "बचत खाता", "चालू खाता", "सैलरी खाता", "एफडी", "फिक्स्ड डिपॉजिट",
    "आरडी", "रिकरिंग डिपॉजिट", "संयुक्त खाता",
    # Tamil
    "சேமிப்பு கணக்கு", "நடப்பு கணக்கு",
    # Telugu
    "పొదుపు ఖాతా", "ప్రస్తుత ఖాతా",
    # Bengali
    "সঞ্চয় অ্যাকাউন্ট", "চলতি অ্যাকাউন্ট",
}

DOCUMENTS = {
    "aadhaar", "aadhar", "adhar", "UID", "UIDAI",
    "PAN", "permanent account number",
    "passport", "voter ID", "voter card", "driving license", "DL",
    "Form 16", "salary slip", "income proof", "address proof",
    "ITR", "income tax return", "bank statement", "passbook",
    "cheque", "cancelled cheque", "KYC",
    # Hindi
    "आधार", "पैन", "पासपोर्ट", "वोटर", "ड्राइविंग लाइसेंस", "सैलरी स्लिप",
    "बैंक स्टेटमेंट", "पासबुक", "फॉर्म", "आय प्रमाण", "पता प्रमाण",
    # Other languages
    "ஆதார்", "ఆధార్", "ಆಧಾರ್", "ആധാർ",
}

TRANSACTION_TYPES = {
    "NEFT", "RTGS", "IMPS", "UPI", "cheque", "DD", "demand draft",
    "wire transfer", "SWIFT", "ACH", "ECS", "NACH",
    "online transfer", "mobile transfer", "bank transfer",
    # Hindi
    "एनईएफटी", "आरटीजीएस", "आईएमपीएस", "यूपीआई", "चेक", "डीडी",
    "ऑनलाइन ट्रांसफर", "बदली",
    # Tamil
    "நெஃப்ட்", "ஆர்டிஜிஎஸ்",
}

LOAN_TYPES = {
    "home loan", "personal loan", "car loan", "auto loan", "education loan",
    "business loan", "gold loan", "loan against property", "LAP",
    "mortgage",    "overdraft", "OD", "cash credit",
    "agricultural loan", "crop loan", "kisan credit card", "KCC",
    # Hindi
    "होम लोन", "पर्सनल लोन", "कार लोन", "शिक्षा ऋण", "व्यापार ऋण",
    "सोने का ऋण", "संपत्ति पर ऋण", "किसान क्रेडिट कार्ड",
    "गृह ऋण", "शिक्षा लोन", "बिज़नेस लोन",
    # Tamil
    "வீட்டுக் கடன்", "தனிப்பட்ட கடன்", "கார் கடன்", "கல்வி கடன்",
    # Bengali
    "গৃহ ঋণ", "ব্যক্তিগত ঋণ", "শিক্ষা ঋণ",
}

BANK_PRODUCTS = {
    "mutual fund", "SIP", "systematic investment plan", "FD",
    "insurance", "term insurance", "health insurance", "life insurance",
    "credit card", "debit card", "ATM card", "net banking", "mobile banking",
    "demat account", "trading account",
    # Hindi
    "म्यूचुअल फंड", "एसआईपी", "बीमा", "टर्म बीमा", "स्वास्थ्य बीमा",
    "जीवन बीमा", "क्रेडिट कार्ड", "डेबिट कार्ड", "एटीएम कार्ड",
    "नेट बैंकिंग", "मोबाइल बैंकिंग",
}


# ============================================================================
# Regex Patterns
# ============================================================================

# Amount patterns (₹, Rs, INR, lakh, crore, rupees)
AMOUNT_PATTERNS = [
    (r'₹\s*[\d,]+(?:\.\d{1,2})?', 'AMOUNT'),
    (r'(?:Rs\.?|RS\.?|INR)\s*[\d,]+(?:\.\d{1,2})?', 'AMOUNT'),
    (r'[\d,]+(?:\.\d{1,2})?\s*(?:rupees|रुपये|টাকা|ரூபாய்)', 'AMOUNT'),
    (r'[\d,]+(?:\.\d{2})?\s*(?:lakh|lac|lACS?)\b', 'AMOUNT'),
    (r'[\d,]+(?:\.\d{2})?\s*(?:crore|CR)\b', 'AMOUNT'),
    (r'(?:लाख|কোটি|லட்சம்)\s*[\d,]+', 'AMOUNT'),
    (r'[\d,]+\s*(?:लाख|কোটি|லட্চம்|లక్షల)', 'AMOUNT'),
]

# Interest rate patterns
RATE_PATTERNS = [
    (r'[\d]+(?:\.\d{1,2})?\s*%\s*(?:p\.?a\.?|per\s+annum|annual|yearly|ब्याज|व्याज|வட்டி)', 'INTEREST_RATE'),
    (r'(?:interest|rate|ब्याज|व्याज|वड्डी|வட்டி|వడ్డీ)\s*(?:rate\s*)?(?:of\s*)?[\d]+(?:\.\d{1,2})?\s*%', 'INTEREST_RATE'),
    (r'[\d]+(?:\.\d{1,2})?\s*%', 'INTEREST_RATE'),
]

# Time period patterns
TIME_PATTERNS = [
    (r'[\d]+\s*(?:years?|yr|yrs|साल|वर्ष|سال|বছর|ஆண்டு|సంవత్సరం|ವರ್ಷ|വർഷം)', 'TIME_PERIOD'),
    (r'[\d]+\s*(?:months?|mo|महीने|মাস|மாதம்|నెల|ತಿಂಗಳು|മാസം)', 'TIME_PERIOD'),
    (r'[\d]+\s*(?:days?|दिन|দিন|நாள்|రోజు|ದಿನ|ദിവസം)', 'TIME_PERIOD'),
]


# ============================================================================
# NER Engine
# ============================================================================

class BankingNER:
    """Banking Named Entity Recognition engine."""

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self.amount_regexes = [(re.compile(p, re.IGNORECASE), t) for p, t in AMOUNT_PATTERNS]
        self.rate_regexes = [(re.compile(p, re.IGNORECASE), t) for p, t in RATE_PATTERNS]
        self.time_regexes = [(re.compile(p, re.IGNORECASE), t) for p, t in TIME_PATTERNS]

        # Build combined gazetteer for quick lookup
        self.gazetteer: Dict[str, Tuple[str, float]] = {}
        for term in ACCOUNT_TYPES:
            self.gazetteer[term.lower()] = ("ACCOUNT_TYPE", 0.92)
        for term in DOCUMENTS:
            self.gazetteer[term.lower()] = ("DOCUMENT", 0.90)
        for term in TRANSACTION_TYPES:
            self.gazetteer[term.lower()] = ("TRANSACTION_TYPE", 0.94)
        for term in LOAN_TYPES:
            self.gazetteer[term.lower()] = ("LOAN_TYPE", 0.91)
        for term in BANK_PRODUCTS:
            self.gazetteer[term.lower()] = ("BANK_PRODUCT", 0.88)

    def extract(self, text: str) -> List[Entity]:
        """
        Extract all banking entities from text.

        Returns list of Entity objects sorted by position.
        """
        entities: List[Entity] = []
        seen_spans = set()

        # 1. Regex-based extraction
        entities.extend(self._extract_regex(text, self.amount_regexes, seen_spans))
        entities.extend(self._extract_regex(text, self.rate_regexes, seen_spans))
        entities.extend(self._extract_regex(text, self.time_regexes, seen_spans))

        # 2. Gazetteer-based extraction
        entities.extend(self._extract_gazetteer(text, seen_spans))

        # Sort by position
        entities.sort(key=lambda e: e.start)
        return entities

    def _extract_regex(self, text: str, patterns: List[Tuple], seen: set) -> List[Entity]:
        """Extract entities using regex patterns."""
        entities = []
        for regex, entity_type in patterns:
            for match in regex.finditer(text):
                span = (match.start(), match.end())
                if not self._overlaps(span, seen):
                    seen.add(span)
                    normalized = self._normalize_value(match.group(), entity_type)
                    entities.append(Entity(
                        text=match.group(),
                        entity_type=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.92,
                        normalized_value=normalized,
                    ))
        return entities

    def _extract_gazetteer(self, text: str, seen: set) -> List[Entity]:
        """Extract entities using gazetteer lookup."""
        entities = []
        text_lower = text.lower()

        # Sort gazetteer terms by length (longest first) to match most specific
        sorted_terms = sorted(self.gazetteer.keys(), key=len, reverse=True)

        for term in sorted_terms:
            if len(term) < 2:
                continue
            start = 0
            while True:
                idx = text_lower.find(term, start)
                if idx == -1:
                    break
                span = (idx, idx + len(term))
                if not self._overlaps(span, seen):
                    seen.add(span)
                    entity_type, confidence = self.gazetteer[term]
                    entities.append(Entity(
                        text=text[idx:idx + len(term)],
                        entity_type=entity_type,
                        start=idx,
                        end=idx + len(term),
                        confidence=confidence,
                    ))
                start = idx + 1

        return entities

    def _overlaps(self, span: Tuple[int, int], seen: set) -> bool:
        """Check if a span overlaps with any existing spans."""
        for s in seen:
            if span[0] < s[1] and span[1] > s[0]:
                return True
        return False

    def _normalize_value(self, text: str, entity_type: str) -> Optional[str]:
        """Normalize extracted values to standard format."""
        if entity_type == "AMOUNT":
            # Remove currency symbols and normalize
            val = re.sub(r'[₹Rs\.INR\s]', '', text, flags=re.IGNORECASE)
            val = val.replace(',', '')
            if 'lakh' in text.lower() or 'lac' in text.lower() or 'लाख' in text:
                try:
                    return f"₹{float(val) * 100000:,.0f}"
                except ValueError:
                    pass
            elif 'crore' in text.lower() or 'CR' in text:
                try:
                    return f"₹{float(val) * 10000000:,.0f}"
                except ValueError:
                    pass
            else:
                try:
                    return f"₹{float(val):,.2f}"
                except ValueError:
                    pass
        elif entity_type == "INTEREST_RATE":
            val = re.search(r'([\d]+(?:\.\d{1,2})?)\s*%', text)
            if val:
                return f"{val.group(1)}% p.a."
        elif entity_type == "TIME_PERIOD":
            return text.strip()
        return None


# Convenience function
_ner = BankingNER()

def extract_entities(text: str) -> List[Entity]:
    """Extract banking entities from text."""
    return _ner.extract(text)


def extract_entities_dict(text: str) -> List[Dict]:
    """Extract banking entities and return as dictionaries."""
    entities = extract_entities(text)
    return [
        {
            "text": e.text,
            "entity_type": e.entity_type,
            "start": e.start,
            "end": e.end,
            "confidence": e.confidence,
            "normalized_value": e.normalized_value,
        }
        for e in entities
    ]
