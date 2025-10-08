from IPython.display import display, Image, Audio
import cv2 
import base64
import time
from openai import OpenAI
import os
from root.backend.analysis.analysis_bridge import get_nba_player_analysis
from dotenv import load_dotenv

load_dotenv()  # Add this before creating the OpenAI client

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Note: Running in IPython will show frame-by-frame preview. 
# Regular Python execution will skip the preview but still perform the analysis.

# extracting frames from video

video_path = os.path.join("import videos", "Hanson.mp4")
if not os.path.exists(video_path):
    raise FileNotFoundError(f"Video file not found: {video_path}")

video = cv2.VideoCapture(video_path)

base64Frames = []
while video.isOpened():
    success, frame = video.read()
    if not success:
        break
    _, buffer = cv2.imencode(".jpg", frame)
    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
video.release()
print(len(base64Frames), "frames read.")

# Optional: Display frames (will work in Jupyter/IPython, skip otherwise)
try:
    # Try to display frames if in IPython environment
    display_handle = display(None, display_id=True)
    for img in base64Frames:
        display_handle.update(Image(data=base64.b64decode(img.encode("utf-8"))))
        time.sleep(0.025)
except:
    print("Frame display skipped - not in IPython environment")
    
# Prompt    
    
PROMPT_MESSAGES = [
    {
        "role": "user",
        "content": [
            "Analyze this basketball shooting form video. Focus on: 1) Jump height 2) Shot set point 3) Foot positioning 4) Ball path to set point 5) Release mechanics 6) Guide hand position 7) Shot motion type (one or two motion) 8) Shoulder alignment. Provide specific details for each element.",
            *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
        ],
    },
]
params = {
    "model": "gpt-4o",
    "messages": PROMPT_MESSAGES,
    "max_tokens": 1000,
}

result = client.chat.completions.create(**params)
print(result.choices[0].message.content)

# Store the GPT-4V analysis as a variable
jumpshot_analysis = result.choices[0].message.content

# Get the NBA player analysis
nba_player = "Stephen Curry"  # or get this from user input
nba_player_analysis = get_nba_player_analysis(nba_player)

# Create a new prompt for comparison
COMPARISON_PROMPT = [
    {
        "role": "user",
        "content": f"""Given these two analyses, provide a technical comparison:

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
    }
]

# Run the comparison through GPT
comparison_params = {
    "model": "gpt-4o",
    "messages": COMPARISON_PROMPT,
    "max_tokens": 1000,
}

comparison_result = client.chat.completions.create(**comparison_params)
print("\nComparison Analysis:")
print(comparison_result.choices[0].message.content)

# Optionally save the results
def save_analysis(filename, amateur_analysis, nba_analysis, comparison):
    with open(filename, 'w') as f:
        f.write(f"Amateur Analysis:\n{amateur_analysis}\n\n")
        f.write(f"NBA Player Analysis:\n{nba_analysis}\n\n")
        f.write(f"Comparison:\n{comparison}")
