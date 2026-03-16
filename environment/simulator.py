import random
import uuid

# A bank of predefined policy paragraphs covering various compliance topics
POLICY_BANK = [
    {
        "section": "Data Privacy",
        "content": "This Privacy Policy Section outlines our commitment to protecting personal data. We ensure that every data subject is informed about how their data is collected, used, and stored. We adhere to the fundamental principles of privacy and ensure rights are respected."
    },
    {
        "section": "Data Retention",
        "content": "Our data retention framework is designed to store personal records only as long as required. The standard retention period for user data is 7 years, after which it will be permanently deleted. This storage duration aligns with local tax and legal obligations."
    },
    {
        "section": "Security Controls",
        "content": "A stringent access control policy is in place for all internal systems. We utilize role-based access control (RBAC) to ensure authorization is provided only to the personnel who require access. All access logs are monitored."
    },
    {
        "section": "Compliance",
        "content": "We are fully committed to GDPR compliance. The General Data Protection regulation governs our operations in the European Union and we have dedicated staff to oversee full alignment. All data subject requests will be processed promptly."
    },
    {
        "section": "Incident Response",
        "content": "In the event of a security breach, our Incident Response Plan will be immediately activated. A breach notification will be sent to the affected users without undue delay, outlining the nature of the security incident and mitigation steps taken."
    },
    {
        "section": "Audit and Logging",
        "content": "Our systems enforce a strict audit logging requirement. Every system access, configuration change, and data export is tracked. The audit trail is securely stored and maintained for forensic analysis when needed."
    },
    {
        "section": "Employee Training",
        "content": "All employees must undergo an annual compliance training requirement. This employee education program covers cybersecurity, data protection, and operational security to raise awareness across the organization."
    },
    {
        "section": "Data Encryption",
        "content": "A definitive encryption policy is established to safeguard sensitive information. All data at rest must be encrypted using AES-256, and data in transit must utilize TLS 1.3 to ensure robust cryptography standards."
    },
    {
        "section": "User Consent",
        "content": "We employ a clear consent mechanism for any marketing communications. Users must explicitly opt-in via a user agreement. They can easily opt-out at any time through their account settings."
    },
    {
        "section": "Governance Review",
        "content": "This document undergoes a regular policy review cycle. The compliance team conducts an annual review to evaluate the effectiveness of the policy and issue a formal policy update or revision if regulatory conditions change."
    },
    {
        "section": "Third-Party Management",
        "content": "We hold our partners to high standards through our third-party vendor management program. Every supplier and subcontractor must pass a security assessment before they are granted access to our environment."
    },
    {
        "section": "Breach Response Timeline",
        "content": "In accordance with legal obligations, we commit to a strict notification timeline. We will report to the supervisory authority within 72 hours of becoming aware of any significant data breach."
    },
    {
        "section": "Erasure Rights",
        "content": "We respect your right to erasure. Any user can submit a deletion request to exercise their right to be forgotten. Upon verification, all non-essential personal data will be purged from our active systems."
    },
    {
        "section": "Data Minimization",
        "content": "Our engineering practices follow the rule of data minimization. We collect only the minimal data that is strictly necessary to provide the requested service and discard any superfluous context."
    },
    {
        "section": "Authentication Policy",
        "content": "We enforce a comprehensive password policy requiring significant length and complexity. We also mandate a strict MFA requirement. Multi-factor authentication (2FA) is enabled by default for all privileged administrative accounts."
    },
    {
        "section": "Vulnerability Testing",
        "content": "We maintain an active vulnerability management process. Regular penetration testing and a formal patch management program are established to identify and remediate weaknesses in our external footprint."
    },
    {
        "section": "Business Continuity",
        "content": "Our organization has developed a comprehensive business continuity plan (BCP). This disaster recovery framework ensures that we can quickly restore operations following any major service disruption."
    },
    {
        "section": "Information Classification",
        "content": "All information assets follow our strict data classification schema. Documents are assigned varying levels of protection, such as public, internal, confidential, or highly restricted."
    },
    {
        "section": "Whistleblower Protection",
        "content": "We operate a formal whistleblower policy. We encourage staff to report misconduct through an anonymous reporting hotline. The organization strictly forbids retaliation against any individual who reports a compliance concern in good faith."
    }
]

def generate_policy(seed: int) -> dict:
    """
    Deterministically generates a policy document based on the given seed.
    """
    random.seed(seed)
    # Pick a random number of sections between 5 and 19 to simulate
    # different levels of compliance
    num_sections = random.randint(5, len(POLICY_BANK))
    
    # Randomly select the sections
    selected_paragraphs = random.sample(POLICY_BANK, num_sections)
    
    document_id = str(uuid.UUID(int=random.getrandbits(128), version=4))
    title = f"Corporate Information Security and Compliance Policy (Gen-{seed})"
    
    sections = []
    content_parts = []
    
    for para in selected_paragraphs:
        sections.append(para["section"])
        content_parts.append(f"## {para['section']}\n{para['content']}")
    
    content = "\n\n".join(content_parts)
    
    return {
        "document_id": document_id,
        "title": title,
        "content": content,
        "sections": sections,
        "seed": seed
    }
