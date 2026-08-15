import subprocess
import json
import re


def get_audio_metadata(file_path):

    # -----------------------------------------
    # Basic metadata using ffprobe
    # -----------------------------------------

    command = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFprobe failed:\n{result.stderr}"
        )

    data = json.loads(result.stdout)

    audio_stream = next(
        (
            stream
            for stream in data.get("streams", [])
            if stream.get("codec_type") == "audio"
        ),
        None
    )

    if audio_stream is None:
        raise ValueError("No audio stream found.")

    # -----------------------------------------
    # Duration
    # -----------------------------------------

    duration = float(
        audio_stream.get(
            "duration",
            data.get("format", {}).get("duration", 0)
        )
    )

    # -----------------------------------------
    # Sample Rate
    # -----------------------------------------

    sample_rate = int(
        audio_stream.get("sample_rate", 0)
    )

    sample_rate_khz = sample_rate / 1000

    # -----------------------------------------
    # Bitrate
    # -----------------------------------------

    bitrate = audio_stream.get(
        "bit_rate",
        data.get("format", {}).get("bit_rate", 0)
    )

    bitrate_kbps = (
        float(bitrate) / 1000
        if bitrate
        else None
    )

    # -----------------------------------------
    # Loudness
    # -----------------------------------------

    loudness_db = get_loudness(file_path)

    return {
        "duration_seconds": duration,
        "sample_rate_khz": sample_rate_khz,
        "bitrate_kbps": bitrate_kbps,
        "loudness_db": loudness_db
    }


def get_loudness(file_path):

    command = [
        "ffmpeg",
        "-i",
        file_path,
        "-af",
        "ebur128",
        "-f",
        "null",
        "-"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    output = result.stderr

    # Look for final integrated loudness
    matches = re.findall(
        r"I:\s*(-?\d+(?:\.\d+)?)\s+LUFS",
        output
    )

    if matches:
        return float(matches[-1])

    return None