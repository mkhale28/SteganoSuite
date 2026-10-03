# Test script
print("Testing modules...")
import sys
sys.path.append('modules')

from modules.image_stego import ImageStego
from modules.audio_stego import AudioStego
from modules.video_stego import VideoStego
from modules.document_stego import DocumentStego

print("✅ All modules imported successfully!")
print("\nReady to run main.py")