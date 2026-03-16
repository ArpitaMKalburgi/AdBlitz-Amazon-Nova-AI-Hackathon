import json
import hashlib
import concurrent.futures
import threading
import requests
from agents.brand_agent import run_brand_agent
from agents.copy_agent import run_copy_agent
from agents.audience_agent import run_audience_agent
from agents.visual_agent import run_visual_agent
from agents.video_agent import run_video_agent
from agents.audio_agent import run_audio_agent
from agents.mediaplan_agent import run_mediaplan_agent
from agents.refine_agent import run_refine_agent
from services._common import build_aws_client, get_setting
from services.polly import generate_voiceover, list_voices
from services.moviepy_processor import add_text_overlay, merge_audio_video
from services.nova_canvas import generate_image
from services.nova_reel import generate_video


# ── S3-based cache ────────────────────────────────────────────

def _get_s3_client():
    # Keep S3 auth behavior consistent with all other AWS service clients.
    return build_aws_client("s3")


def _cache_key(image_bytes):
    return hashlib.md5(image_bytes).hexdigest()


def get_cached_campaign(image_bytes):
    key = _cache_key(image_bytes)
    try:
        s3 = _get_s3_client()
        obj = s3.get_object(Bucket=get_setting("S3_BUCKET"), Key=f"cache/{key}.json")
        return json.loads(obj["Body"].read().decode("utf-8"))
    except Exception:
        return None


def _save_to_cache(image_bytes, campaign):
    key = _cache_key(image_bytes)
    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=get_setting("S3_BUCKET"),
            Key=f"cache/{key}.json",
            Body=json.dumps(campaign),
            ContentType="application/json",
        )
    except Exception:
        pass


def _has_complete_video(campaign):
    video = (campaign or {}).get("video") or {}
    return bool(video.get("url"))


def _can_resume_video_from_cache(campaign):
    if not campaign or _has_complete_video(campaign):
        return False

    required_fields = ("brand_brief", "copy", "personas", "images", "video", "audio")
    if not all(field in campaign for field in required_fields):
        return False

    video = campaign.get("video") or {}
    audio = campaign.get("audio") or {}
    return bool(video.get("video_prompt") and audio.get("script_text"))


# ── Helpers ───────────────────────────────────────────────────

def _emit(cb, msg):
    if cb:
        cb(msg)


def _image_dimensions(fmt):
    if fmt == "story":
        return 720, 1280
    return 1024, 1024


def _summarize_voices():
    voices = list_voices()
    summarized = [
        {
            "voice_id": v.get("voice_id"),
            "name": v.get("name"),
            "labels": v.get("labels", {}),
            "description": v.get("description", ""),
        }
        for v in voices
    ]
    return voices, summarized


def _pick_voice_id(audio_output, voices):
    configured = get_setting("POLLY_VOICE_ID", default=get_setting("ELEVENLABS_VOICE_ID", default=""))
    if audio_output.get("voice_id"):
        return audio_output["voice_id"]
    if configured:
        return configured
    if voices:
        return voices[0].get("voice_id")
    raise RuntimeError("No Amazon Polly voice_id available.")


def _render_one_image(spec):
    w, h = _image_dimensions(spec.get("format"))
    asset = {
        "format": spec.get("format"),
        "platform": spec.get("platform"),
        "description": spec.get("description"),
        "prompt": spec.get("prompt"),
        "url": None,
    }
    try:
        asset["url"] = generate_image(spec["prompt"], width=w, height=h)
    except Exception as e:
        asset["error"] = str(e)
    return asset


def _render_images(specs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(_render_one_image, specs))


def _get_lifestyle_image_bytes(images):
    for img in images:
        if img.get("format") == "lifestyle" and img.get("url"):
            try:
                r = requests.get(img["url"], timeout=15)
                if r.status_code == 200:
                    return r.content
            except Exception:
                pass
    for img in images:
        if img.get("url"):
            try:
                r = requests.get(img["url"], timeout=15)
                if r.status_code == 200:
                    return r.content
            except Exception:
                pass
    return None


