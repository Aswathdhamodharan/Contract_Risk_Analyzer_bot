import json
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import config
from risk_scorer import RiskScorer

class ContractAnalyzer:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or config.GOOGLE_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL
        self.model = None
        if self.api_key and "YOUR_API_KEY" not in self.api_key:
             try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
             except Exception as e:
                 print(f"Error configuring Gemini: {e}")
                 
        self.scorer = RiskScorer()

    def analyze_contract(self, contract_text: str, contract_type_hint: str = "General") -> dict:
        """
        Analyze contract using Google Gemini API.
        Returns a dictionary with structured analysis.
        """
        if not self.model:
            return {
                "error": "API Key not configured. Please provide a valid Google API Key."
            }
            
        prompt = f"""
        You are a legal contract analyst specializing in Indian SME contracts.
        
        Analyze this {contract_type_hint} contract text and provide a structured JSON output.
        Focus on identifying risks, obligations, and key terms.
        
        Output format (STRICTLY JSON, no markdown code blocks, just the raw JSON):
        {{
            "contract_type": "Type of contract (Employment/Vendor/Lease/etc)",
            "summary": "Plain language summary of what this contract is about (2-3 sentences)",
            "parties": ["Party A", "Party B"],
            "contract_date": "Date if found",
            "jurisdiction": "City/State/Country laws applicable",
            "clauses": [
                {{
                    "id": "1",
                    "title": "Title of clause",
                    "text": "Full text or summary of clause",
                    "type": "Category (e.g., Termination, Payment, Indemnity, Non-Compete)",
                    "risk_level": "Low/Medium/High",
                    "explanation": "Simple explanation of what this means for the user",
                    "recommendation": "Negotiation tip or alternative wording if risky"
                }}
            ],
            "overall_risk_factors": ["List of key risky terms found globally"]
        }}
        
        Contract Text:
        {contract_text[:30000]} 
        """
        # Truncating to 30k chars to stay within safe limits, though Gemini has large context.
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Simple cleaning if Gemini adds markdown blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            analysis = json.loads(content.strip())
            
            # Post-process with internal RiskScorer for consistent scoring verification
            clauses = analysis.get("clauses", [])
            for clause in clauses:
                # Augment with numeric score
                clause["risk_score"] = self.scorer.calculate_clause_risk(
                    clause.get("text", "") + " " + clause.get("title", ""),
                    clause.get("type", "")
                )
                
            # Calculate overall metrics
            composite_metrics = self.scorer.calculate_composite_risk(clauses)
            analysis["risk_metadata"] = composite_metrics
            
            return analysis
            
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse AI response. The model might have returned unstructured text.",
                "raw_response": content if 'content' in locals() else "No content"
            }
        except google_exceptions.PermissionDenied:
             return {
                "error": "Authentication Failed: Invalid API Key. Please check your key in the sidebar."
            }
        except google_exceptions.InvalidArgument:
            return {
                 "error": "Invalid Argument: The request was rejected. Check if the text is too long or malformed."
            }
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}"
            }
