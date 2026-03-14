import json

from agents._json_utils import parse_json_response
from services.bedrock import call_nova_text

MEDIAPLAN_SYSTEM_PROMPT = """You are an expert digital media planner and advertising strategist.
You will be given a Brand Brief, ad copy for 5 platforms, and 3 customer personas.
Use all of this to create a complete 7-day launch strategy.

You MUST respond with ONLY valid JSON - no markdown, no explanation, no extra text.

Return this exact JSON structure:
{
    "budget_split": {
        "instagram": 40,
        "tiktok": 25,
        "google": 20,
        "email": 15
    },
    "daily_budget_recommendation": "$XX-$XX/day for first week",
    "platform_strategy": [
        {
            "platform": "Instagram",
            "creatives": ["carousel", "story", "video"],
            "targeting": "Which persona(s) this targets",
            "why": "One sentence explaining why this platform for this audience"
        }
    ],
    "ab_tests": [
        {
            "test": "What is being tested",
            "variant_a": "Version A text",
            "variant_b": "Version B text",
            "metric": "What metric to track",
            "duration": "How long to run the test",
            "winner_rule": "How to determine the winner"
        }
    ],
    "seven_day_calendar": [
        {
            "day": 1,
            "action": "What to do on this day",
            "platform": "Which platform",
            "budget": "$XX"
        }
    ]
}

Rules:
- budget_split percentages must add up to 100
- platform_strategy should include Instagram, TikTok, Google, and Email
- create exactly 2 meaningful A/B tests
- create exactly 7 calendar entries

Respond with ONLY the JSON object. Nothing else."""


def run_mediaplan_agent(brand_brief, copy_output, personas):
    """
    Takes Brand Brief, copy output, and personas and returns a media plan.
    """
    context = {
        "brand_brief": brand_brief,
        "copy": copy_output,
        "personas": personas,
    }
    raw_text = call_nova_text(
        prompt=f"Here is everything you need:\n{json.dumps(context, indent=2)}\n\nCreate a complete 7-day media launch strategy.",
        system_prompt=MEDIAPLAN_SYSTEM_PROMPT,
        max_tokens=2048,
        temperature=0.7,
    )
    return parse_json_response(raw_text)


if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF, MOCK_COPY, MOCK_PERSONAS

    print("Running Media Plan Agent with mock data...")
    result = run_mediaplan_agent(MOCK_BRAND_BRIEF, MOCK_COPY, MOCK_PERSONAS)
    print(json.dumps(result, indent=2))
