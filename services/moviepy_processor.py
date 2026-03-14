import os
import tempfile
from typing import Iterable, List, Sequence

from services._common import build_object_key
from services.s3 import read_file_bytes, upload_file

try:
    from moviepy import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip, concatenate_videoclips
except ImportError:  # pragma: no cover - MoviePy v1 fallback
    from moviepy.editor import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip, concatenate_videoclips


def _write_temp_file(directory: str, filename: str, content: bytes) -> str:
    path = os.path.join(directory, filename)
    with open(path, "wb") as file_handle:
        file_handle.write(content)
    return path


def _subclip(clip, start_time: float, end_time: float):
    if hasattr(clip, "subclipped"):
        return clip.subclipped(start_time, end_time)
    return clip.subclip(start_time, end_time)


def _with_audio(video_clip, audio_clip):
    if hasattr(video_clip, "with_audio"):
        return video_clip.with_audio(audio_clip)
    return video_clip.set_audio(audio_clip)


def _with_duration(clip, duration: float):
    if hasattr(clip, "with_duration"):
        return clip.with_duration(duration)
    return clip.set_duration(duration)


def _with_position(clip, position):
    if hasattr(clip, "with_position"):
        return clip.with_position(position)
    return clip.set_position(position)


def _with_start(clip, start_time: float):
    if hasattr(clip, "with_start"):
        return clip.with_start(start_time)
    return clip.set_start(start_time)


def _seconds(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    if text.endswith("s"):
        text = text[:-1]
    return float(text)


def _normalize_overlays(text_lines, positions, timings) -> List[dict]:
    if text_lines and isinstance(text_lines[0], dict):
        overlays = []
        for overlay in text_lines:
            overlays.append(
                {
                    "text": overlay["text"],
                    "position": overlay.get("position", "center"),
                    "start": _seconds(overlay.get("time_start", 0)),
                    "end": _seconds(overlay.get("time_end", 1)),
                }
            )
        return overlays

    overlays = []
    positions = positions or ["center"] * len(text_lines)
    timings = timings or [(0, 1)] * len(text_lines)

    for text, position, timing in zip(text_lines, positions, timings):
        start_time, end_time = timing
        overlays.append(
            {
                "text": text,
                "position": position,
                "start": _seconds(start_time),
                "end": _seconds(end_time),
            }
        )

    return overlays


def _text_position(position: str):
    normalized = str(position).strip().lower()
    if normalized == "top":
        return ("center", 50)
    if normalized == "bottom":
        return ("center", "bottom")
    return "center"


def _make_text_clip(text: str, video_width: int):
    kwargs = {
        "text": text,
        "font_size": 54,
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 2,
        "method": "caption",
        "size": (int(video_width * 0.8), None),
    }
    try:
        return TextClip(**kwargs)
    except TypeError:
        return TextClip(
            txt=text,
            fontsize=54,
            color="white",
            stroke_color="black",
            stroke_width=2,
            method="caption",
            size=(int(video_width * 0.8), None),
        )


def merge_audio_video(video_s3_url: str, audio_s3_url: str) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = _write_temp_file(temp_dir, "input-video.mp4", read_file_bytes(video_s3_url))
        audio_path = _write_temp_file(temp_dir, "input-audio.mp3", read_file_bytes(audio_s3_url))
        output_path = os.path.join(temp_dir, "merged-video.mp4")

        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        merged_clip = None

        try:
            final_duration = min(video_clip.duration, audio_clip.duration)
            final_video = _subclip(video_clip, 0, final_duration)
            final_audio = _subclip(audio_clip, 0, final_duration)
            merged_clip = _with_audio(final_video, final_audio)
            merged_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=getattr(video_clip, "fps", 24),
                logger=None,
            )

            with open(output_path, "rb") as file_handle:
                return upload_file(file_handle.read(), build_object_key("generated/videos", ".mp4"), "video/mp4")
        finally:
            video_clip.close()
            audio_clip.close()
            try:
                merged_clip.close()
            except Exception:
                pass


def add_text_overlay(
    video_s3_url: str,
    text_lines: Sequence,
    positions: Sequence = None,
    timings: Sequence = None,
) -> str:
    overlays = _normalize_overlays(list(text_lines), positions, timings)

    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = _write_temp_file(temp_dir, "overlay-input.mp4", read_file_bytes(video_s3_url))
        output_path = os.path.join(temp_dir, "overlay-output.mp4")

        video_clip = VideoFileClip(video_path)
        text_clips = []
        composite = None

        try:
            for overlay in overlays:
                duration = max(overlay["end"] - overlay["start"], 0.1)
                text_clip = _make_text_clip(overlay["text"], int(video_clip.w))
                text_clip = _with_position(text_clip, _text_position(overlay["position"]))
                text_clip = _with_start(text_clip, overlay["start"])
                text_clip = _with_duration(text_clip, duration)
                text_clips.append(text_clip)

            layers = [video_clip, *text_clips]
            composite = CompositeVideoClip(layers, size=video_clip.size)
            if video_clip.audio is not None:
                composite = _with_audio(composite, video_clip.audio)

            composite.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

            with open(output_path, "rb") as file_handle:
                return upload_file(file_handle.read(), build_object_key("generated/videos", ".mp4"), "video/mp4")
        finally:
            video_clip.close()
            for clip in text_clips:
                clip.close()
            try:
                composite.close()
            except Exception:
                pass


def stitch_clips(clip_s3_urls: Iterable[str]) -> str:
    clip_s3_urls = list(clip_s3_urls)
    if not clip_s3_urls:
        raise ValueError("stitch_clips requires at least one clip URL.")

    with tempfile.TemporaryDirectory() as temp_dir:
        local_paths = []
        for index, clip_url in enumerate(clip_s3_urls, start=1):
            local_paths.append(
                _write_temp_file(temp_dir, f"clip-{index}.mp4", read_file_bytes(clip_url))
            )

        clips = [VideoFileClip(path) for path in local_paths]
        output_path = os.path.join(temp_dir, "stitched-output.mp4")
        final_clip = None

        try:
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

            with open(output_path, "rb") as file_handle:
                return upload_file(file_handle.read(), build_object_key("generated/videos", ".mp4"), "video/mp4")
        finally:
            for clip in clips:
                clip.close()
            try:
                final_clip.close()
            except Exception:
                pass
