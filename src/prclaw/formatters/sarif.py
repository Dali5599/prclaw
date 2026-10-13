"""SARIF Formatter for GitHub Code Scanning."""

import json
from typing import Any, Dict
from prclaw.models import FindingSeverity, ReviewSummary


class SarifFormatter:
    """Exports PRClaw review findings into OASIS SARIF v2.1.0 standard format."""

    SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
    SARIF_VERSION = "2.1.0"

    LEVEL_MAP = {
        FindingSeverity.CRITICAL: "error",
        FindingSeverity.HIGH: "error",
        FindingSeverity.MEDIUM: "warning",
        FindingSeverity.LOW: "note",
        FindingSeverity.INFO: "none",
    }

    def format_sarif(self, summary: ReviewSummary) -> Dict[str, Any]:
        """Convert ReviewSummary into full SARIF dictionary."""
        rules_map = {}
        results = []

        for f in summary.findings:
            if f.rule_id not in rules_map:
                rules_map[f.rule_id] = {
                    "id": f.rule_id,
                    "name": f.rule_id,
                    "shortDescription": {"text": f.message},
                    "defaultConfiguration": {"level": self.LEVEL_MAP.get(f.severity, "warning")},
                }

            result_obj: Dict[str, Any] = {
                "ruleId": f.rule_id,
                "level": self.LEVEL_MAP.get(f.severity, "warning"),
                "message": {"text": f.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": f.file_path},
                            "region": {"startLine": f.line_number or 1},
                        }
                    }
                ],
            }
            results.append(result_obj)

        return {
            "$schema": self.SARIF_SCHEMA,
            "version": self.SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "PRClaw",
                            "version": "0.1.0",
                            "informationUri": "https://github.com/Dali5599/prclaw",
                            "rules": list(rules_map.values()),
                        }
                    },
                    "results": results,
                }
            ],
        }

    def render_json(self, summary: ReviewSummary) -> str:
        """Render SARIF as pretty formatted JSON string."""
        data = self.format_sarif(summary)
        return json.dumps(data, indent=2)
