import json

from agents._json_utils import parse_json_response
from services.bedrock import call_nova_text

AUDIENCE_SYSTEM_PROMPT = """You are an expert audience researcher and consumer psychologist.
You will be given a Brand Brief (JSON). Use it to create 3 detailed customer personas.

You MUST respond with ONLY valid JSON - no markdown, no explanation, no extra text.

Return this exact JSON structure (an array of 3 personas):
[
    {
        "name": "A realistic first name that fits the persona",
        "age": 28,
        "job": "Their job title",
        "income": "$XX,XXX-$XX,XXX",
        "platforms": ["Platform 1", "Platform 2"],
        "active_times": "When they're online (e.g., Evenings 7-10pm, Sunday mornings)",
        "values": ["Value 1", "Value 2", "Value 3"],
        "pain_points": ["Pain point 1", "Pain point 2"],
        "how_they_discover": "How they find new products (e.g., Instagram explore, influencers, Google search)",
        "buying_triggers": ["What makes them buy 1", "What makes them buy 2", "What makes them buy 3"],
        "buying_blockers": ["What stops them from buying 1", "What stops them from buying 2"],
        "best_ad_format": "The best ad format to reach this persona (e.g., Instagram Story + Carousel)"
    }
]

Rules:
- Create exactly 3 personas that are DIFFERENT from each other
- Each persona should represent a distinct segment of the target audience
- Persona 1: The primary buyer (most likely customer)
- Persona 2: The secondary buyer (gift-giver, adjacent audience)
- Persona 3: The aspirational buyer (influenced by trends, social proof)
- Make personas feel like real people - specific ages, real job titles, realistic incomes
- Platforms should match where this type of person actually spends time
- Pain points should be things this product can solve
- Buying triggers and blockers should be realistic and specific
- best_ad_format should match the persona's preferred platforms

Respond with ONLY the JSON array. Nothing else."""


def run_audience_agent(brand_brief):
    """
    Takes a Brand Brief dictionary and returns a list of 3 personas.
    """
    raw_text = call_nova_text(
        prompt=f"Here is the Brand Brief:\n{json.dumps(brand_brief, indent=2)}\n\nCreate 3 detailed customer personas.",
        system_prompt=AUDIENCE_SYSTEM_PROMPT,
        max_tokens=2048,
        temperature=0.7,
    )
    return parse_json_response(raw_text)


if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF

    print("Running Audience Agent with mock brand brief...")
    result = run_audience_agent(MOCK_BRAND_BRIEF)
    print(json.dumps(result, indent=2))
