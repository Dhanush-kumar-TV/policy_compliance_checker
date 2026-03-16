import json
import os
import datetime

class MaxStepsExceededException(Exception):
    pass

class BaseAgent:
    def __init__(self, agent_name: str, run_id: str, tool_allowlist: list[str], max_steps: int = 20):
        self.agent_name = agent_name
        self.run_id = run_id
        self.tool_allowlist = tool_allowlist
        self.max_steps = max_steps
        self.current_steps = 0

    def run(self, input_data: dict) -> dict:
        raise NotImplementedError("Subclasses must implement run()")

    def log_event(self, event_type: str, data: dict):
        log_file = os.path.join("logs", "runs", f"{self.run_id}.jsonl")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        log_entry = {
            "run_id": self.run_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "agent": self.agent_name,
            "event_type": event_type,
            "data": data
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def increment_step(self):
        self.current_steps += 1
        if self.current_steps > self.max_steps:
            raise MaxStepsExceededException(f"Run exceeded {self.max_steps} steps")
