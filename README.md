# Jumpshot Comparison Prototype
This project explores whether video input and an AI model can analyze a basketball jumpshot and compare it to an NBA player.

## Demo
The demo loads a jumpshot video, extracts frames, samples a smaller set for Gemini, and returns a text-based shooting-form analysis.

The checked-in demo assets are:
- `demo/input.mp4`
- `demo/output.txt`

## Example Output
```text
=== Video Loaded ===
354 frames extracted from video.
8 frames prepared for Gemini sampling.

=== Demo Summary ===
Reference player: Stephen Curry
Status: fallback active (Gemini shot analysis failed: [WinError 10051] A socket operation was attempted to an unreachable network)
```

## Pipeline
1. Load the input jumpshot video.
2. Extract frames from the video with OpenCV.
3. Sample a smaller set of frames for Gemini.
4. Send the sampled frames to Gemini for shooting-form analysis.
5. Build a comparison prompt against a reference NBA player.
6. Print the shot analysis, reference snapshot, and comparison text.
7. Fall back to `demo/output.txt` if Gemini is unavailable in demo mode.

## Run
```bash
powershell -ExecutionPolicy Bypass -File .\run_demo.ps1
```

The script runs `python backend/analysis/main.py` with `DEMO_MODE=true`.

## Key Takeaway
Prompt-based video analysis can generate detailed basketball feedback, but it is not reliable enough by itself. The model can sound confident while still identifying the wrong player or making incorrect form comparisons.

## Limitations
- No pose estimation
- No joint tracking
- No biomechanics features
- No temporal motion model
- Output depends heavily on the model's visual interpretation

## Future Work
A stronger version would use pose estimation and motion features to compare jumpshots more objectively.

## Status
Early prototype / exploration.

## Notes
This repo also contains earlier backend and frontend experiments. The main documented path is the analysis demo above.
