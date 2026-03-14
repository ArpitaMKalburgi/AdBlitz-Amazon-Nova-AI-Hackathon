import json

from agents.audio_agent import run_audio_agent
from agents.audience_agent import run_audience_agent
from agents.brand_agent import run_brand_agent
from agents.copy_agent import run_copy_agent
from agents.mediaplan_agent import run_mediaplan_agent
from agents.refine_agent import run_refine_agent
from agents.video_agent import run_video_agent
from agents.visual_agent import run_visual_agent
from services._common import get_setting
from services.elevenlabs import generate_voiceover, list_voices
from services.moviepy_processor import add_text_overlay, merge_audio_video
from services.nova_canvas import generate_image
from services.nova_reel import generate_video


def _emit(status_callback, message):
    if status_callback:
        status_callback(message)


def _image_dimensions(image_format):
    if image_format == "story":
        return 720, 1280
    return 1024, 1024


def _summarize_voices():
    voices = list_voices()
    summarized = []
    for voice in voices:
        summarized.append(
            {
                "voice_id": voice.get("voice_id"),
                "name": voice.get("name"),
                "labels": voice.get("labels", {}),
                "description": voice.get("description", ""),
            }
        )
    return voices, summarized


def _pick_voice_id(audio_output, voices):
    configured_voice_id = get_setting("ELEVENLABS_VOICE_ID", default="")
    if audio_output.get("voice_id"):
        return audio_output["voice_id"]
    if configured_voice_id:
        return configured_voice_id
    if voices:
        return voices[0].get("voice_id")
    raise RuntimeError("No ElevenLabs voice_id available.")


def _render_images(image_specs):
    rendered = []
    for image_spec in image_specs:
        width, height = _image_dimensions(image_spec.get("format"))
        asset = {
            "format": image_spec.get("format"),
            "platform": image_spec.get("platform"),
            "description": image_spec.get("description"),
            "prompt": image_spec.get("prompt"),
            "url": None,
        }
        try:
            asset["url"] = generate_image(
                image_spec["prompt"],
                width=width,
                height=height,
            )
        except Exception as exc:
            asset["error"] = str(exc)
        rendered.append(asset)
    return rendered


def _render_video_assets(image_bytes, video_plan, audio_plan):
    rendered_video = dict(video_plan)
    rendered_audio = dict(audio_plan)

    try:
        voices, _ = _summarize_voices()
    except Exception:
        voices = []
    voice_id = _pick_voice_id(rendered_audio, voices)
    rendered_audio["voice_id"] = voice_id
    rendered_audio["url"] = generate_voiceover(rendered_audio["script_text"], voice_id)

    raw_video_url = generate_video(
        image_bytes,
        rendered_video["video_prompt"],
        duration_seconds=rendered_video.get("duration_seconds", 6),
    )
    rendered_video["raw_url"] = raw_video_url

    text_overlays = rendered_video.get("text_overlays") or []
    text_overlay_url = add_text_overlay(raw_video_url, text_overlays) if text_overlays else raw_video_url
    rendered_video["text_overlay_url"] = text_overlay_url

    final_video_url = merge_audio_video(text_overlay_url, rendered_audio["url"])
    rendered_video["url"] = final_video_url
    rendered_video["has_voiceover"] = True

    return rendered_video, rendered_audio


