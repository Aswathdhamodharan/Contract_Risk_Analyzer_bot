from typing import List, Dict, Any

class RiskScorer:
    def __init__(self):
        # Keywords to help identify risky clauses if not explicitly tagged by LLM
        # or to validate LLM output.
        self.risk_patterns = {
            "high": [
                "penalty", "liquidated damages", "unilateral termination", 
                "termination for convenience", "indemnify", "indemnification",
                "non-compete", "exclusivity", "governing law", "arbitration"
            ],
            "medium": [
                "auto-renewal", "automatic renewal", "confidentiality",
                "non-solicitation", "payment terms", "late fee",
                "limitation of liability"
            ],
            "low": [
                "definitions", "preamble", "recitals", "force majeure",
                "notices", "amendment"
            ]
        }
        
        # Base scores (0-10) for types
        self.risk_weights = {
            "penalty": 9,
            "unilateral termination": 9,
            "indemnity": 8,
            "non-compete": 8,
            "ip transfer": 8,
            "confidentiality": 4,
            "auto-renewal": 6,
            "arbitration": 7,
            "jurisdiction": 5
        }

    def calculate_clause_risk(self, clause_text: str, clause_type: str = None) -> int:
        """
        Calculate risk score for a single clause (0-10).
        Uses clause_type if provided (from LLM), otherwise heuristic text analysis.
        """
        score = 1 # Minimum risk
        text_lower = clause_text.lower()
        
        # 1. Use type-based base score if available
        if clause_type:
            for key, weight in self.risk_weights.items():
                if key in clause_type.lower():
                    score = max(score, weight)
        
        # 2. Text-based heuristic boost
        for keyword in self.risk_patterns["high"]:
            if keyword in text_lower:
                score = max(score, 7)
        
        for keyword in self.risk_patterns["medium"]:
            if keyword in text_lower and score < 5:
                score = max(score, 5)
                
        # 3. Specific boosters
        if "shall pay" in text_lower or "liable for" in text_lower:
            score += 1
            
        return min(10, score) # Cap at 10

    def calculate_composite_risk(self, clauses_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall contract risk score.
        clauses_analysis: List of dicts with 'risk_score' and 'type' keys.
        """
        if not clauses_analysis:
            return {"score": 0, "level": "Low", "breakdown": {}}
            
        total_score = 0
        max_clause_score = 0
        high_risk_count = 0
        
        for clause in clauses_analysis:
            r_score = clause.get('risk_score', 0)
            total_score += r_score
            if r_score > max_clause_score:
                max_clause_score = r_score
            if r_score >= 7:
                high_risk_count += 1
                
        avg_score = total_score / len(clauses_analysis)
        
        # Composite score logic: Weighted average but heavily influenced by max risk
        # A valid contract with one terrible clause is still a risky contract.
        composite = (avg_score * 0.4) + (max_clause_score * 0.6)
        
        # Determine level
        if composite >= 7:
            level = "High"
        elif composite >= 4:
            level = "Medium"
        else:
            level = "Low"
            
        return {
            "score": round(composite, 1),
            "level": level,
            "max_clause_score": max_clause_score,
            "high_risk_clauses": high_risk_count
        }