def _render_video_assets(image_bytes, video_plan, audio_plan):
    rv = dict(video_plan)
    ra = dict(audio_plan)

    try:
        voices, _ = _summarize_voices()
    except Exception:
        voices = []

    try:
        voice_id = _pick_voice_id(ra, voices)
        ra["voice_id"] = voice_id
        ra["url"] = generate_voiceover(ra["script_text"], voice_id)
    except Exception as exc:
        # Voiceover is optional; keep going so Bedrock can still return a raw video.
        ra["url"] = None
        ra["error"] = str(exc)

    raw_url = generate_video(
        image_bytes, rv["video_prompt"],
        duration_seconds=rv.get("duration_seconds", 6),
    )
    rv["raw_url"] = raw_url

    overlay_url = raw_url
    rv["text_overlay_url"] = raw_url

    if ra.get("url"):
        try:
            final_url = merge_audio_video(overlay_url, ra["url"])
            rv["url"] = final_url
            rv["has_voiceover"] = True
        except Exception as exc:
            # If merge fails (e.g. on cloud), use raw video without voiceover.
            ra["error"] = str(exc)
            rv["url"] = raw_url
            rv["has_voiceover"] = False
    else:
        rv["url"] = raw_url
        rv["has_voiceover"] = False

    return rv, ra


def _render_video_assets_with_timeout(image_bytes, video_plan, audio_plan, timeout=600):
    """Run video generation in a thread with a timeout to prevent Streamlit Cloud drops."""
    result = {"video": None, "audio": None, "error": None}

    def _worker():
        try:
            v, a = _render_video_assets(image_bytes, video_plan, audio_plan)
            result["video"] = v
            result["audio"] = a
        except Exception as e:
            print(f"VIDEO ERROR: {e}")
            import traceback
            traceback.print_exc()
            result["error"] = str(e)

    thread = threading.Thread(target=_worker)
    thread.start()

    # Poll in small intervals to keep Streamlit connection alive
    elapsed = 0
    poll_interval = 5
    while thread.is_alive() and elapsed < timeout:
        thread.join(timeout=poll_interval)
        elapsed += poll_interval

    if thread.is_alive():
        # Thread still running — video is generating but we timed out
        result["error"] = "Video is still generating. It will be available in cache on next load."

    return result


# ── Main pipeline ─────────────────────────────────────────────

