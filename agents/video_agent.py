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

VIDEO_SYSTEM_PROMPT = """You are an expert video director and creative strategist for short-form ads.
You will be given a Brand Brief and a TikTok script (from the Copy Agent).
Your job is to write a detailed video generation prompt for an AI video generator (Amazon Nova Reel).

You MUST respond with ONLY valid JSON — no markdown, no explanation, no extra text.

Return this exact JSON structure:
{
    "video_prompt": "A detailed, vivid video generation prompt. 2-4 sentences describing exactly what the video should show: camera movements, subjects, lighting, mood, transitions. Be cinematic and specific.",
    "duration_seconds": 6,
    "text_overlays": [
        {
            "text": "Text to show on screen",
            "time_start": "0s",
            "time_end": "2s",
            "position": "center"
        },
        {
            "text": "Next text overlay",
            "time_start": "3s",
            "time_end": "5s",
            "position": "bottom"
        }
    ],
    "voiceover_script": "The exact words for the voiceover narration. Short, punchy, matches brand voice. Max 2-3 sentences."
}

Rules for video_prompt:
- Describe ONE continuous shot or scene — Nova Reel works best with a single coherent scene
- Include: camera movement (slow zoom, pan, dolly, static), subject action, lighting, mood
- Keep it cinematic and commercial-quality
- Match the brand_vibe from the Brand Brief
- Reference the product naturally in the scene
- Do NOT describe text overlays in the video prompt — those are handled separately
- Duration is always 6 seconds (Nova Reel generates 6-second clips)

Rules for text_overlays:
- 2-3 text overlays max
- Use taglines and CTA from the Brand Brief
- Position: "top", "center", or "bottom"
- These will be added by MoviePy after video generation

Rules for voiceover_script:
- Max 2-3 short sentences that fit in 6 seconds when spoken
- Match the brand_voice (warm, energetic, calm, etc.)
- End with the product name or tagline

Respond with ONLY the JSON object. Nothing else."""


def run_video_agent(brand_brief, tiktok_copy):
    """
    Takes Brand Brief and TikTok copy from Copy Agent.
    Returns video prompt, text overlays, and voiceover script.
    Person 2 will use video_prompt with Nova Reel to generate the video.
    """
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": f"Here is the Brand Brief:\n{json.dumps(brand_brief, indent=2)}\n\nHere is the TikTok script:\n{json.dumps(tiktok_copy, indent=2)}\n\nWrite a video generation prompt and voiceover script for a 6-second ad."
                    }
                ]
            }
        ],
        "system": [
            {
                "text": VIDEO_SYSTEM_PROMPT
            }
        ],
        "inferenceConfig": {
            "maxTokens": 1024,
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

    video_output = json.loads(raw_text)

    return video_output


# --- Test independently ---
if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF, MOCK_COPY

    print("Running Video Agent with mock data...")
    result = run_video_agent(MOCK_BRAND_BRIEF, MOCK_COPY["tiktok"])
    print(json.dumps(result, indent=2))