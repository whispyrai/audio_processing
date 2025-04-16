from pydub import AudioSegment
from pydub.utils import mediainfo
import fleep
import os


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
        with open(file_path, "rb") as file:
            info = fleep.get(file.read(128))
            if info.type and "audio" in info.type:
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
        return info.get("format_name", None)
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


def process_audio(
    file_path=None,
    *,
    audio=None,
    target_sample_rate: int = 48_000,
    target_bit_depth: int = 24,
    target_channels: int = 1,
    save: bool = False,
):
    """
    Entry‑point for the format‑standardization module.
    It can now be used in two ways:

    1. Pipeline mode (in‑memory)  ➜  pass `audio` (AudioSegment)
    2. Stand‑alone  / debug mode  ➜  pass `file_path` (str)

    Parameters
    ----------
    file_path : str | None
        Path to the original audio file on disk.  Required if `audio` is
        not provided.  When `save=True`, the processed file is written
        next to this path inside a "format-standardized/" sub‑folder.
    audio : AudioSegment | None
        In‑memory audio from a previous pipeline stage.  Supply this
        instead of `file_path` when chaining modules.
    target_sample_rate : int
        Desired sample‑rate in Hz (default 48 kHz).
    target_bit_depth : int
        Desired bit‑depth (16 or 24; default 24).
    target_channels : int
        Desired number of channels (1 = mono, 2 = stereo; default 1).
    save : bool
        If True **and** `file_path` is given, write the converted file
        to "<input_dir>/format-standardized/<name>_format_standardized.wav".

    Returns
    -------
    AudioSegment
        The processed (format‑standardized) audio.
    """
    # ------------------------------------------------------------------ #
    # 0. Basic validation
    # ------------------------------------------------------------------ #
    if audio is None and file_path is None:
        raise ValueError("Provide either `file_path` or `audio`.")

    # ------------------------------------------------------------------ #
    # 1. If we received only a file path, load & analyse it
    # ------------------------------------------------------------------ #
    if audio is None:
        print(f"Processing: {file_path}")

        # --- format / integrity diagnostics (for debug clarity) -------- #
        try:
            fmt_fleep = detect_audio_format_fleep(file_path)
            print(f"Format detected by fleep: {fmt_fleep}")
        except Exception as e:
            print(e)

        try:
            fmt_media = detect_audio_format_mediainfo(file_path)
            print(f"Format detected by mediainfo: {fmt_media}")
        except Exception as e:
            print(e)

        try:
            if check_audio_integrity(file_path):
                print("Audio file is valid and not corrupted.")
        except Exception as e:
            print(e)

        # --- actually load the audio ---------------------------------- #
        audio = AudioSegment.from_file(file_path)

    # ------------------------------------------------------------------ #
    # 2. Convert sample‑rate, bit‑depth, channels
    # ------------------------------------------------------------------ #
    audio = convert_sample_rate(audio, target_sample_rate)
    audio = convert_bit_depth(audio, target_bit_depth)
    audio = convert_channels(audio, target_channels)

    # ------------------------------------------------------------------ #
    # 3. Optionally save to disk (only possible if we know the origin)
    # ------------------------------------------------------------------ #
    if save:
        if file_path is None:
            raise ValueError(
                "save=True was requested but no `file_path` supplied. "
                "Either provide the path of the original file or set save=False."
            )

        input_dir = os.path.dirname(file_path)
        output_dir = os.path.join(input_dir, "format-standardized")
        os.makedirs(output_dir, exist_ok=True)

        base = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, f"{base}_format_standardized.wav")
        print(f"Converted file will be saved at: {output_path}")
        audio.export(output_path, format="wav")
        print(f"Audio file successfully saved as: {output_path}")

    # ------------------------------------------------------------------ #
    # 4. Return the processed AudioSegment so the pipeline can continue
    # ------------------------------------------------------------------ #
    return audio
