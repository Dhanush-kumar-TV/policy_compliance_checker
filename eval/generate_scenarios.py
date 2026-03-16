import json
import os

RULES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "checklist", "compliance_rules.json")
SCENARIOS_DIR = os.path.dirname(__file__)

with open(RULES_PATH, 'r') as f:
    RULES = json.load(f)

# Base dictionary mapping rule IDs to a sample text containing their keywords
RULE_TEXTS = {
    "R001": "## Privacy Policy\nThis is a dedicated privacy policy section covering all personal data and data subject rights.",
    "R002": "## Data Retention\nWe have a strict retention period of 7 years to retain data for business needs.",
    "R003": "## Access Control\nWe enforce strict access control using role-based access to ensure proper authorization.",
    "R004": "## GDPR Compliance\nWe strictly comply with the direct General Data Protection regulation and standard GDPR rules.",
    "R005": "## Incident Response\nOur incident response plan outlines immediate breach notification procedures.",
    "R006": "## Audit Logging\nEvery action generates an audit log to maintain a complete audit trail.",
    "R007": "## Employee Training\nAll staff must undergo regular compliance training and security awareness education.",
    "R008": "## Encryption\nAll sensitive information requires TLS encryption and robust cryptography.",
    "R009": "## Consent Mechanism\nUsers must explicitly opt-in via a consent form, forming a binding user agreement.",
    "R010": "## Policy Review\nAn annual review and policy update cycle ensures everything remains current.",
    "R011": "## Vendor Management\nA comprehensive third-party vendor assessment limits supplier risks.",
    "R012": "## Breach Notification\nWe adhere to a mandatory 72 hours notification timeline.",
    "R013": "## Right to Erasure\nUsers can submit a deletion request to exercise their right to be forgotten.",
    "R014": "## Data Minimization\nOnly strictly necessary and minimal data is collected from users.",
    "R015": "## Password Policy\nOur password policy enforces significant length and complexity.",
    "R016": "## MFA Requirement\nWe mandate a multi-factor authentication (MFA) requirement for all users.",
    "R017": "## Vulnerability Management\nWeekly vulnerability scans and penetration testing are part of our process.",
    "R018": "## Business Continuity\nOur business continuity plan (BCP) includes comprehensive disaster recovery protocols.",
    "R019": "## Data Classification\nWe enforce a structured data classification system dividing public and restricted data.",
    "R020": "## Whistleblower Policy\nWe maintain a secure whistleblower hotline for anonymous reporting of misconduct."
}

def build_policy_text(exclude_rules=None):
    if exclude_rules is None:
        exclude_rules = []
    text_blocks = []
    for r_id, p_text in RULE_TEXTS.items():
        if r_id not in exclude_rules:
            text_blocks.append(p_text)
    return "\n\n".join(text_blocks)

scenarios = [
    {
        "id": "01",
        "desc": "Fully compliant policy \u2014 all 20 rules pass",
        "exclude": [],
        "expected_score_min": 95.0,
        "violations_max": 0,
        "grade": "A"
    },
    {
        "id": "02",
        "desc": "Missing data retention clause",
        "exclude": ["R002"],
        "expected_score_min": 90.0,
        "violations_max": 1,
        "grade": "A" # R002 is high, score might be slightly lower
    },
    {
        "id": "03",
        "desc": "Missing privacy policy section",
        "exclude": ["R001"],
        "expected_score_min": 85.0,
        "violations_max": 1,
        "grade": "A"
    },
    {
        "id": "04",
        "desc": "No security controls defined",
        "exclude": ["R003", "R008", "R015", "R016", "R017"],
        "expected_score_min": 70.0,
        "violations_max": 5,
        "grade": "B"
    },
    {
        "id": "05",
        "desc": "Missing GDPR references",
        "exclude": ["R004"],
        "expected_score_min": 90.0,
        "violations_max": 1,
        "grade": "A"
    },
    {
        "id": "06",
        "desc": "No incident response plan",
        "exclude": ["R005", "R012"],
        "expected_score_min": 85.0,
        "violations_max": 2,
        "grade": "A"
    },
    {
        "id": "07",
        "desc": "Missing access control rules",
        "exclude": ["R003"],
        "expected_score_min": 90.0,
        "violations_max": 1,
        "grade": "A"
    },
    {
        "id": "08",
        "desc": "Incomplete audit logging policy",
        "exclude": ["R006"],
        "expected_score_min": 90.0,
        "violations_max": 1,
        "grade": "A"
    },
    {
        "id": "09",
        "desc": "No employee training requirement",
        "exclude": ["R007"],
        "expected_score_min": 90.0,
        "violations_max": 1,
        "grade": "A"
    },
    {
        "id": "10",
        "desc": "Completely non-compliant policy",
        "exclude": list(RULE_TEXTS.keys()),
        "expected_score_min": 0.0,
        "violations_max": 20,
        "grade": "F"
    }
]

os.makedirs(os.path.join(SCENARIOS_DIR, "scenarios"), exist_ok=True)

for sc in scenarios:
    policy_text = build_policy_text(sc["exclude"])
    data = {
        "scenario_id": sc["id"],
        "seed": 42,
        "description": sc["desc"],
        "input": {
            "policy_text": policy_text if policy_text else "This is a generic document with no compliance controls."
        },
        "expected_outcome": {
            "compliance_score_min": sc["expected_score_min"],
            "grade": sc["grade"],
            "risk_level": "Low" if sc["expected_score_min"] >= 80 else ("Medium" if sc["expected_score_min"] >= 60 else ("High" if sc["expected_score_min"] >= 40 else "Critical")),
            "violations_max": sc["violations_max"]
        }
    }
    
    filepath = os.path.join(SCENARIOS_DIR, "scenarios", f"scenario_{sc['id']}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

print(f"Generated {len(scenarios)} scenarios successfully.")
