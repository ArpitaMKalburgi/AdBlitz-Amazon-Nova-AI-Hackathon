import json

from agents._json_utils import parse_json_response
from services.bedrock import call_nova_multimodal

BRAND_SYSTEM_PROMPT = """You are an expert brand strategist and marketing consultant.
You will be given a product photo. Analyze it carefully and create a complete brand brief.

You MUST respond with ONLY valid JSON - no markdown, no explanation, no extra text.

Return this exact JSON structure:
{
    "product_name": "Name of the product",
    "category": "Product category (e.g., Home & Wellness, Fashion, Tech, Food & Beverage)",
    "target_audience": "Primary target audience description",
    "brand_vibe": "2-4 word brand vibe (e.g., calm, minimal, premium)",
    "brand_voice": "2-4 word brand voice (e.g., warm, soft-spoken, aspirational)",
    "color_palette": ["#hex1", "#hex2", "#hex3"],
    "taglines": ["tagline 1", "tagline 2", "tagline 3"],
    "selling_points": ["point 1", "point 2", "point 3"],
    "emotional_angle": "The core emotional appeal (e.g., comfort and self-care)"
}

Rules:
- color_palette: Extract 3 colors from the product image + complementary colors. Use hex codes.
- taglines: Write 3 punchy, memorable taglines. Short and catchy.
- selling_points: Infer 3 key selling points from what you see in the image.
- brand_vibe: Think about what aesthetic this product represents.
- brand_voice: How should ads for this product sound?
- emotional_angle: What feeling should the customer associate with this product?
- target_audience: Be specific - include age range, gender if relevant, lifestyle.

Respond with ONLY the JSON object. Nothing else."""


def run_brand_agent(image_bytes):
    """
    Takes raw image bytes, sends to Nova Lite for brand analysis.
    Returns a parsed Brand Brief dictionary.
    """
    raw_text = call_nova_multimodal(
        prompt="Analyze this product photo and create a complete brand brief.",
        image_base64=image_bytes,
        system_prompt=BRAND_SYSTEM_PROMPT,
        max_tokens=1024,
        temperature=0.7,
    )
    return parse_json_response(raw_text)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python brand_agent.py <image_path>")
        print("Example: python brand_agent.py test_candle.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    with open(image_path, "rb") as file_handle:
        img_bytes = file_handle.read()

    print("Running Brand Agent...")
    result = run_brand_agent(img_bytes)
    print(json.dumps(result, indent=2))
