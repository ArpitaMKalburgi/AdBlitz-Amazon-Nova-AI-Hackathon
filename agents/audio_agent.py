import json

from agents._json_utils import parse_json_response
from services.bedrock import call_nova_text

AUDIO_SYSTEM_PROMPT = """You are an expert voice director and audio branding specialist.
You will be given a Brand Brief, a voiceover script, and a list of available voices.
Your job is to select the perfect voice characteristics and the best matching voice_id.

You MUST respond with ONLY valid JSON - no markdown, no explanation, no extra text.

Return this exact JSON structure:
{
    "voice_id": "The best matching voice ID from the provided list",
    "voice_gender": "male or female",
    "voice_tone": "Describe the tone (e.g., warm, confident, soothing, energetic, friendly)",
    "voice_pacing": "slow, medium, or fast",
    "voice_energy": "low, medium, or high",
    "voice_style": "A 2-4 word summary of the overall voice style",
    "script_text": "The exact voiceover script text to be spoken. Clean, ready to send to text-to-speech.",
    "reasoning": "One sentence explaining why this voice fits the brand"
}

Rules:
- Match voice characteristics to the brand_vibe and brand_voice from the Brand Brief
- Pick voice_id from the available voices list exactly
- Keep script_text short enough to fit in 6 seconds when spoken naturally

Respond with ONLY the JSON object. Nothing else."""


def run_audio_agent(brand_brief, voiceover_script, available_voices=None):
    """
    Takes Brand Brief and voiceover script and returns voice selection details.
    """
    raw_text = call_nova_text(
        prompt=(
            f"Here is the Brand Brief:\n{json.dumps(brand_brief, indent=2)}"
            f"\n\nHere is the voiceover script:\n\"{voiceover_script}\""
            f"\n\nAvailable voices:\n{json.dumps(available_voices or [], indent=2)}"
            "\n\nSelect the perfect voice characteristics for this brand."
        ),
        system_prompt=AUDIO_SYSTEM_PROMPT,
        max_tokens=768,
        temperature=0.7,
    )
    return parse_json_response(raw_text)


if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF

    mock_voiceover = "Light up your evening ritual with our Lavender Soy Candle. Pure peace, one flame at a time."

    print("Running Audio Agent with mock data...")
    result = run_audio_agent(MOCK_BRAND_BRIEF, mock_voiceover, [])
    print(json.dumps(result, indent=2))
