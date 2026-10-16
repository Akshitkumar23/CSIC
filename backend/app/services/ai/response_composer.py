"""Grounded Response Composer Without a Generative Model.

Converts structured DecisionOutput into clear, professional natural-language
Markdown answers using reusable institutional templates with zero hallucinations.
"""
from typing import Any, Dict, List

from backend.app.services.ai.decision_engine import DecisionOutput


class ResponseComposer:
    """Formats deterministic academic facts and calculations into readable Markdown."""

    @staticmethod
    def compose(decision: DecisionOutput) -> str:
        """Assemble structured Markdown response with 6-part grounding."""
        is_hinglish = decision.is_hinglish
        parts: List[str] = []

        # 1. Direct Answer
        parts.append(decision.direct_answer.strip())

        # 2. Verified Facts & Relevant Calculations
        calcs = decision.calculations
        vdata = decision.verified_data

        fact_lines: List[str] = []
        if calcs:
            if "required_consecutive_classes" in calcs and calcs["required_consecutive_classes"] > 0:
                fact_lines.append(f"- **Required Consecutive Classes**: `{calcs['required_consecutive_classes']}` lectures to reach 75%")
            if "safe_bunks" in calcs and calcs["safe_bunks"] > 0:
                fact_lines.append(f"- **Safe Missable Classes**: `{calcs['safe_bunks']}` lectures remaining in buffer")
            if "current_percentage" in calcs:
                fact_lines.append(f"- **Current Attendance Percentage**: `{calcs['current_percentage']:.1f}%`")
            if "overall_percentage" in calcs:
                fact_lines.append(f"- **Overall Aggregate Percentage**: `{calcs['overall_percentage']:.1f}%`")
            if "attended" in calcs and "total" in calcs:
                fact_lines.append(f"- **Attended / Total Sessions**: `{calcs['attended']} / {calcs['total']}`")

        if fact_lines:
            header = "### Verified Facts & Academic Calculations" if not is_hinglish else "### Verified Facts & Calculation (Tathya)"
            parts.append(f"\n{header}\n" + "\n".join(fact_lines))

        # 3. Why It Matters (Official Regulations)
        if decision.why_it_matters:
            header = "### Why This Matters" if not is_hinglish else "### Yeh Kyun Zaroori Hai (Official Policy)"
            parts.append(f"\n{header}\n{decision.why_it_matters}")

        # 4. Practical Next Steps Supported by Rules
        if decision.practical_steps:
            header = "### Practical Next Steps" if not is_hinglish else "### Agle Kadam (Next Steps)"
            step_lines = [f"{idx}. {step}" for idx, step in enumerate(decision.practical_steps, 1)]
            parts.append(f"\n{header}\n" + "\n".join(step_lines))

        # 5. Provenance & Official Source Documents
        if decision.sources:
            header = "### Official Institutional Provenance" if not is_hinglish else "### Official Source & Record"
            source_lines = [f"- 🏛️ {src}" for src in decision.sources]
            parts.append(f"\n{header}\n" + "\n".join(source_lines))

        # 6. Follow-up suggestions
        if decision.follow_up_suggestions:
            pills = " • ".join([f"`{s}`" for s in decision.follow_up_suggestions])
            footer = f"\n*Suggested follow-ups:*\n{pills}"
            parts.append(footer)

        return "\n\n".join(parts)


# Singleton composer instance
response_composer_instance = ResponseComposer()
