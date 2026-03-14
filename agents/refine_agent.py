import json

from agents._json_utils import parse_json_response
from services.bedrock import call_nova_text

REFINE_SYSTEM_PROMPT = """You are an expert campaign manager who reviews ad campaigns and determines what needs to change based on user feedback.

You will be given:
1. The current full campaign output
2. User feedback in plain English

Your job is to determine which agents need to re-run and what changes to make.

You MUST respond with ONLY valid JSON - no markdown, no explanation, no extra text.

Return this exact JSON structure:
{
    "agents_to_rerun": ["brand_agent", "copy_agent"],
    "changes": [
        {
            "agent": "brand_agent",
            "instruction": "Specific instruction for what this agent should change. Be precise."
        }
    ],
    "reasoning": "One sentence explaining your decision"
}

Valid agent names: brand_agent, copy_agent, audience_agent, mediaplan_agent, visual_agent, video_agent, audio_agent

Respond with ONLY the JSON object. Nothing else."""


def run_refine_agent(feedback, current_campaign):
    """
    Takes user feedback and current campaign output.
    Returns which agents need to re-run and what should change.
    """
    raw_text = call_nova_text(
        prompt=(
            f"Here is the current campaign:\n{json.dumps(current_campaign, indent=2)}"
            f"\n\nUser feedback: \"{feedback}\""
            "\n\nWhich agents need to re-run and what should change?"
        ),
        system_prompt=REFINE_SYSTEM_PROMPT,
        max_tokens=1024,
        temperature=0.5,
    )
    return parse_json_response(raw_text)


if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF, MOCK_COPY, MOCK_PERSONAS, MOCK_MEDIA_PLAN

    mock_campaign = {
        "brand_brief": MOCK_BRAND_BRIEF,
        "copy": MOCK_COPY,
        "personas": MOCK_PERSONAS,
        "media_plan": MOCK_MEDIA_PLAN,
    }

    feedback = "Make the copy more playful and fun"

    print(f"Running Refine Agent with feedback: '{feedback}'...")
    result = run_refine_agent(feedback, mock_campaign)
    print(json.dumps(result, indent=2))
