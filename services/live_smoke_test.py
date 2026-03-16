import base64
import json
from pprint import pprint

from agents.orchestrator import generate_campaign
from services.polly import generate_voiceover, list_voices
from services.moviepy_processor import add_text_overlay, merge_audio_video
from services._common import build_aws_client, get_setting
from services.nova_canvas import generate_image
from services.nova_reel import generate_video
from services.s3 import read_file_bytes


def _pick_voice_id() -> str:
    from services._common import get_setting

    configured_voice_id = get_setting("POLLY_VOICE_ID", default=get_setting("ELEVENLABS_VOICE_ID"))
    if configured_voice_id:
        return configured_voice_id

    voices = list_voices()
    if not voices:
        raise RuntimeError("No Amazon Polly voices available for this configuration.")

    preferred_names = {"joanna", "matthew", "danielle", "gregory", "ruth", "stephen"}
    for voice in voices:
        if voice.get("name", "").strip().lower() in preferred_names:
            return voice["voice_id"]

    return voices[0]["voice_id"]


def _generate_seed_image_bytes():
    client = build_aws_client("bedrock-runtime", read_timeout=3600)
    prompt = (
        "Premium lavender soy candle in a frosted glass jar on a minimalist wooden tray, "
        "soft warm bedroom lighting, calm luxury wellness aesthetic, photorealistic product photo"
    )
    request_body = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "quality": "standard",
            "width": 1280,
            "height": 720,
            "seed": 42,
            "cfgScale": 8.0,
        },
    }
    response = client.invoke_model(
        modelId=get_setting("NOVA_CANVAS_MODEL_ID", default="amazon.nova-canvas-v1:0"),
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json",
    )
    response_body = json.loads(response["body"].read())
    images = response_body.get("images") or []
    if not images:
        raise RuntimeError(f"Nova Canvas did not return image bytes: {response_body}")
    return base64.b64decode(images[0])


def run_live_smoke_test():
    results = {"checks": {}, "artifacts": {}, "errors": {}}
    sts_client = build_aws_client("sts")
    caller_identity = sts_client.get_caller_identity()
    print(f"0. Caller identity: {caller_identity['Arn']}")
    results["checks"]["caller_identity"] = caller_identity["Arn"]

    print("1. Generating seed product image bytes with Nova Canvas...")
    seed_image_bytes = _generate_seed_image_bytes()
    results["checks"]["seed_image_bytes"] = len(seed_image_bytes)
    print(f"   Seed image bytes: {len(seed_image_bytes)}")

    print("2. Running orchestrator against the seed image...")
    campaign = generate_campaign(seed_image_bytes, status_callback=lambda message: print(f"   {message}"))
    results["checks"]["orchestrator"] = "ok"

    print("3. Campaign summary:")
    summary = {
        "brand_product_name": campaign.get("brand_brief", {}).get("product_name"),
        "copy_keys": list(campaign.get("copy", {}).keys()),
        "persona_count": len(campaign.get("personas", [])),
        "visual_prompt_count": len(campaign.get("images", [])),
        "video_fields": list(campaign.get("video", {}).keys()),
        "audio_fields": list(campaign.get("audio", {}).keys()),
    }
    pprint(summary)
    results["checks"]["campaign_summary"] = summary

    visual_prompts = campaign.get("images", [])
    if not visual_prompts:
        raise RuntimeError("Visual Agent returned no prompts.")

    print("4. Generating one real campaign image from the first visual prompt...")
    try:
        campaign_image_url = generate_image(
            visual_prompts[0]["prompt"],
            width=1024,
            height=1024,
            quality="standard",
        )
        print(f"   Campaign image: {campaign_image_url}")
        results["artifacts"]["campaign_image_url"] = campaign_image_url
    except Exception as exc:
        print(f"   Campaign image generation/upload failed: {exc}")
        results["errors"]["campaign_image"] = str(exc)

    print("5. Generating voiceover with Amazon Polly...")
    try:
        voice_id = _pick_voice_id()
        results["checks"]["voice_id"] = voice_id
        voice_script = (
            campaign.get("audio", {}).get("script_text")
            or campaign.get("video", {}).get("voiceover_script")
            or campaign.get("brand_brief", {}).get("product_name", "AdBlitz demo")
        )
        audio_url = generate_voiceover(voice_script, voice_id=voice_id)
        print(f"   Voiceover: {audio_url}")
        results["artifacts"]["audio_url"] = audio_url
    except Exception as exc:
        print(f"   Voiceover generation/upload failed: {exc}")
        results["errors"]["audio"] = str(exc)

    print("6. Generating Nova Reel video...")
    try:
        image_base64 = base64.b64encode(seed_image_bytes).decode("utf-8")
        video_prompt = campaign.get("video", {}).get("video_prompt")
        if not video_prompt:
            raise RuntimeError("Video Agent returned no video prompt.")
        raw_video_url = generate_video(image_base64, video_prompt, duration_seconds=6)
        print(f"   Raw video: {raw_video_url}")
        results["artifacts"]["raw_video_url"] = raw_video_url
    except Exception as exc:
        raw_video_url = None
        print(f"   Nova Reel generation failed: {exc}")
        results["errors"]["video"] = str(exc)

    print("7. Adding text overlays...")
    try:
        text_overlays = campaign.get("video", {}).get("text_overlays", [])
        video_with_text_url = add_text_overlay(raw_video_url, text_overlays) if raw_video_url and text_overlays else raw_video_url
        print(f"   Video with text: {video_with_text_url}")
        results["artifacts"]["video_with_text_url"] = video_with_text_url
    except Exception as exc:
        video_with_text_url = raw_video_url
        print(f"   Text overlay step failed: {exc}")
        results["errors"]["text_overlay"] = str(exc)

    print("8. Merging audio and video...")
    try:
        audio_url = results["artifacts"].get("audio_url")
        final_video_url = (
            merge_audio_video(video_with_text_url, audio_url)
            if video_with_text_url and audio_url
            else None
        )
        print(f"   Final video: {final_video_url}")
        results["artifacts"]["final_video_url"] = final_video_url
    except Exception as exc:
        print(f"   Audio/video merge failed: {exc}")
        results["errors"]["final_video"] = str(exc)

    result = {"results": results, "campaign": campaign}

    print("9. Done.")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run_live_smoke_test()
