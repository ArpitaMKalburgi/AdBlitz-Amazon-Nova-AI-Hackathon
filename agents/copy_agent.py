import json
import boto3
import streamlit as st

# Initialize Bedrock client
bedrock = boto3.client(
    "bedrock-runtime",
    region_name=st.secrets["AWS_REGION"],
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
)

COPY_SYSTEM_PROMPT = """You are an elite advertising copywriter who writes for top brands.
You will be given a Brand Brief (JSON). Use it to write ad copy for 5 platforms.

You MUST respond with ONLY valid JSON — no markdown, no explanation, no extra text.

Return this exact JSON structure:
{
    "instagram": {
        "hook": "First line that appears before 'more' (max 125 chars, punchy, stops the scroll)",
        "body": "3-4 lines of emotional, lifestyle-focused copy",
        "cta": "Clear call to action",
        "hashtags": ["#relevant", "#hashtags", "#15to20of them"]
    },
    "facebook": {
        "primary_text": "Short punchy text (max 125 chars)",
        "headline": "Product name + key benefit",
        "description": "One-line description",
        "cta": "Shop Now / Learn More / etc.",
        "long_body": "3-5 sentences. Storytelling approach. Emotional. Ends with CTA."
    },
    "google": {
        "headlines": ["Headline 1 (max 30 chars)", "Headline 2 (max 30 chars)", "Headline 3 (max 30 chars)"],
        "descriptions": ["Description 1 (max 90 chars)", "Description 2 (max 90 chars)"],
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8", "keyword9", "keyword10"]
    },
    "tiktok": {
        "hook": "First 2 seconds — must stop the scroll (short, punchy, curiosity-driven)",
        "scenes": [
            {"time": "0-2s", "action": "Hook text on screen, product in background"},
            {"time": "2-5s", "action": "Describe what happens visually"},
            {"time": "5-10s", "action": "Product reveal or demo moment"},
            {"time": "10-13s", "action": "Benefit or lifestyle shot"},
            {"time": "13-15s", "action": "CTA with product shot and tagline"}
        ],
        "cta": "Clear CTA for TikTok",
        "suggested_audio": "Describe the type of audio/music that fits the brand vibe"
    },
    "email": {
        "subject_lines": ["Subject 1 (curiosity-driven)", "Subject 2 (benefit-driven)", "Subject 3 (urgency-driven)"],
        "preview_text": "Preview text that appears after subject line (max 90 chars)",
        "body": "Full email body. Greeting, 2-3 short paragraphs, CTA, sign-off. Use \\n for line breaks."
    }
}

Rules:
- Match the brand_voice and brand_vibe from the brief in ALL copy
- Instagram: emotional, visual language, lots of hashtags
- Facebook: storytelling, longer form, benefit-focused
- Google: strict character limits, keyword-rich, search-intent focused
- TikTok: fast-paced, trend-aware, hook in first 2 seconds, scene-by-scene script with timings
- Email: personal, warm, one clear CTA, feels like a friend writing
- Use the taglines and selling points from the brand brief naturally
- All copy should feel human, not AI-generated

Respond with ONLY the JSON object. Nothing else."""


def run_copy_agent(brand_brief):
    """
    Takes a Brand Brief dictionary, sends to Nova Lite.
    Returns ad copy for all 5 platforms as a dictionary.
    """
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": f"Here is the Brand Brief:\n{json.dumps(brand_brief, indent=2)}\n\nWrite ad copy for all 5 platforms."
                    }
                ]
            }
        ],
        "system": [
            {
                "text": COPY_SYSTEM_PROMPT
            }
        ],
        "inferenceConfig": {
            "maxTokens": 2048,
            "temperature": 0.7
        }
    }

    response = bedrock.invoke_model(
        modelId=st.secrets["BEDROCK_MODEL_ID"],
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    raw_text = response_body["output"]["message"]["content"][0]["text"]

    # Clean up response
    raw_text = raw_text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()

    copy_output = json.loads(raw_text)

    return copy_output


# --- Test independently ---
if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF

    print("Running Copy Agent with mock brand brief...")
    result = run_copy_agent(MOCK_BRAND_BRIEF)
    print(json.dumps(result, indent=2))