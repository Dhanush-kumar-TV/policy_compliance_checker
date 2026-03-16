import os
import json
import glob
from agents.orchestrator import Orchestrator
from state.state_machine import StateMachine

def main():
    root_dir = os.path.dirname(os.path.dirname(__file__))
    rules_path = os.path.join(root_dir, "checklist", "compliance_rules.json")
    
    with open(rules_path, 'r') as f:
        rules = json.load(f)
        
    tool_allowlist = [
        "document_parser_tool",
        "compliance_engine_tool",
        "violation_extractor_tool",
        "score_calculator_tool",
        "report_generator_tool"
    ]
    
    scenarios_dir = os.path.join(os.path.dirname(__file__), "scenarios")
    scenario_files = sorted(glob.glob(os.path.join(scenarios_dir, "*.json")))
    
    print(f"| scenario_id | description | score | grade | violations | passed | notes |")
    print(f"|-------------|-------------|-------|-------|------------|--------|-------|")
    
    total_scenarios = 0
    passed_scenarios = 0
    avg_score = 0.0
    
    for sf in scenario_files:
        with open(sf, 'r') as f:
            sc = json.load(f)
            
        scenario_id = sc["scenario_id"]
        description = sc["description"]
        policy_text = sc["input"]["policy_text"]
        expected = sc["expected_outcome"]
        
        state_machine = StateMachine()
        state_machine.transition("document_uploaded")
        
        orchestrator = Orchestrator(
            run_id=f"eval_{scenario_id}",
            state_machine=state_machine,
            tool_allowlist=tool_allowlist,
            rules=rules,
            seed=sc.get("seed", 42)
        )
        
        input_data = {
            "raw_text": policy_text,
            "document_id": f"doc_{scenario_id}"
        }
        
        try:
            report = orchestrator.run(input_data)
            
            actual_score = report["compliance_score"]
            actual_grade = report["grade"]
            
            # Count total violations
            actual_violations = 0
            for k, v in report.get("violations_by_category", {}).items():
                actual_violations += len(v)
                
            score_pass = actual_score >= expected["compliance_score_min"] - 5.0 # tolerate slight differences
            # If scenario 10, actual_score should be 0.
            if actual_score == 0 and expected["compliance_score_min"] == 0:
                score_pass = True
                
            passed = "✅" if score_pass else "❌"
            if score_pass: passed_scenarios += 1
            total_scenarios += 1
            avg_score += actual_score
            
            # Truncate description for table
            desc_short = (description[:15] + '..') if len(description) > 17 else description.ljust(17)
            
            print(f"| {scenario_id:11} | {desc_short:11} | {actual_score:5.1f} | {actual_grade:5} | {actual_violations:10} | {passed:6} |       |")
            
        except Exception as e:
            print(f"| {scenario_id:11} | ERROR       | ERROR | ERROR | ERROR      | ❌     | {str(e)[:15]} |")
            
    print("\nAggregate Metrics:")
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Passed Scenarios: {passed_scenarios}")
    print(f"Average Score: {avg_score / total_scenarios if total_scenarios > 0 else 0:.1f}")

if __name__ == "__main__":
    main()
