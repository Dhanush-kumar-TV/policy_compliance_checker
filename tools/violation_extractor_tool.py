from pydantic import BaseModel

class RuleResultForViolation(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: str
    passed: bool
    # other fields optional, we only need these
    evidence: str | None = None
    matched_keywords: list[str] | None = None

class ViolationExtractorInput(BaseModel):
    results: list[RuleResultForViolation]
    rules: list[dict] # Pass rules to retrieve remediation

class Violation(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: str
    description: str
    remediation: str

class ViolationExtractorOutput(BaseModel):
    total_violations: int
    critical_count: int
    high_count: int
    medium_count: int
    violations: list[Violation]

def extract_violations(input_data: dict) -> dict:
    parsed_input = ViolationExtractorInput(**input_data)
    
    rules_dict = {r["rule_id"]: r for r in parsed_input.rules}
    
    violations = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    
    for res in parsed_input.results:
        if not res.passed:
            rule_def = rules_dict.get(res.rule_id, {})
            severity = res.severity.lower()
            
            if severity == "critical":
                critical_count += 1
            elif severity == "high":
                high_count += 1
            elif severity == "medium":
                medium_count += 1
                
            violations.append(Violation(
                rule_id=res.rule_id,
                rule_name=res.rule_name,
                category=res.category,
                severity=severity,
                description=rule_def.get("description", "No description provided"),
                remediation=rule_def.get("remediation", "No remediation provided")
            ))
            
    output = ViolationExtractorOutput(
        total_violations=len(violations),
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        violations=violations
    )
    return output.model_dump()
