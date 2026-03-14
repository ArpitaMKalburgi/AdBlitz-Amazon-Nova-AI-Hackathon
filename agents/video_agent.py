import json

from agents._json_utils import parse_json_response
from services.bedrock import call_nova_text

VIDEO_SYSTEM_PROMPT = """You are an expert video director and creative strategist for short-form ads.
You will be given a Brand Brief and a TikTok script (from the Copy Agent).
Your job is to write a detailed video generation prompt for an AI video generator (Amazon Nova Reel).

You MUST respond with ONLY valid JSON - no markdown, no explanation, no extra text.

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

Rules:
- Describe one continuous shot or scene
- Include camera movement, subject action, lighting, and mood
- Keep it cinematic and commercial-quality
- Match the brand_vibe from the Brand Brief
- Do NOT describe text overlays in the video prompt
- Duration is always 6 seconds
- Use 2-3 text overlays max
- Voiceover should fit naturally in 6 seconds

Respond with ONLY the JSON object. Nothing else."""


def run_video_agent(brand_brief, tiktok_copy):
    """
    Takes Brand Brief and TikTok copy and returns video prompt details.
    """
    raw_text = call_nova_text(
        prompt=(
            f"Here is the Brand Brief:\n{json.dumps(brand_brief, indent=2)}"
            f"\n\nHere is the TikTok script:\n{json.dumps(tiktok_copy, indent=2)}"
            "\n\nWrite a video generation prompt and voiceover script for a 6-second ad."
        ),
        system_prompt=VIDEO_SYSTEM_PROMPT,
        max_tokens=1024,
        temperature=0.7,
    )
    return parse_json_response(raw_text)


if __name__ == "__main__":
    from mock_data import MOCK_BRAND_BRIEF, MOCK_COPY

    print("Running Video Agent with mock data...")
    result = run_video_agent(MOCK_BRAND_BRIEF, MOCK_COPY["tiktok"])
    print(json.dumps(result, indent=2))
