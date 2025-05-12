import cv2
import time
import argparse
import threading
import pygame
import os


# TESTIRANJE KOMITA

from moviepy import (
    VideoFileClip)

ASCII_CHARS_GRAY = [' ', '.', '\'', '`', '^', '"', ',', ':', ';', '!', 'i',
                    'l', '*', '+', '=', '#', '%', '@']
ASCII_CHARS_COLOR = [' ', '.', ':', '+', '*', 'e', 's', '#']


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
    height, original_width, _ = frame.shape
    char_aspect = 11 / 24  # Character width to height ratio
    aspect_ratio = original_width / height
    new_height = int(width / aspect_ratio * char_aspect)
    resized = cv2.resize(
        frame, (width, new_height), interpolation=cv2.INTER_AREA
    )

    luminances = []
    for row in resized:
        for b, g, r in row:
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            luminances.append(lum)
    min_lum = min(luminances)
    max_lum = max(luminances)

    if max_lum - min_lum < 1:
        max_lum = min_lum + 1

    ascii_lines = []
    charset = ASCII_CHARS_GRAY if grayscale else ASCII_CHARS_COLOR

    for row in resized:
        line = ""
        for b, g, r in row:
            raw_lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            norm_lum = (raw_lum - min_lum) / (max_lum - min_lum)
            adj_lum = adjust_luminance(norm_lum * 255)
            char = pixel_to_ascii(adj_lum, charset)
            line += colored_ascii(char, r, g, b, grayscale)
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
    frames = [
        frame for frame in clip.iter_frames(fps=fps, dtype="uint8")
    ]

    audio_thread = None
    if enable_audio:
        clip.audio.write_audiofile(audio_path)
        audio_thread = threading.Thread(
            target=play_audio_sync, args=(audio_path,)
        )
        audio_thread.start()

    start_time = time.time()

    print("\033[?25l", end="")  # Hide cursor
    print("\033[2J", end="")  # Clear screen
    try:
        next_frame_time = start_time
        for i in range(len(frames)):
            elapsed = time.time() - start_time
            expected_frame = int(elapsed * fps)
            if expected_frame >= len(frames):
                break

            frame_bgr = cv2.cvtColor(frames[expected_frame], cv2.COLOR_RGB2BGR)
            ascii_frame = frame_to_ascii_color(frame_bgr, width, grayscale)

            print("\033[H", end="")  # Move cursor
            print(ascii_frame)
            print("\033[J", end="")

            next_frame_time += 1 / fps
            sleep_time = next_frame_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        print("\033[?25h", end="")
        pygame.mixer.music.stop()
        if audio_thread:
            audio_thread.join()
        clip.close()
        if enable_audio and os.path.exists(audio_path):
            os.remove(audio_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video",
                        help="Path to video file")
    parser.add_argument("--width",
                        type=int, default=80,
                        help="ASCII output width")
    parser.add_argument("--sound",
                        action="store_true",
                        help="Enable audio playback")
    parser.add_argument("--mute",
                        action="store_true",
                        help="Disable audio even if --sound is set")
    parser.add_argument("--grayscale",
                        action="store_true",
                        help="Render without color")

    args = parser.parse_args()
    enable_audio = args.sound and not args.mute

    play_video_as_ascii(args.video, args.width, enable_audio, args.grayscale)


if __name__ == "__main__":
    main()
