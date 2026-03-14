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

AUDIO_SYSTEM_PROMPT = """You are an expert voice director and audio branding specialist.
You will be given a Brand Brief and a voiceover script.
Your job is to select the perfect voice characteristics for this brand's ad voiceover.

You MUST respond with ONLY valid JSON — no markdown, no explanation, no extra text.

Return this exact JSON structure:
{
    "voice_gender": "male or female",
    "voice_tone": "Describe the tone (e.g., warm, confident, soothing, energetic, friendly)",
    "voice_pacing": "slow, medium, or fast",
    "voice_energy": "low, medium, or high",
    "voice_style": "A 2-4 word summary of the overall voice style (e.g., warm soft female, confident upbeat male)",
    "script_text": "The exact voiceover script text to be spoken. Clean, ready to send to text-to-speech.",
    "reasoning": "One sentence explaining why this voice fits the brand"
}

Rules:
- Match voice characteristics to the brand_vibe and brand_voice from the Brand Brief
- Calm/wellness brands → warm, soft, slow pacing, low energy
- Energetic/fitness brands → confident, upbeat, fast pacing, high energy
- Luxury/premium brands → elegant, measured, medium pacing, medium energy
- Fun/playful brands → friendly, bright, medium-fast pacing, medium-high energy
- Tech/professional brands → clear, authoritative, medium pacing, medium energy
- The script_text should be the final clean version ready for text-to-speech
- Keep script_text short enough to fit in 6 seconds when spoken naturally

Respond with ONLY the JSON object. Nothing else."""


def run_audio_agent(brand_brief, voiceover_script):
    """
    Takes Brand Brief and voiceover script from Video Agent.
    Returns voice selection and final script for Person 2 to send to ElevenLabs.
    """
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": f"Here is the Brand Brief:\n{json.dumps(brand_brief, indent=2)}\n\nHere is the voiceover script:\n\"{voiceover_script}\"\n\nSelect the perfect voice characteristics for this brand."
                    }
                ]
            }
        ],
        "system": [
            {
                "text": AUDIO_SYSTEM_PROMPT
            }
        ],
        "inferenceConfig": {
            "maxTokens": 512,
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

    audio_output = json.loads(raw_text)

    return audio_output


# --- Test independently ---
if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF

    mock_voiceover = "Light up your evening ritual with our Lavender Soy Candle. Pure peace, one flame at a time."

    print("Running Audio Agent with mock data...")
    result = run_audio_agent(MOCK_BRAND_BRIEF, mock_voiceover)
    print(json.dumps(result, indent=2))