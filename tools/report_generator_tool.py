import uuid
import datetime
from pydantic import BaseModel
from collections import defaultdict

class Violation(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: str
    description: str
    remediation: str
    suggested_fix: str | None = None # Added for violation agent output

class ReportGeneratorInput(BaseModel):
    document_id: str
    compliance_score: float
    grade: str
    risk_level: str
    weighted_score: float
    total_rules: int
    passed: int
    failed: int
    violations: list[Violation]
    run_id: str
    seed: int

class ComplianceReport(BaseModel):
    report_id: str
    run_id: str
    document_id: str
    generated_at: str
    compliance_score: float
    grade: str
    risk_level: str
    executive_summary: str
    violations_by_category: dict[str, list[Violation]]
    top_3_critical_actions: list[str]
    passed_rules: int
    failed_rules: int
    total_rules: int

def generate_report(input_data: dict) -> dict:
    parsed_input = ReportGeneratorInput(**input_data)
    
    report_id = str(uuid.uuid4())
    generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Group violations by category
    violations_by_category = defaultdict(list)
    critical_actions = []
    
    for v in parsed_input.violations:
        violations_by_category[v.category].append(v)
        if v.severity.lower() == "critical":
            critical_actions.append(f"[{v.rule_id}] {v.remediation}")
            if v.suggested_fix:
                critical_actions[-1] += f" (Fix: {v.suggested_fix})"
                
    # Take top 3 critical actions
    top_3_critical_actions = critical_actions[:3]
    
    # Generate an executive summary
    summary = (
        f"This policy compilation evaluated {parsed_input.total_rules} standard rules. "
        f"The document passed {parsed_input.passed} checks and failed {parsed_input.failed} checks, "
        f"resulting in a compliance score of {parsed_input.compliance_score}%. "
        f"The overall grade is {parsed_input.grade} and the business risk level is designated as {parsed_input.risk_level.upper()}."
    )
    
    output = ComplianceReport(
        report_id=report_id,
        run_id=parsed_input.run_id,
        document_id=parsed_input.document_id,
        generated_at=generated_at,
        compliance_score=parsed_input.compliance_score,
        grade=parsed_input.grade,
        risk_level=parsed_input.risk_level,
        executive_summary=summary,
        violations_by_category=dict(violations_by_category),
        top_3_critical_actions=top_3_critical_actions,
        passed_rules=parsed_input.passed,
        failed_rules=parsed_input.failed,
        total_rules=parsed_input.total_rules
    )
    return output.model_dump()
