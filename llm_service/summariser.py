import json
from typing import List, Dict
from config import OLLAMA_HOST, MODEL_NAME, MOCK_MODE, SUPPORTED_LANGUAGES
import httpx


class SessionSummariser:
    """Generates bilingual summaries of banking sessions."""

    def __init__(self):
        self.base_url = OLLAMA_HOST
        self.model = MODEL_NAME
        self.mock_mode = MOCK_MODE

    async def summarise(
        self,
        session_history: List[Dict],
        customer_language: str = "en"
    ) -> Dict:
        """Generate a summary of the session in English and customer's language."""

        if self.mock_mode:
            return self._mock_summary(session_history, customer_language)

        # Build conversation transcript
        transcript = "\n".join([
            f"{msg.get('role', 'user').title()}: {msg.get('text_en', msg.get('text', ''))}"
            for msg in session_history
        ])

        # Detect query type
        query_type = self._detect_query_type(transcript)
        resolved = self._check_resolution(transcript)

        prompt = f"""Analyze this banking conversation and provide a summary in JSON format:

Conversation:
{transcript}

Provide:
{{
  "summary_en": "Brief summary in English (2-3 sentences)",
  "summary_lang": "Brief summary in {customer_language} (2-3 sentences)",
  "query_type": "{query_type}",
  "resolved": {resolved},
  "key_points": ["point 1", "point 2", "point 3"],
  "action_items": ["action 1", "action 2"]
}}

Keep it concise and professional."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": "You are a banking assistant. Provide responses in valid JSON format only.",
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = response.json()

                response_text = result.get("response", "{}")
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(0))

        except Exception as e:
            print(f"Summariser error: {e}")
            return self._mock_summary(session_history, customer_language)

    def _detect_query_type(self, transcript: str) -> str:
        """Detect the type of banking query."""
        transcript_lower = transcript.lower()

        query_types = {
            "Account Opening": ["account", "open", "new account", "savings", "current"],
            "Loan Enquiry": ["loan", "borrow", "credit", "emi", "interest rate"],
            "KYC Verification": ["kyc", "verify", "identity", "document", "aadhaar", "pan"],
            "Fixed Deposit": ["fd", "fixed deposit", "term deposit", "invest"],
            "Remittance": ["remit", "transfer", "send money", "neft", "rtgs", "imps"],
            "Complaint": ["complaint", "issue", "problem", "dispute", "grievance"],
            "Balance Enquiry": ["balance", "how much", "check balance"],
            "Transaction Issue": ["transaction", "failed", "debit", "credit", "not received"]
        }

        for qtype, keywords in query_types.items():
            if any(kw in transcript_lower for kw in keywords):
                return qtype

        return "General Enquiry"

    def _check_resolution(self, transcript: str) -> bool:
        """Check if the query was resolved."""
        positive_indicators = ["thank you", "thanks", "resolved", "done", "completed", "perfect", "great", "satisfied"]
        negative_indicators = ["not resolved", "still issue", "escalate", "manager", "supervisor", "complaint"]

        transcript_lower = transcript.lower()

        # Check for explicit resolution indicators
        if any(ind in transcript_lower for ind in positive_indicators):
            # Also check that there are no negative indicators
            if not any(ind in transcript_lower for ind in negative_indicators):
                return True

        # If conversation ended with information sharing, consider it resolved
        # This is a heuristic - in practice, you'd want more sophisticated detection
        return False

    def _mock_summary(self, session_history: List[Dict], customer_language: str) -> Dict:
        """Generate mock summary for testing."""
        # Combine all messages
        all_text = " ".join([
            msg.get('text_en', msg.get('text', ''))
            for msg in session_history
        ])

        query_type = self._detect_query_type(all_text)
        resolved = self._check_resolution(all_text)

        # Extract key points (mock)
        key_points = [
            "Customer visited the branch for assistance",
            f"Query related to {query_type}",
            "Bank staff provided necessary guidance"
        ]

        # Mock translations for different languages
        translations = {
            "hi": "ग्राहक शाखा में सहायता के लिए आया था। बैंक कर्मचारी ने आवश्यक मार्गदर्शन प्रदान किया।",
            "ta": "வாடிக்கையாளர் உதவிக்கு கிளையில் வந்தார். வங்கி ஊழியர் தேவையான வழிகாட்டுதலை வழங்கினார்.",
            "te": "కస్టమర్ సహాయం కోసం బ్రాంచ్‌కి వచ్చారు. బ్యాంక్ సిబ్బంది అవసరమైన మార్గనిర్దేశం అందించారు.",
            "kn": "ಗ್ರಾಹಕರು ಸಹಾಯಕ್ಕಾಗಿ ಶಾಖೆಗೆ ಭೇಟಿ ನೀಡಿದರು. ಬ್ಯಾಂಕ್ ಸಿಬ್ಬಂದಿ ಅಗತ್ಯ ಮಾರ್ಗದರ್ಶನ ನೀಡಿದರು.",
            "ml": "സഹായത്തിനായി ഉപഭോക്താവ് ശാഖയിൽ എത്തി. ബാങ്ക് ജീവനക്കാർ ആവശ്യമായ മാർഗ്ഗനിർദ്ദേശം നൽകി.",
            "mr": "ग्राहक मदतीसाठी शाखेत आला. बँक कर्मचाऱ्यांनी आवश्यक मार्गदर्शन केले.",
            "gu": "ગ્રાહક મદદ માટે શાખામાં આવ્યા હતા. બેંક સ્ટાફે જરૂરી માર્ગદર્શન આપ્યું.",
            "bn": "সহাযতার জন্য গ্রাহক শাখায় এসেছিলেন। ব্যাংক কর্মীরা প্রয়োজনীয় নির্দেশনা প্রদান করেছেন।",
            "or": "ସହାୟତା ପାଇଁ ଗ୍ରାହକ ଶାଖାରେ ଆସିଥିଲେ। ବ୍ୟାଙ୍କ କର୍ମଚାରୀ ଆବଶ୍ୟକୀୟ ନିର୍ଦ୍ଦେබ ପ୍ରଦାନ କରିଥିଲେ।"
        }

        summary_lang = translations.get(customer_language, all_text[:100] + "...")

        # Generate specific summary based on query type
        summary_en_templates = {
            "Account Opening": f"Customer enquired about opening a new account. Staff explained the account opening process, required documents (PAN, Aadhaar), and minimum balance requirements. {'Query resolved.' if resolved else 'Follow-up required.'}",
            "Loan Enquiry": f"Customer sought information about loans. Staff provided details on interest rates, eligibility criteria, and required documentation. {'Loan application process explained.' if resolved else 'Further assessment needed.'}",
            "KYC Verification": f"Customer's KYC verification was processed. Staff collected and verified identity and address documents as per RBI guidelines. {'KYC completed successfully.' if resolved else 'Additional documents required.'}",
            "Fixed Deposit": f"Customer enquired about fixed deposit options. Staff explained current interest rates, tenure options, and premature withdrawal norms. {'FD booking completed.' if resolved else 'Customer considering options.'}",
            "Remittance": f"Customer required fund transfer assistance. Staff guided through NEFT/RTGS/IMPS process and verified beneficiary details. {'Transfer completed.' if resolved else 'Transaction pending authentication.'}",
            "Complaint": f"Customer lodged a complaint. Staff recorded the grievance and provided a reference number. {'Issue resolved.' if resolved else 'Complaint forwarded for resolution.'}"
        }

        summary_en = summary_en_templates.get(
            query_type,
            f"Customer visited the branch for {query_type}. Banking staff provided necessary assistance and guidance."
        )

        # Action items based on resolution
        action_items = []
        if not resolved:
            action_items.append("Follow up with customer")
            if query_type == "Loan Enquiry":
                action_items.extend(["Process loan application", "Conduct credit assessment"])
            elif query_type == "Account Opening":
                action_items.extend(["Complete account opening", "Generate account number"])
            elif query_type == "Complaint":
                action_items.extend(["Monitor complaint resolution", "Update customer"])
        else:
            action_items.append("Close session")

        return {
            "summary_en": summary_en,
            "summary_lang": summary_lang,
            "query_type": query_type,
            "resolved": resolved,
            "key_points": key_points,
            "action_items": action_items
        }


# Singleton instance
_summariser = None

def get_summariser() -> SessionSummariser:
    global _summariser
    if _summariser is None:
        _summariser = SessionSummariser()
    return _summariser
