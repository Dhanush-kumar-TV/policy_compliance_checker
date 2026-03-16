from pydantic import BaseModel

class ScoreCalculatorInput(BaseModel):
    total_rules: int
    passed: int
    violations: list[dict] # we can accept violations as dicts for simple passing
    rules: list[dict] # all rules for weight calculation

class ScoreCalculatorOutput(BaseModel):
    compliance_score: float
    grade: str
    risk_level: str
    weighted_score: float

def calculate_score(input_data: dict) -> dict:
    parsed_input = ScoreCalculatorInput(**input_data)
    
    # 1. Compliance Score
    if parsed_input.total_rules > 0:
        compliance_score = (parsed_input.passed / parsed_input.total_rules) * 100.0
    else:
        compliance_score = 0.0
        
    # Grade thresholds: A=90+, B=75+, C=60+, D=40+, F=<40
    if compliance_score >= 90:
        grade = "A"
    elif compliance_score >= 75:
        grade = "B"
    elif compliance_score >= 60:
        grade = "C"
    elif compliance_score >= 40:
        grade = "D"
    else:
        grade = "F"
        
    # Risk level: Low=80+, Medium=60+, High=40+, Critical=<40
    # The prompt says score based?
    if compliance_score >= 80:
        risk_level = "Low"
    elif compliance_score >= 60:
        risk_level = "Medium"
    elif compliance_score >= 40:
        risk_level = "High"
    else:
        risk_level = "Critical"
        
    # Weighted score
    weight_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    
    total_weight = 0
    passed_weight = 0
    
    # Find which rules failed from violations
    failed_rule_ids = {v["rule_id"] for v in parsed_input.violations}
    
    for rule in parsed_input.rules:
        w = weight_map.get(rule.get("severity", "low").lower(), 1)
        total_weight += w
        if rule["rule_id"] not in failed_rule_ids:
            passed_weight += w
            
    weighted_score = (passed_weight / total_weight) * 100.0 if total_weight > 0 else 0.0
    
    output = ScoreCalculatorOutput(
        compliance_score=round(compliance_score, 2),
        grade=grade,
        risk_level=risk_level,
        weighted_score=round(weighted_score, 2)
    )
    return output.model_dump()
