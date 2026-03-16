import streamlit as st
import json
from agents.base_agent import BaseAgent
from tools.tool_registry import call_tool
from state.state_machine import StateMachine, ComplianceState
from tools.report_generator_tool import ComplianceReport

class ComplianceAgent(BaseAgent):
    def __init__(self, run_id: str, tool_allowlist: list[str], max_steps: int = 20, state_machine: StateMachine = None, rules: list[dict] = None, seed: int = 42):
        super().__init__("compliance_agent", run_id, tool_allowlist, max_steps)
        self.state_machine = state_machine
        self.rules = rules or []
        self.seed = seed
        self.transcript = []

    def _check_stop(self):
        if hasattr(st, "session_state") and st.session_state.get("stop_requested", False):
            self.transcript.append("Human Override: Stop requested.")
            if self.state_machine.get_current() != ComplianceState.DONE.name:
                self.state_machine.transition("reset")
            raise InterruptedError("Run stopped by user.")

    def run(self, input_data: dict) -> dict:
        # Expected input: {"raw_text": str, "document_id": str}
        try:
            self._check_stop()
            
            # Step 1: Parse
            self.log_event("message", {"text": "Starting document parsing."})
            self.transcript.append("Starting document parsing.")
            self.increment_step()
            
            parser_input = {"raw_text": input_data["raw_text"], "document_id": input_data["document_id"]}
            parser_output = call_tool("document_parser_tool", parser_input, run_id=self.run_id, agent=self.agent_name)
            self.state_machine.transition("parse_success")
            
            self._check_stop()
            
            # Step 2: Validate
            self.log_event("message", {"text": "Running compliance validations."})
            self.transcript.append("Running compliance validations.")
            self.increment_step()
            
            engine_input = {
                "document_id": input_data["document_id"],
                "full_text": parser_output["full_text"],
                "rules": self.rules
            }
            engine_output = call_tool("compliance_engine_tool", engine_input, run_id=self.run_id, agent=self.agent_name)
            self.state_machine.transition("validation_complete")
            
            self._check_stop()
            
            # Step 3: Extract Violations (Wait, state should transition to SCORING)
            self.log_event("message", {"text": "Extracting violations."})
            self.transcript.append("Extracting violations.")
            self.increment_step()
            
            extractor_input = {
                "results": engine_output["results"],
                "rules": self.rules
            }
            extractor_output = call_tool("violation_extractor_tool", extractor_input, run_id=self.run_id, agent=self.agent_name)
            
            self._check_stop()
            
            # Step 4: Score Calculator
            self.log_event("message", {"text": "Calculating score."})
            self.transcript.append("Calculating score.")
            self.increment_step()
            
            score_input = {
                "total_rules": engine_output["total_rules"],
                "passed": engine_output["passed"],
                "violations": extractor_output["violations"],
                "rules": self.rules
            }
            score_output = call_tool("score_calculator_tool", score_input, run_id=self.run_id, agent=self.agent_name)
            self.state_machine.transition("score_computed")
            
            self._check_stop()
            
            # Step 5: Report Generator
            self.log_event("message", {"text": "Generating report."})
            self.transcript.append("Generating report.")
            self.increment_step()
            
            report_input = {
                "document_id": input_data["document_id"],
                "compliance_score": score_output["compliance_score"],
                "grade": score_output["grade"],
                "risk_level": score_output["risk_level"],
                "weighted_score": score_output["weighted_score"],
                "total_rules": engine_output["total_rules"],
                "passed": engine_output["passed"],
                "failed": engine_output["failed"],
                "violations": extractor_output["violations"],
                "run_id": self.run_id,
                "seed": self.seed
            }
            report_output = call_tool("report_generator_tool", report_input, run_id=self.run_id, agent=self.agent_name)
            self.state_machine.transition("report_ready")
            
            self.log_event("message", {"text": "Pipeline completed successfully."})
            self.transcript.append("Pipeline completed successfully.")
            return report_output
            
        except Exception as e:
            self.log_event("error", {"error": str(e)})
            self.transcript.append(f"Error: {str(e)}")
            if self.state_machine.get_current() == ComplianceState.PARSING.name:
                self.state_machine.transition("parse_failed")
            elif self.state_machine.get_current() == ComplianceState.VALIDATING.name:
                self.state_machine.transition("validation_failed")
            else:
                pass # Already in error, or can't transition to error from scoring?
            raise
