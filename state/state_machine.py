from enum import Enum
import datetime

class ComplianceState(Enum):
    IDLE = "IDLE"
    PARSING = "PARSING"
    VALIDATING = "VALIDATING"
    SCORING = "SCORING"
    REPORTING = "REPORTING"
    DONE = "DONE"
    ERROR = "ERROR"

TRANSITIONS = {
    (ComplianceState.IDLE, "document_uploaded"): ComplianceState.PARSING,
    (ComplianceState.PARSING, "parse_success"): ComplianceState.VALIDATING,
    (ComplianceState.PARSING, "parse_failed"): ComplianceState.ERROR,
    (ComplianceState.VALIDATING, "validation_complete"): ComplianceState.SCORING,
    (ComplianceState.VALIDATING, "validation_failed"): ComplianceState.ERROR,
    (ComplianceState.SCORING, "score_computed"): ComplianceState.REPORTING,
    (ComplianceState.REPORTING, "report_ready"): ComplianceState.DONE,
    (ComplianceState.ERROR, "reset"): ComplianceState.IDLE,
    (ComplianceState.DONE, "reset"): ComplianceState.IDLE,
}

class StateMachine:
    def __init__(self):
        self._state = ComplianceState.IDLE
        self._history = []

    def transition(self, event: str) -> None:
        key = (self._state, event)
        if key not in TRANSITIONS:
            # Handle invalid transitions by either raising or going to error depending on strictness
            # We'll go to ERROR as a safe fallback or simply raise an exception
            raise ValueError(f"Invalid transition from {self._state.name} with event '{event}'")
            
        next_state = TRANSITIONS[key]
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        self._history.append({
            "previous_state": self._state.name,
            "event": event,
            "next_state": next_state.name,
            "timestamp": timestamp
        })
        
        self._state = next_state

    def get_history(self) -> list[dict]:
        return self._history

    def get_current(self) -> str:
        return self._state.name

    def reset(self) -> None:
        if self._state in [ComplianceState.ERROR, ComplianceState.DONE]:
            self.transition("reset")
        else:
            self._state = ComplianceState.IDLE
            self._history.clear()
