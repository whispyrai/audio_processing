from pydub import AudioSegment
from pydub.silence import split_on_silence
import os


def detect_silent_segments(audio_path, silence_thresh=-40, min_silence_len=1000):
    """
    Detects silent segments in an audio file.

    :param audio_path: str, path to the audio file.
    :param silence_thresh: int, the silence threshold in dBFS (default -40dB).
    :param min_silence_len: int, minimum length of silence to be considered (in ms).
    :return: list of tuples, where each tuple is (start, end) of the silent segments.
    """
    audio = AudioSegment.from_file(audio_path)

    # Detect silent segments
    silent_segments = split_on_silence(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
    )

    # The resulting silent segments will be the parts of the audio that are silent
    print(f"Found {len(silent_segments)} non-silent segments.")
    return silent_segments


def save_audio_without_silence(audio_path, silent_segments):
    """
    Saves the new audio without the silent segments in the specified output directory.

    :param audio_path: str, path to the original audio file.
    :param silent_segments: list of non-silent audio segments.
    :param output_name: str, the new file name (without extension).
    """
    # Extract the directory of the input file
    input_dir = os.path.dirname(audio_path)

    # Define a subdirectory names "silence-removed"
    output_dir = os.path.join(input_dir, "silence-removed")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create the directory if it doesn't exist

    # Create the output file path
    output_name = os.path.splitext(os.path.basename(audio_path))[0] + "_silence_removed"
    output_path = os.path.join(output_dir, f"{output_name}.wav")

    # Combine all the non-silent segments into one audio file
    audio_without_silence = AudioSegment.empty()
    for segment in silent_segments:
        audio_without_silence += segment

    # Export the new audio without silence
    audio_without_silence.export(output_path, format="wav")
    print(f"New audio file saved as: {output_path}")


def process_audio(audio_path):
    """
    Process the audio file by detecting silent segments and saving the audio without the silent parts.

    :param audio_path: str, path to the audio file.
    """
    # Detect silent segments
    silent_segments = detect_silent_segments(audio_path)

    # Save the new audio without the silent segments
    save_audio_without_silence(
        audio_path,
        silent_segments,
    )
