import streamlit as st
from agents.base_agent import BaseAgent

class ViolationAgent(BaseAgent):
    def __init__(self, run_id: str, tool_allowlist: list[str], max_steps: int = 10):
        super().__init__("violation_agent", run_id, tool_allowlist, max_steps)
        self.transcript = []

    def _check_stop(self):
        if hasattr(st, "session_state") and st.session_state.get("stop_requested", False):
            self.transcript.append("Human Override: Stop requested.")
            raise InterruptedError("Run stopped by user.")

    def run(self, input_data: dict) -> dict:
        self._check_stop()
        
        self.log_event("message", {"text": "Starting violation enrichment."})
        self.transcript.append("Starting violation enrichment.")
        self.increment_step()
        
        violations = input_data.get("violations", [])
        enriched_violations = []
        
        for v in violations:
            self._check_stop()
            
            # Since LLM API is local execution only and simulating, generate a contextual fix logic:
            fix = f"[TEMPLATED LLM REMEDIATION] To fully resolve this {v['severity']} violation ({v['rule_id']}), you must integrate the standard operating procedure: {v['remediation']}"
            
            # Simple simulation of model processing delay can be done if desired
            v_enriched = dict(v)
            v_enriched["suggested_fix"] = fix
            enriched_violations.append(v_enriched)
            
            self.log_event("message", {"text": f"Enriched violation {v['rule_id']}."})
            self.transcript.append(f"Enriched violation {v['rule_id']} automatically.")
            
        self.log_event("message", {"text": "Finished violation enrichment."})
        self.transcript.append("Finished violation enrichment.")
        
        return {"enriched_violations": enriched_violations}
