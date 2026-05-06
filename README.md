# Jumpshot Comparison Prototype

## Overview
This project is a technical experiment exploring the limitations of LLM-only video analysis for basketball jumpshot comparison. It samples frames from a shot video, sends them to Gemini, and compares the result against a reference NBA player.
The goal was to test whether prompt-based multimodal analysis could generate meaningful shooting-form comparisons from video alone.

## Pipeline
1. Load the input jumpshot video.
2. Extract every frame with OpenCV.
3. Sample a smaller frame set for Gemini.
4. Send the sampled frames and a shot-analysis prompt to Gemini.
5. Load a reference NBA player description.
6. Ask Gemini for a comparison between the two analyses.
7. Print the analysis to the terminal and save the demo artifact.

## Demo Output
```text
=== Demo Summary ===
354 frames extracted from video
8 frames prepared for Gemini sampling
Reference player: Stephen Curry

=== Shot Analysis ===
Jump Height: moderate to low
Release Mechanics: smooth and consistent

=== Issue Observed ===
The model produced a detailed analysis but incorrectly identified the player as Nikola Jokic.
```

## Observed Failure
The most important takeaway from the demo is not that the system predicts perfectly, but that Gemini can produce confident and structured analysis while still misidentifying the shooter.

## Limitations
- No pose estimation
- No joint tracking
- No biomechanics features
- No temporal motion model
- Output depends heavily on the model's visual interpretation

## Future Work
A stronger version would use pose estimation, tracked body landmarks, and motion features to compare jumpshots more objectively.

## Status
Early prototype / exploration.
