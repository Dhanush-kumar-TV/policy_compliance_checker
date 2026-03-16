import streamlit as st
import datetime
from agents.compliance_agent import ComplianceAgent
from agents.violation_agent import ViolationAgent
from state.state_machine import StateMachine, ComplianceState

class Orchestrator:
    def __init__(self, run_id: str, state_machine: StateMachine, tool_allowlist: list[str], rules: list[dict], seed: int = 42):
        self.run_id = run_id
        self.state_machine = state_machine
        self.tool_allowlist = tool_allowlist
        self.rules = rules
        self.seed = seed
        self.compliance_agent = ComplianceAgent(run_id, tool_allowlist, state_machine=state_machine, rules=rules, seed=seed)
        self.violation_agent = ViolationAgent(run_id, tool_allowlist)
        self.transcript = []

    def _check_stop(self):
        if hasattr(st, "session_state") and st.session_state.get("stop_requested", False):
            self.transcript.append("Human Override: Stop requested by user.")
            raise InterruptedError("Run stopped by user.")

    def run(self, input_data: dict) -> dict:
        self.transcript.append("Orchestrator: Starting multi-agent pipeline.")
        
        # 1. Hand policy to compliance_agent
        self.transcript.append("Orchestrator: Handing off to compliance_agent.")
        report_output = self.compliance_agent.run(input_data)
        self.transcript.extend(self.compliance_agent.transcript)
        
        self._check_stop()
        
        # Check if there are violations
        total_violations = []
        for cat, v_list in report_output.get("violations_by_category", {}).items():
            total_violations.extend(v_list)
            
        # 2. If violations exist, hand to violation_agent
        if total_violations:
            self.transcript.append("Orchestrator ──→ violation_agent: Violations detected, requesting enrichment.")
            
            enrichment_result = self.violation_agent.run({"violations": total_violations})
            self.transcript.extend(self.violation_agent.transcript)
            enriched_violations = enrichment_result.get("enriched_violations", [])
            
            # 3. Merge results
            self.transcript.append("Orchestrator: Merging enriched violations into final report.")
            
            # Re-group enriched violations
            from collections import defaultdict
            merged_by_category = defaultdict(list)
            critical_actions = []
            
            for v in enriched_violations:
                merged_by_category[v["category"]].append(v)
                if v["severity"].lower() == "critical":
                    action = f"[{v['rule_id']}] {v['remediation']}"
                    if v.get("suggested_fix"):
                        action += f" (Fix: {v['suggested_fix']})"
                    critical_actions.append(action)
                    
            report_output["violations_by_category"] = dict(merged_by_category)
            report_output["top_3_critical_actions"] = critical_actions[:3]
            
        else:
            self.transcript.append("Orchestrator: No violations detected. Bypassing violation_agent.")
            
        self.transcript.append("Orchestrator: Pipeline complete.")
        return report_output
