import json
import httpx
from typing import Any
from config import OLLAMA_HOST, MODEL_NAME, MOCK_MODE, SYSTEM_PROMPT


class LLMClient:
    """Client for interacting with Ollama LLM service."""

    def __init__(self):
        self.base_url = OLLAMA_HOST
        self.model = MODEL_NAME
        self.mock_mode = MOCK_MODE

    async def generate(
        self,
        prompt: str,
        context: str = "",
        language: str = "en"
    ) -> dict[str, Any]:
        """Generate a response from the LLM."""

        if self.mock_mode:
            return self._mock_response(prompt, context)

        system_prompt = SYSTEM_PROMPT.format(language=language)

        # Build the full prompt with context
        full_prompt = f"""Context:
{context}

User Query:
{prompt}

Provide your response as JSON only."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "system": system_prompt,
                        "stream": False,
                        "format": "json",
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9,
                            "num_predict": 500
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()

                # Parse the response
                response_text = result.get("response", "{}")

                # Try to extract JSON from the response
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    # If the model didn't return valid JSON, try to extract it
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(0))
                    else:
                        # Fallback response
                        return {
                            "suggestions": ["Please rephrase your request."],
                            "process_steps": [],
                            "escalate": False
                        }

        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                "suggestions": ["I'm having trouble connecting to the AI service. Please try again."],
                "process_steps": [],
                "escalate": True,
                "reasoning": "Service unavailable"
            }

    def _mock_response(self, prompt: str, context: str) -> dict[str, Any]:
        """Generate mock responses for testing."""
        prompt_lower = prompt.lower()

        # Account Opening
        if any(kw in prompt_lower for kw in ["account", "open", "new account", "savings", "current"]):
            return {
                "suggestions": [
                    "Ask the customer for PAN card and Aadhaar card",
                    "Verify the customer's KYC documents",
                    "Explain the types of accounts available: Savings, Current, Salary Account",
                    "Inform about minimum balance requirements",
                    "Fill the account opening form with customer details"
                ],
                "process_steps": [
                    {"step": 1, "description": "Obtain and verify PAN card", "done": False},
                    {"step": 2, "description": "Obtain and verify Aadhaar card (with Aadhaar XML if paperless)", "done": False},
                    {"step": 3, "description": "Capture recent passport-size photograph", "done": False},
                    {"step": 4, "description": "Fill Account Opening Form (AOF) with customer details", "done": False},
                    {"step": 5, "description": "Complete KYC verification and biometric authentication", "done": False},
                    {"step": 6, "description": "Make initial deposit (minimum balance as per account type)", "done": False},
                    {"step": 7, "description": "Generate account number and provide welcome kit", "done": False}
                ],
                "escalate": False
            }

        # Loan Enquiry
        elif any(kw in prompt_lower for kw in ["loan", "borrow", "credit", "interest rate", "emi"]):
            return {
                "suggestions": [
                    "Ask about the type of loan: Home, Personal, Auto, or Business",
                    "Check the customer's CIBIL score",
                    "Explain the current interest rates",
                    "Calculate EMI based on loan amount and tenure",
                    "Collect income documents for loan eligibility assessment"
                ],
                "process_steps": [
                    {"step": 1, "description": "Identify loan type and customer requirements", "done": False},
                    {"step": 2, "description": "Check customer's credit score (CIBIL)", "done": False},
                    {"step": 3, "description": "Explain interest rates and charges", "done": False},
                    {"step": 4, "description": "Calculate EMI and provide amortization schedule", "done": False},
                    {"step": 5, "description": "Collect income documents (salary slips, IT returns, Form 16)", "done": False},
                    {"step": 6, "description": "Assess loan eligibility based on income and existing EMIs", "done": False},
                    {"step": 7, "description": "Provide loan quotation and collect application", "done": False}
                ],
                "escalate": False
            }

        # KYC Verification
        elif any(kw in prompt_lower for kw in ["kyc", "verify", "identity", "document", "aadhaar", "pan"]):
            return {
                "suggestions": [
                    "Accept Aadhaar card or passport as proof of identity",
                    "Accept Aadhaar, passport, voter ID, or utility bills as proof of address",
                    "Use Aadhaar OTP or biometric for e-KYC verification",
                    "Ensure documents are valid and not expired",
                    "For NRIs, collect passport and valid visa copy"
                ],
                "process_steps": [
                    {"step": 1, "description": "Collect Proof of Identity (POI) - PAN/Aadhaar/Passport", "done": False},
                    {"step": 2, "description": "Collect Proof of Address (POA) - Aadhaar/Utility Bill/Passport", "done": False},
                    {"step": 3, "description": "Collect recent passport-size photograph", "done": False},
                    {"step": 4, "description": "Verify document authenticity and validity dates", "done": False},
                    {"step": 5, "description": "Perform e-KYC via Aadhaar OTP/biometric OR offline KYC with Aadhaar XML", "done": False},
                    {"step": 6, "description": "Complete CKYCCR (Central KYC Records Registry) verification", "done": False},
                    {"step": 7, "description": "Update customer profile with KYC details", "done": False}
                ],
                "escalate": False
            }

        # FD Booking
        elif any(kw in prompt_lower for kw in ["fd", "fixed deposit", "term deposit", "invest"]):
            return {
                "suggestions": [
                    "Explain current FD interest rates for different tenures",
                    "Inform about premature withdrawal penalties",
                    "Explain tax deduction at source (TDS) on interest",
                    "Offer auto-renewal facility for FD maturity",
                    "Suggest FD laddering for better liquidity"
                ],
                "process_steps": [
                    {"step": 1, "description": "Discuss FD tenure options and interest rates", "done": False},
                    {"step": 2, "description": "Explain premature withdrawal rules and penalties", "done": False},
                    {"step": 3, "description": "Verify customer has savings account for debit", "done": False},
                    {"step": 4, "description": "Fill FD opening form with nomination details", "done": False},
                    {"step": 5, "description": "Debit amount from customer's account", "done": False},
                    {"step": 6, "description": "Issue FD receipt with maturity date and amount", "done": False}
                ],
                "escalate": False
            }

        # Remittance
        elif any(kw in prompt_lower for kw in ["remit", "transfer", "send money", "wire", "neft", "rtgs", "imps"]):
            return {
                "suggestions": [
                    "Confirm the transfer method: IMPS (instant), NEFT, or RTGS",
                    "Check daily transfer limits for customer's account",
                    "Verify beneficiary details before adding",
                    "Inform about charges for IMPS/NEFT/RTGS",
                    "For international transfers, collect purpose of remittance and Form A2"
                ],
                "process_steps": [
                    {"step": 1, "description": "Identify transfer type and amount", "done": False},
                    {"step": 2, "description": "Add or verify beneficiary account details", "done": False},
                    {"step": 3, "description": "Check account balance and daily limits", "done": False},
                    {"step": 4, "description": "For RTGS (>₹2 lakh): Use RTGS; For NEFT (<₹2 lakh): Use NEFT", "done": False},
                    {"step": 5, "description": "For instant transfer (<₹5 lakh): Use IMPS", "done": False},
                    {"step": 6, "description": "Authenticate transaction via SMS OTP or debit card PIN", "done": False},
                    {"step": 7, "description": "Provide transaction confirmation with UTR reference number", "done": False}
                ],
                "escalate": False
            }

        # Complaint Lodging
        elif any(kw in prompt_lower for kw in ["complaint", "issue", "problem", "dispute", "grievance"]):
            return {
                "suggestions": [
                    "Listen carefully and note down the customer's grievance",
                    "Acknowledge the issue and express empathy",
                    "Check if the issue can be resolved immediately",
                    "If not, lodge a complaint with unique reference number",
                    "Inform about the resolution timeline (SLA)",
                    "Offer to escalate to branch manager if unsatisfied"
                ],
                "process_steps": [
                    {"step": 1, "description": "Record customer's complaint details in the complaint register", "done": False},
                    {"step": 2, "description": "Categorize complaint type (transaction/account/service/ATM)", "done": False},
                    {"step": 3, "description": "Check if immediate resolution is possible", "done": False},
                    {"step": 4, "description": "If not resolved, raise ticket in CMS (Complaint Management System)", "done": False},
                    {"step": 5, "description": "Provide complaint reference number to customer", "done": False},
                    {"step": 6, "description": "Inform about resolution timeline (usually 7-14 working days)", "done": False},
                    {"step": 7, "description": "Follow up with customer within promised timeline", "done": False}
                ],
                "escalate": any(kw in prompt_lower for kw in ["manager", "supervisor", "escalate"])
            }

        # Default - escalation for unknown queries
        return {
            "suggestions": [
                "Listen carefully to the customer's request",
                "If unsure about the procedure, consult the branch operations manual",
                "Consider escalating to the branch manager for complex queries"
            ],
            "process_steps": [],
            "escalate": True,
            "reasoning": "Unable to identify specific banking process"
        }


# Singleton instance
_llm_client = None

def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
