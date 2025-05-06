import cv2
import time
import argparse
import threading
import pygame
import numpy as np
import os

from moviepy import VideoFileClip

# Smoothed and visually clean character sets
ASCII_CHARS_GRAY = [' ', '.', ':', '-', '=', '+', '*', 'o', 'O', '#', '@']
ASCII_CHARS_COLOR = [' ', '.', ':', '+', '*', 'o', 'O', '#', '@']

def pixel_to_ascii(luminance, charset):
    index = int(luminance / 256 * len(charset))
    return charset[min(index, len(charset) - 1)]

def adjust_luminance(lum, gamma=0.85):
    return 255 * ((lum / 255) ** gamma)

def colored_ascii(char, r, g, b, grayscale):
    if grayscale:
        return char
    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"

def frame_to_ascii_color(frame, width, grayscale):
    height, _, _ = frame.shape
    char_aspect = 11 / 24  # Font aspect ratio (depends on terminal font)
    new_height = int(height * width * char_aspect / frame.shape[1])

    # Resize for performance & proportional output
    resized = cv2.resize(frame, (width, new_height), interpolation=cv2.INTER_AREA)

    ascii_lines = []
    charset = ASCII_CHARS_GRAY if grayscale else ASCII_CHARS_COLOR

    for row in resized:
        line = ""
        for b, g, r in row:
            lum = adjust_luminance(0.2126 * r + 0.7152 * g + 0.0722 * b)
            char = pixel_to_ascii(lum, charset)
            line += colored_ascii(char, r, g, b, grayscale) * 2
        ascii_lines.append(line)
    return "\n".join(ascii_lines)

def play_audio_sync(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

def play_video_as_ascii(video_path, width, enable_audio, grayscale):
    clip = VideoFileClip(video_path)
    fps = clip.fps
    audio_path = "temp_audio.mp3"
    frames = [frame for frame in clip.iter_frames(fps=fps, dtype="uint8")]

    audio_thread = None
    if enable_audio:
        clip.audio.write_audiofile(audio_path)
        audio_thread = threading.Thread(target=play_audio_sync, args=(audio_path,))
        audio_thread.start()

    start_time = time.time()

    print("\033[?25l", end="")  # Hide cursor
    try:
        for i in range(len(frames)):
            elapsed = time.time() - start_time
            expected_frame = int(elapsed * fps)
            if expected_frame >= len(frames):
                break

            frame_bgr = cv2.cvtColor(frames[expected_frame], cv2.COLOR_RGB2BGR)
            ascii_frame = frame_to_ascii_color(frame_bgr, width, grayscale)

            print("\033[H", end="")  # Move cursor to top-left
            print(ascii_frame)

            time.sleep(1 / fps / 2)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        print("\033[?25h", end="")  # Show cursor
        pygame.mixer.music.stop()
        if audio_thread:
            audio_thread.join()
        clip.close()
        if enable_audio and os.path.exists(audio_path):
            os.remove(audio_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--width", type=int, default=80, help="ASCII output width")
    parser.add_argument("--sound", action="store_true", help="Enable audio playback")
    parser.add_argument("--mute", action="store_true", help="Disable audio even if --sound is set")
    parser.add_argument("--grayscale", action="store_true", help="Render without color")

    args = parser.parse_args()
    enable_audio = args.sound and not args.mute

    play_video_as_ascii(args.video, args.width, enable_audio, args.grayscale)

if __name__ == "__main__":
    main()