def generate_campaign(image_bytes, status_callback=None):
    """
    Main pipeline: takes a product photo and runs all 7 agents plus real media services.
    """
    campaign = {}

    _emit(status_callback, "Brand Agent analyzing product...")
    brand_brief = run_brand_agent(image_bytes)
    campaign["brand_brief"] = brand_brief

    _emit(status_callback, "Copy Agent writing ad copy...")
    copy_output = run_copy_agent(brand_brief)
    campaign["copy"] = copy_output

    _emit(status_callback, "Audience Agent creating personas...")
    personas = run_audience_agent(brand_brief)
    campaign["personas"] = personas

    _emit(status_callback, "Visual Agent planning campaign images...")
    image_specs = run_visual_agent(brand_brief)
    _emit(status_callback, "Visual Agent generating final images...")
    campaign["images"] = _render_images(image_specs)

    _emit(status_callback, "Video Agent creating video prompt...")
    video_plan = run_video_agent(brand_brief, copy_output.get("tiktok", {}))

    _emit(status_callback, "Audio Agent selecting voice...")
    try:
        _, summarized_voices = _summarize_voices()
    except Exception:
        summarized_voices = []
    audio_output = run_audio_agent(brand_brief, video_plan.get("voiceover_script", ""), summarized_voices)

    _emit(status_callback, "Generating voiceover and video assets...")
    try:
        video_output, audio_output = _render_video_assets(image_bytes, video_plan, audio_output)
    except Exception as exc:
        video_output = dict(video_plan)
        video_output["url"] = None
        video_output["has_voiceover"] = False
        video_output["error"] = str(exc)
        audio_output = dict(audio_output)
        audio_output["url"] = None
        audio_output["error"] = str(exc)

    campaign["video"] = video_output
    campaign["audio"] = audio_output

    _emit(status_callback, "Media Plan Agent creating launch strategy...")
    campaign["media_plan"] = run_mediaplan_agent(brand_brief, copy_output, personas)

    _emit(status_callback, "Campaign complete!")
    return campaign


def refine_campaign(feedback, current_campaign, image_bytes=None, status_callback=None):
    """
    Re-runs only the affected agents and regenerates assets when needed.
    """
    _emit(status_callback, "Analyzing your feedback...")
    refine_result = run_refine_agent(feedback, current_campaign)
    agents_to_rerun = set(refine_result.get("agents_to_rerun", []))

    brand_brief = current_campaign["brand_brief"]
    copy_output = current_campaign["copy"]
    personas = current_campaign["personas"]
    image_specs = current_campaign.get("images", [])
    video_output = current_campaign.get("video", {})
    audio_output = current_campaign.get("audio", {})

    if "brand_agent" in agents_to_rerun and image_bytes:
        _emit(status_callback, "Re-running Brand Agent...")
        brand_brief = run_brand_agent(image_bytes)
        current_campaign["brand_brief"] = brand_brief

    if "copy_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Copy Agent...")
        copy_output = run_copy_agent(brand_brief)
        current_campaign["copy"] = copy_output

    if "audience_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Audience Agent...")
        personas = run_audience_agent(brand_brief)
        current_campaign["personas"] = personas

    if "visual_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Visual Agent...")
        image_specs = run_visual_agent(brand_brief)
        current_campaign["images"] = _render_images(image_specs)

    if "video_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Video Agent...")
        video_output = run_video_agent(brand_brief, copy_output.get("tiktok", {}))

    if "audio_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Audio Agent...")
        try:
            _, summarized_voices = _summarize_voices()
        except Exception:
            summarized_voices = []
        audio_output = run_audio_agent(
            brand_brief,
            video_output.get("voiceover_script", ""),
            summarized_voices,
        )

    if {"video_agent", "audio_agent"} & agents_to_rerun:
        _emit(status_callback, "Regenerating video and audio assets...")
        if image_bytes:
            try:
                video_output, audio_output = _render_video_assets(image_bytes, video_output, audio_output)
            except Exception as exc:
                video_output = dict(video_output)
                video_output["url"] = None
                video_output["has_voiceover"] = False
                video_output["error"] = str(exc)
                audio_output = dict(audio_output)
                audio_output["url"] = None
                audio_output["error"] = str(exc)
        current_campaign["video"] = video_output
        current_campaign["audio"] = audio_output

    if "mediaplan_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Media Plan Agent...")
        current_campaign["media_plan"] = run_mediaplan_agent(brand_brief, copy_output, personas)

    _emit(status_callback, "Refinement complete!")
    return current_campaign


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m agents.orchestrator <image_path>")
        print("Example: python -m agents.orchestrator test_candle.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    with open(image_path, "rb") as file_handle:
        img_bytes = file_handle.read()

    def print_status(message):
        print(f"  >> {message}")

    print("Running full campaign pipeline...")
    result = generate_campaign(img_bytes, status_callback=print_status)
    print("\n=== FULL CAMPAIGN OUTPUT ===")
    print(json.dumps(result, indent=2))
