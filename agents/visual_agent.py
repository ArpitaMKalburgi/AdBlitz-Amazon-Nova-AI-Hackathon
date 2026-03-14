import json

from agents._json_utils import parse_json_response
from services.bedrock import call_nova_text

VISUAL_SYSTEM_PROMPT = """You are an expert art director and visual marketing specialist.
You will be given a Brand Brief (JSON). Use it to write detailed image generation prompts
for an AI image generator (Amazon Nova Canvas).

You MUST respond with ONLY valid JSON - no markdown, no explanation, no extra text.

Return this exact JSON structure (an array of image objects):
[
    {
        "prompt": "A detailed, vivid image generation prompt. Include: subject, setting, lighting, mood, camera angle, style. Be very specific.",
        "format": "lifestyle",
        "platform": "instagram",
        "description": "Short human-readable description of what this image shows"
    },
    {
        "prompt": "...",
        "format": "hero",
        "platform": "all",
        "description": "..."
    },
    {
        "prompt": "...",
        "format": "carousel",
        "platform": "instagram",
        "description": "..."
    },
    {
        "prompt": "...",
        "format": "carousel",
        "platform": "instagram",
        "description": "..."
    },
    {
        "prompt": "...",
        "format": "carousel",
        "platform": "instagram",
        "description": "..."
    },
    {
        "prompt": "...",
        "format": "story",
        "platform": "instagram",
        "description": "..."
    }
]

Create exactly 6 images:
1. Lifestyle image in a real-world setting that matches the brand vibe.
2. Product hero shot on a branded background using colors from the color_palette.
3. Carousel slide 1 showing the pain point the product solves.
4. Carousel slide 2 showing the product as the solution.
5. Carousel slide 3 showing social proof cues.
6. Story format image in vertical 9:16 composition.

Rules for prompts:
- Each prompt must be 2-4 sentences and highly descriptive
- Include lighting direction, camera angle, and mood
- Use colors from the brand's color_palette
- Match the brand_vibe in every prompt
- Do NOT include text in the prompt itself
- Focus on photorealistic, commercial-quality imagery

Respond with ONLY the JSON array. Nothing else."""


def run_visual_agent(brand_brief):
    """
    Takes a Brand Brief dictionary and returns image prompt objects.
    """
    raw_text = call_nova_text(
        prompt=(
            f"Here is the Brand Brief:\n{json.dumps(brand_brief, indent=2)}"
            "\n\nWrite 6 detailed image generation prompts for this product's ad campaign."
        ),
        system_prompt=VISUAL_SYSTEM_PROMPT,
        max_tokens=2048,
        temperature=0.7,
    )
    return parse_json_response(raw_text)


if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF

    print("Running Visual Agent with mock brand brief...")
    result = run_visual_agent(MOCK_BRAND_BRIEF)
    print(json.dumps(result, indent=2))
