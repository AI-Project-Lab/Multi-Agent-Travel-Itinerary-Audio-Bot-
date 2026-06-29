from genai_voice.processing.audio import Audio
import time

print("Initializing Audio...")
audio = Audio()

print("Testing communicate('Hello world')...")
try:
    audio.communicate("Hello world. This is a test of the audio system.")
    print("Communicate finished.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")

print("Done.")