def generate_campaign(image_bytes, status_callback=None):
    cached = get_cached_campaign(image_bytes)
    if _has_complete_video(cached):
        _emit(status_callback, "Loading from cache...")
        return cached

    if _can_resume_video_from_cache(cached):
        _emit(status_callback, "Retrying video generation from cache...")
        campaign = cached
        brand_brief = campaign["brand_brief"]
        copy_output = campaign["copy"]
        personas = campaign["personas"]
        video_plan = campaign["video"]
        audio_output = campaign["audio"]
    else:
        campaign = {}

        _emit(status_callback, "Analyzing product...")
        brand_brief = run_brand_agent(image_bytes)
        campaign["brand_brief"] = brand_brief

        _emit(status_callback, "Writing copy, building personas, planning visuals...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            future_copy = pool.submit(run_copy_agent, brand_brief)
            future_audience = pool.submit(run_audience_agent, brand_brief)
            future_visual = pool.submit(run_visual_agent, brand_brief)

            copy_output = future_copy.result()
            personas = future_audience.result()
            image_specs = future_visual.result()

        campaign["copy"] = copy_output
        campaign["personas"] = personas

        _emit(status_callback, "Generating ad images...")
        campaign["images"] = _render_images(image_specs)

        _emit(status_callback, "Directing video ad...")
        video_plan = run_video_agent(brand_brief, copy_output.get("tiktok", {}))

        _emit(status_callback, "Selecting voice...")
        try:
            _, summarized = _summarize_voices()
        except Exception:
            summarized = []
        audio_output = run_audio_agent(brand_brief, video_plan.get("voiceover_script", ""), summarized)

        # Save campaign WITHOUT video first so user gets results faster
        campaign["video"] = dict(video_plan)
        campaign["video"]["url"] = None
        campaign["video"]["has_voiceover"] = False
        campaign["video"]["status"] = "generating"
        campaign["audio"] = dict(audio_output)
        campaign["audio"]["url"] = None

        # Save partial campaign to cache (everything except video)
        _save_to_cache(image_bytes, campaign)

    lifestyle_bytes = _get_lifestyle_image_bytes(campaign["images"])
    video_source = lifestyle_bytes if lifestyle_bytes else image_bytes

    _emit(status_callback, "Generating video and voiceover (this may take a few minutes)...")

    # Now attempt video generation with timeout (10 min)
    video_result = _render_video_assets_with_timeout(video_source, video_plan, audio_output, timeout=600)

    if video_result["video"] and not video_result["error"]:
        campaign["video"] = video_result["video"]
        campaign["video"]["status"] = "completed"
        campaign["video"].pop("error", None)
        campaign["audio"] = video_result["audio"]
        campaign["audio"].pop("error", None)
    else:
        campaign["video"] = dict(video_plan)
        campaign["video"]["url"] = None
        campaign["video"]["has_voiceover"] = False
        campaign["video"]["error"] = video_result.get("error", "Video generation timed out")
        campaign["video"]["status"] = "failed"
        campaign["audio"] = dict(audio_output)
        campaign["audio"]["url"] = None

    if not campaign.get("media_plan"):
        _emit(status_callback, "Creating launch strategy...")
        campaign["media_plan"] = run_mediaplan_agent(brand_brief, copy_output, personas)

    _emit(status_callback, "Done.")
    # Save final campaign with video (or without if failed)
    _save_to_cache(image_bytes, campaign)

    return campaign


# ── Refine ────────────────────────────────────────────────────

def refine_campaign(feedback, current_campaign, image_bytes=None, status_callback=None):
    _emit(status_callback, "Analyzing feedback...")
    refine_result = run_refine_agent(feedback, current_campaign)
    agents_to_rerun = set(refine_result.get("agents_to_rerun", []))

    brand_brief = current_campaign["brand_brief"]
    copy_output = current_campaign["copy"]
    personas = current_campaign["personas"]

    if "brand_agent" in agents_to_rerun and image_bytes:
        _emit(status_callback, "Re-running Brand Agent...")
        brand_brief = run_brand_agent(image_bytes)
        current_campaign["brand_brief"] = brand_brief

    parallel_agents = {"copy_agent", "audience_agent", "visual_agent"} & agents_to_rerun
    if parallel_agents:
        _emit(status_callback, "Regenerating affected sections...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = {}
            if "copy_agent" in parallel_agents:
                futures["copy"] = pool.submit(run_copy_agent, brand_brief)
            if "audience_agent" in parallel_agents:
                futures["personas"] = pool.submit(run_audience_agent, brand_brief)
            if "visual_agent" in parallel_agents:
                futures["images"] = pool.submit(run_visual_agent, brand_brief)

            if "copy" in futures:
                copy_output = futures["copy"].result()
                current_campaign["copy"] = copy_output
            if "personas" in futures:
                personas = futures["personas"].result()
                current_campaign["personas"] = personas
            if "images" in futures:
                specs = futures["images"].result()
                current_campaign["images"] = _render_images(specs)

    if "video_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Video Agent...")
        video_output = run_video_agent(brand_brief, copy_output.get("tiktok", {}))
        current_campaign["video"] = video_output

    if "audio_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Audio Agent...")
        try:
            _, summarized = _summarize_voices()
        except Exception:
            summarized = []
        audio_output = run_audio_agent(
            brand_brief,
            current_campaign.get("video", {}).get("voiceover_script", ""),
            summarized,
        )
        current_campaign["audio"] = audio_output

    if {"video_agent", "audio_agent"} & agents_to_rerun:
        _emit(status_callback, "Regenerating video assets...")
        if image_bytes:
            try:
                lifestyle_bytes = _get_lifestyle_image_bytes(current_campaign.get("images", []))
                video_source = lifestyle_bytes if lifestyle_bytes else image_bytes
                video_result = _render_video_assets_with_timeout(
                    video_source,
                    current_campaign.get("video", {}),
                    current_campaign.get("audio", {}),
                    timeout=600,
                )
                if video_result["video"] and not video_result["error"]:
                    current_campaign["video"] = video_result["video"]
                    current_campaign["audio"] = video_result["audio"]
                else:
                    current_campaign["video"]["error"] = video_result.get("error", "Video generation timed out")
                    current_campaign["audio"]["error"] = video_result.get("error", "")
            except Exception as e:
                current_campaign["video"]["error"] = str(e)
                current_campaign["audio"]["error"] = str(e)

    if "mediaplan_agent" in agents_to_rerun:
        _emit(status_callback, "Re-running Media Plan Agent...")
        current_campaign["media_plan"] = run_mediaplan_agent(brand_brief, copy_output, personas)

    _emit(status_callback, "Refinement complete.")
    return current_campaign


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m agents.orchestrator <image_path>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        img = f.read()

    def log(msg):
        print(f"  >> {msg}")

    print("Running full campaign pipeline...")
    result = generate_campaign(img, status_callback=log)
    print("\n=== FULL CAMPAIGN OUTPUT ===")
    print(json.dumps(result, indent=2))
