import json

from agents._json_utils import parse_json_response
from services.bedrock import call_nova_text

AUDIO_SYSTEM_PROMPT = """You are an expert voice director and audio branding specialist.
You will be given a Brand Brief, a voiceover script, and a list of available voices.
Your job is to select the perfect voice for this brand's ad voiceover.

You MUST respond with ONLY valid JSON - no markdown, no explanation, no extra text.

Return this exact JSON structure:
{
    "voice_id": "COPY THE EXACT voice_id STRING FROM THE AVAILABLE VOICES LIST - for Amazon Polly this is usually a voice name like Joanna or Matthew",
    "voice_gender": "male or female",
    "voice_tone": "Describe the tone",
    "voice_pacing": "slow, medium, or fast",
    "voice_energy": "low, medium, or high",
    "voice_style": "2-4 word summary",
    "script_text": "The exact voiceover script text to be spoken.",
    "reasoning": "One sentence explaining why this voice fits the brand"
}

CRITICAL RULES:
- voice_id MUST be copied exactly from the available voices list
- If the available voices list is empty, set voice_id to ""
- Keep script_text short enough to fit in 6 seconds when spoken naturally
- Match voice characteristics to the brand_vibe and brand_voice

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
            "\n\nSelect the perfect voice for this brand. IMPORTANT: voice_id must exactly match one of the IDs in the available voices list."
        ),
        system_prompt=AUDIO_SYSTEM_PROMPT,
        max_tokens=768,
        temperature=0.7,
    )
    return parse_json_response(raw_text)
