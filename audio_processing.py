from pydub import AudioSegment
from pydub.utils import mediainfo
import fleep
import os

audio_file_path = r"C:\Users\nadee\Downloads\AR_M_Ahmed.mp3"  

# Takes the first 128 bytes to make sure it's an audio file
def detect_audio_format_fleep(file_path):
    """
    Detects the audio format using fleep (byte-level analysis).

    Args:
        file_path (str): The path to the audio file.

    Returns:
        str: File extension (e.g., 'mp3', 'wav') if recognized as audio.

    Raises:
        ValueError: If the file is not recognized as an audio file or detection fails.
    """
    try:
        with open(file_path, 'rb') as file:
            info = fleep.get(file.read(128))
            if info.type and 'audio' in info.type:
                return info.extension[0] if info.extension else None
            else:
                raise ValueError("File is not recognized as an audio file by fleep.")
    except Exception as e:
        raise ValueError(f"fleep detection failed: {e}")

# Detects the audio type
def detect_audio_format_mediainfo(file_path):
    """
    Detects the audio format using pydub's mediainfo utility.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        str: Format name as reported by mediainfo (e.g., 'mp3', 'wav').

    Raises:
        ValueError: If format detection fails.
    """
    try:
        info = mediainfo(file_path)
        return info.get('format_name', None)
    except Exception as e:
        raise ValueError(f"mediainfo detection failed: {e}")

def check_audio_integrity(file_path):
    """
    Checks if the audio file is valid (not empty or corrupted).

    Args:
        file_path (str): The path to the audio file.

    Returns:
        bool: True if the audio file is valid and has non-zero length.

    Raises:
        ValueError: If the audio is unreadable or empty.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        if len(audio) == 0:
            raise ValueError("Audio file is empty.")
        return True
    except Exception as e:
        raise ValueError(f"Audio file integrity check failed: {e}")

# Converts to the wanted sample rate (usually 44.1kHz)
def convert_sample_rate(audio, target_sample_rate):
    """
    Converts the sample rate of the audio if needed.

    Args:
        audio (AudioSegment): The audio object to convert.
        target_sample_rate (int): Desired sample rate in Hz.

    Returns:
        AudioSegment: Audio with the updated sample rate.
    """
    if audio.frame_rate != target_sample_rate:
        audio = audio.set_frame_rate(target_sample_rate)
        print(f"Converted sample rate to {target_sample_rate} Hz.")
    return audio

# Only accepts 16 or 24 (16 is the most commonly used depth)
def convert_bit_depth(audio, target_bit_depth):
    """
    Converts the bit depth of the audio to 16 or 24 bits.

    Args:
        audio (AudioSegment): The audio object to convert.
        target_bit_depth (int): Target bit depth (16 or 24).

    Returns:
        AudioSegment: Audio with the new bit depth.

    Raises:
        ValueError: If an unsupported bit depth is provided.
    """
    if target_bit_depth == 16:
        audio = audio.set_sample_width(2)
    elif target_bit_depth == 24:
        audio = audio.set_sample_width(3)
    else:
        raise ValueError("Only 16-bit and 24-bit conversions are supported.")
    print(f"Converted bit depth to {target_bit_depth}-bit.")
    return audio

def convert_channels(audio, target_channels):
    """
    Converts the audio to the specified number of channels.

    Args:
        audio (AudioSegment): The audio object to convert.
        target_channels (int): Number of desired audio channels (1 for mono, 2 for stereo).

    Returns:
        AudioSegment: Audio with the desired number of channels.
    """
    if audio.channels != target_channels:
        audio = audio.set_channels(target_channels)
        print(f"Converted to {target_channels} channels.")
    return audio

def process_audio_file(file_path, target_sample_rate=44100, target_bit_depth=16, target_channels=2):
    """
    Processes the audio file: detects format, checks integrity, and performs conversions.

    Args:
        file_path (str): Path to the input audio file.
        target_sample_rate (int, optional): Desired sample rate in Hz (default is 44100).
        target_bit_depth (int, optional): Desired bit depth (16 or 24, default is 16).
        target_channels (int, optional): Desired number of channels (default is 2).

    Returns:
        None
    """
    print(f"Processing: {file_path}")
    
    try:
        format_fleep = detect_audio_format_fleep(file_path)
        print(f"Format detected by fleep: {format_fleep}")
    except Exception as e:
        print(e)

    try:
        format_mediainfo = detect_audio_format_mediainfo(file_path)
        print(f"Format detected by mediainfo: {format_mediainfo}")
    except Exception as e:
        print(e)

    try:
        if check_audio_integrity(file_path):
            print("Audio file is valid and not corrupted.")
    except Exception as e:
        print(e)

    try:
        audio = AudioSegment.from_file(file_path)

        # Perform conversions
        audio = convert_sample_rate(audio, target_sample_rate)
        audio = convert_bit_depth(audio, target_bit_depth)
        audio = convert_channels(audio, target_channels)

        # Ensure the directory exists for saving the converted file
        output_dir = "C:/Converted/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)  # Create the directory if it doesn't exist

        # Construct the output file path
        output_path = f"{output_dir}converted_{os.path.basename(file_path)}"
        print(f"Converted file will be saved at: {output_path}")
        
        # Export the audio in WAV format
        audio.export(output_path, format="wav")
        print(f"Audio file successfully saved as: {output_path}")

    except Exception as e:
        print(f"Conversion failed: {e}")

if __name__ == "__main__":
    process_audio_file(audio_file_path)
