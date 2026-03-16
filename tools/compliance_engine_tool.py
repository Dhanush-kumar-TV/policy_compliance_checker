import re
from pydantic import BaseModel

class ComplianceEngineInput(BaseModel):
    document_id: str
    full_text: str
    rules: list[dict]

class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: str
    passed: bool
    matched_keywords: list[str]
    evidence: str | None

class ComplianceEngineOutput(BaseModel):
    document_id: str
    total_rules: int
    passed: int
    failed: int
    results: list[RuleResult]

def run_compliance_check(input_data: dict) -> dict:
    parsed_input = ComplianceEngineInput(**input_data)
    text = parsed_input.full_text
    text_lower = text.lower()
    
    # Extract sentences to find evidence
    # Simple split by period, newline
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +|\n+', text) if s.strip()]
    
    results = []
    passed_count = 0
    failed_count = 0
    
    for rule in parsed_input.rules:
        matched_keywords = []
        evidence = None
        passed = False
        
        for kw in rule.get("keywords", []):
            if kw.lower() in text_lower:
                matched_keywords.append(kw)
                passed = True
                # Find evidence sentence
                if not evidence:
                    for sentence in sentences:
                        if kw.lower() in sentence.lower():
                            evidence = sentence
                            break
                            
        if passed:
            passed_count += 1
        else:
            failed_count += 1
            
        results.append(RuleResult(
            rule_id=rule["rule_id"],
            rule_name=rule["name"],
            category=rule["category"],
            severity=rule["severity"],
            passed=passed,
            matched_keywords=matched_keywords,
            evidence=evidence
        ))
        
    output = ComplianceEngineOutput(
        document_id=parsed_input.document_id,
        total_rules=len(parsed_input.rules),
        passed=passed_count,
        failed=failed_count,
        results=results
    )
    return output.model_dump()
