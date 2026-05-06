try:
    from IPython.display import display, Image
except ImportError:
    display = None
    Image = None
import cv2
import time
import os
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None
from analysis_bridge import get_nba_player_analysis, is_demo_mode
from dotenv import load_dotenv


def load_environment():
    env_candidates = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
    ]
    for env_path in env_candidates:
        absolute_path = os.path.abspath(env_path)
        if os.path.exists(absolute_path):
            load_dotenv(absolute_path, override=False)


load_environment()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
REFERENCE_PLAYER = os.environ.get("REFERENCE_PLAYER", "Stephen Curry")


def build_gemini_client():
    if genai is None or not GEMINI_API_KEY:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def resolve_demo_output_path():
    return os.path.join(repo_root(), "demo", "output.txt")


def load_saved_demo_output():
    output_path = resolve_demo_output_path()
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Demo output not found at {output_path}")
    with open(output_path, "r", encoding="utf-8") as handle:
        return handle.read()


def extract_saved_section(content, heading):
    marker = f"{heading}\n"
    start = content.find(marker)
    if start == -1:
        return content.strip()

    start += len(marker)
    lines = content[start:].splitlines()
    collected = []

    for line in lines:
        if line and not line.startswith(" ") and line in {
            "Shot Analysis",
            "Reference Snapshot",
            "Player Comparison",
        }:
            break
        collected.append(line)

    return "\n".join(collected).strip()


def load_demo_fallback_result():
    saved_output = load_saved_demo_output()
    return {
        "video_path": resolve_video_path(),
        "amateur_analysis": extract_saved_section(saved_output, "Shot Analysis"),
        "nba_analysis": extract_saved_section(saved_output, "Reference Snapshot"),
        "comparison": extract_saved_section(saved_output, "Player Comparison"),
    }


def print_stage(title, detail=None):
    print(f"\n=== {title} ===")
    if detail:
        print(detail)


def print_demo_result(result, fallback_reason=None):
    print_stage("Demo Summary")
    print(f"Video: {result['video_path']}")
    print(f"Reference player: {REFERENCE_PLAYER}")
    print(f"Mode: {'demo' if is_demo_mode() else 'live'}")

    if fallback_reason:
        print(f"Status: fallback active ({fallback_reason})")
    else:
        print("Status: live Gemini analysis completed")

    print_stage("Shot Analysis")
    print(result["amateur_analysis"])

    print_stage("Reference Snapshot")
    print(result["nba_analysis"])

    print_stage("Player Comparison")
    print(result["comparison"])

def resolve_video_path():
    # Prefer the original local example if present, but fall back to the repo demo asset
    # so the script still has a valid sample after the repo cleanup.
    video_candidates = [
        os.path.join("import videos", "Hanson.mp4"),
        os.path.join(repo_root(), "demo", "input.mp4"),
    ]

    video_path = next((path for path in video_candidates if os.path.exists(path)), None)
    if video_path is None:
        raise FileNotFoundError(
            "Video file not found. Expected one of: "
            + ", ".join(video_candidates)
        )
    return video_path

def main():
    # Note: Running in IPython will show frame-by-frame preview.
    # Regular Python execution will skip the preview but still perform the analysis.

    video_path = resolve_video_path()

    video = cv2.VideoCapture(video_path)

    frame_parts = []
    preview_frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        jpeg_bytes = buffer.tobytes()
        preview_frames.append(jpeg_bytes)
        if types is not None:
            frame_parts.append(
                types.Part.from_bytes(
                    data=jpeg_bytes,
                    mime_type="image/jpeg",
                )
            )
    video.release()
    print_stage("Video Loaded", video_path)
    print(f"{len(preview_frames)} frames extracted from video.")
    if frame_parts:
        print(f"{len(frame_parts[0::50])} frames prepared for Gemini sampling.")

    # Optional: Display frames (will work in Jupyter/IPython, skip otherwise)
    try:
        if display is None or Image is None:
            raise RuntimeError("IPython display is unavailable")
        display_handle = display(None, display_id=True)
        for img in preview_frames:
            display_handle.update(Image(data=img))
            time.sleep(0.025)
    except Exception:
        print("Frame preview skipped outside IPython.")

    client = build_gemini_client()
    if client is None:
        if not is_demo_mode():
            raise RuntimeError(
                "Gemini is unavailable. Install google-genai and set GEMINI_API_KEY or GOOGLE_API_KEY."
            )
        fallback_result = load_demo_fallback_result()
        fallback_result["amateur_analysis"] = (
            f"Read {len(preview_frames)} frames from {video_path}. "
            "Gemini client unavailable, so this demo used the saved comparison artifact."
        )
        print_demo_result(
            fallback_result,
            fallback_reason="Gemini client unavailable",
        )
        return fallback_result

    try:
        analysis_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                "Analyze this basketball shooting form video. Focus on: 1) Jump height 2) Shot set point 3) Foot positioning 4) Ball path to set point 5) Release mechanics 6) Guide hand position 7) Shot motion type (one or two motion) 8) Shoulder alignment. Provide specific details for each element.",
                *frame_parts[0::50],
            ],
        )
        jumpshot_analysis = analysis_response.text
    except Exception as error:
        if not is_demo_mode():
            raise
        error_message = str(error)
        fallback_result = load_demo_fallback_result()
        fallback_result["amateur_analysis"] = (
            f"Read {len(preview_frames)} frames from {video_path}. "
            f"Gemini shot analysis failed ({error_message}), so this demo used the saved comparison artifact."
        )
        print_demo_result(
            fallback_result,
            fallback_reason=f"Gemini shot analysis failed: {error_message}",
        )
        return fallback_result

    # Get the NBA player analysis
    nba_player = REFERENCE_PLAYER
    nba_player_analysis = get_nba_player_analysis(nba_player)

    comparison_prompt = f"""Given these two analyses, provide a technical comparison:

Amateur Analysis:
{jumpshot_analysis}

NBA Player Analysis (for {nba_player}):
{nba_player_analysis}

Focus only on comparing:
1. Technical similarities in form
2. Key mechanical differences
3. Specific improvement recommendations
4. Overall form matching percentage
"""
    try:
        comparison_result = client.models.generate_content(
            model=MODEL_NAME,
            contents=comparison_prompt,
        )
        comparison_text = comparison_result.text
    except Exception:
        if not is_demo_mode():
            raise
        comparison_text = load_saved_demo_output()

    result = {
        "video_path": video_path,
        "amateur_analysis": jumpshot_analysis,
        "nba_analysis": nba_player_analysis,
        "comparison": comparison_text,
    }
    print_demo_result(result)

    if is_demo_mode():
        save_analysis(
            resolve_demo_output_path(),
            jumpshot_analysis,
            nba_player_analysis,
            comparison_text,
        )

    return result

def save_analysis(filename, amateur_analysis, nba_analysis, comparison):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding="utf-8") as f:
        f.write("Demo comparison artifact\n\n")
        f.write(f"Reference player: {REFERENCE_PLAYER}\n\n")
        f.write("Shot Analysis\n")
        f.write(f"{amateur_analysis}\n\n")
        f.write("Reference Snapshot\n")
        f.write(f"{nba_analysis}\n\n")
        f.write("Player Comparison\n")
        f.write(comparison)

if __name__ == "__main__":
    main()
