# orbital-agent/src/compliance_engine/policy_enforcer.py
import logging
import json
from typing import Dict, List, Any, Optional
from jsonpath_ng import parse
import re

logger = logging.getLogger(__name__)

class PolicyViolationError(Exception):
    """Exception raised for policy violations"""

class PolicySyntaxError(Exception):
    """Exception raised for invalid policy syntax"""

class PolicyEnforcer:
    def __init__(self, policy_path: str = None):
        self.policies: List[Dict] = []
        self.compiled_rules = {}
        if policy_path:
            self.load_policies(policy_path)

    def load_policies(self, policy_path: str):
        """Load policies from JSON file"""
        try:
            with open(policy_path, 'r') as f:
                policy_data = json.load(f)
                self._validate_policy_structure(policy_data)
                self.policies = policy_data.get("policies", [])
                self._compile_rules()
                logger.info(f"Loaded {len(self.policies)} policies from {policy_path}")
        except (json.JSONDecodeError, KeyError) as e:
            raise PolicySyntaxError(f"Invalid policy format: {str(e)}")

    def evaluate_request(self, request: Dict) -> Dict:
        """Evaluate request against all loaded policies"""
        violations = []
        results = {"approved": True, "violations": []}

        for policy in self.policies:
            try:
                if not self._check_policy_conditions(policy, request):
                    violation = {
                        "policy_id": policy["id"],
                        "rule": policy["description"],
                        "severity": policy["severity"]
                    }
                    violations.append(violation)
                    logger.warning(f"Policy violation detected: {policy['id']}")
            except Exception as e:
                logger.error(f"Policy evaluation error: {str(e)}")
                raise

        if violations:
            results["approved"] = False
            results["violations"] = violations
            self._execute_remediation_actions(violations, request)

        return results

    def _compile_rules(self):
        """Precompile JSONPath expressions for performance"""
        self.compiled_rules.clear()
        for policy in self.policies:
            for condition in policy.get("conditions", []):
                if "jsonpath" in condition:
                    try:
                        self.compiled_rules[condition["jsonpath"]] = parse(condition["jsonpath"])
                    except Exception:
                        raise PolicySyntaxError(f"Invalid JSONPath: {condition['jsonpath']}")

    def _check_policy_conditions(self, policy: Dict, request: Dict) -> bool:
        """Evaluate all conditions for a single policy"""
        for condition in policy.get("conditions", []):
            if not self._evaluate_condition(condition, request):
                return False
        return True

    def _evaluate_condition(self, condition: Dict, request: Dict) -> bool:
        """Evaluate individual policy condition"""
        condition_type = condition.get("type")
        
        try:
            if condition_type == "jsonpath":
                return self._evaluate_jsonpath(condition, request)
            elif condition_type == "regex":
                return self._evaluate_regex(condition, request)
            elif condition_type == "custom_logic":
                return self._evaluate_custom_logic(condition, request)
            else:
                raise PolicySyntaxError(f"Unknown condition type: {condition_type}")
        except Exception as e:
            logger.error(f"Condition evaluation failed: {str(e)}")
            return False

    def _evaluate_jsonpath(self, condition: Dict, request: Dict) -> bool:
        """Evaluate JSONPath existence or value comparison"""
        jsonpath_expr = self.compiled_rules.get(condition["jsonpath"])
        if not jsonpath_expr:
            return False

        matches = [match.value for match in jsonpath_expr.find(request)]
        operator = condition.get("operator", "exists")
        expected_value = condition.get("value")

        if operator == "exists":
            return len(matches) > 0
        elif operator == "equals":
            return any(str(match) == str(expected_value) for match in matches)
        elif operator == "contains":
            return any(str(expected_value) in str(match) for match in matches)
        else:
            raise PolicySyntaxError(f"Unsupported JSONPath operator: {operator}")

    def _evaluate_regex(self, condition: Dict, request: Dict) -> bool:
        """Evaluate regular expression pattern matching"""
        field_value = request.get(condition["field"], "")
        pattern = condition["pattern"]
        return re.match(pattern, str(field_value)) is not None

    def _evaluate_custom_logic(self, condition: Dict, request: Dict) -> bool:
        """Hook for custom business logic evaluation"""
        # Implementation would connect to external decision service
        # For demonstration purposes, assume custom logic passes
        return True

    def _execute_remediation_actions(self, violations: List, request: Dict):
        """Execute configured remediation steps for violations"""
        for violation in violations:
            severity = violation["severity"]
            if severity == "high":
                logger.critical(f"Critical violation: {violation['policy_id']}")
                # Implementation would trigger incident response workflow
            elif severity == "medium":
                logger.warning(f"Medium severity violation: {violation['policy_id']}")
                # Implementation would queue for review
            else:
                logger.info(f"Low severity violation: {violation['policy_id']}")

    def _validate_policy_structure(self, policy_data: Dict):
        """Validate policy schema structure"""
        required_fields = {"id", "description", "severity", "conditions"}
        for policy in policy_data.get("policies", []):
            missing = required_fields - policy.keys()
            if missing:
                raise PolicySyntaxError(f"Policy missing required fields: {missing}")
