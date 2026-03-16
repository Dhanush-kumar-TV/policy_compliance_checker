import json
import os
import datetime
import concurrent.futures
from pydantic import ValidationError

from tools.document_parser_tool import parse_document
from tools.compliance_engine_tool import run_compliance_check
from tools.violation_extractor_tool import extract_violations
from tools.score_calculator_tool import calculate_score
from tools.report_generator_tool import generate_report

TOOL_ALLOWLIST = [
    "document_parser_tool",
    "compliance_engine_tool",
    "violation_extractor_tool",
    "score_calculator_tool",
    "report_generator_tool"
]

TOOL_FUNCTIONS = {
    "document_parser_tool": parse_document,
    "compliance_engine_tool": run_compliance_check,
    "violation_extractor_tool": extract_violations,
    "score_calculator_tool": calculate_score,
    "report_generator_tool": generate_report
}

class ToolNotAllowedException(Exception):
    pass

class ToolExecutionException(Exception):
    pass

def log_tool_io(run_id: str, agent: str, tool_name: str, input_data: dict, output_data: dict | None, duration_ms: float, error: str | None = None):
    # Log to logs/runs/{run_id}.jsonl
    log_file = os.path.join("logs", "runs", f"{run_id}.jsonl")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    log_entry = {
        "run_id": run_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "agent": agent,
        "event_type": "tool_call" if error is None else "error",
        "data": {
            "tool_name": tool_name,
            "input": input_data,
            "output": output_data,
            "duration_ms": duration_ms
        }
    }
    
    if error:
        log_entry["data"]["error"] = error

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def call_tool(name: str, input_data: dict, timeout: int = 10, run_id: str = "default", agent: str = "system") -> dict:
    if name not in TOOL_ALLOWLIST:
        raise ToolNotAllowedException(f"{name} is not an approved tool")
        
    tool_fn = TOOL_FUNCTIONS.get(name)
    if not tool_fn:
        raise ToolExecutionException(f"Function implementation for {name} missing")
        
    start_time = datetime.datetime.now()
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(tool_fn, input_data)
            result = future.result(timeout=timeout)
            
        duration_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
        log_tool_io(run_id, agent, name, input_data, result, duration_ms)
        return result
        
    except concurrent.futures.TimeoutError:
        duration_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
        error_msg = f"Tool {name} timed out after {timeout} seconds"
        log_tool_io(run_id, agent, name, input_data, None, duration_ms, error=error_msg)
        raise ToolExecutionException(error_msg)
        
    except ValidationError as e:
        duration_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
        error_msg = f"Output Schema Validation Error: {str(e)}"
        log_tool_io(run_id, agent, name, input_data, None, duration_ms, error=error_msg)
        raise
        
    except Exception as e:
        duration_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
        error_msg = str(e)
        log_tool_io(run_id, agent, name, input_data, None, duration_ms, error=error_msg)
        raise ToolExecutionException(f"Error executing {name}: {error_msg}")
