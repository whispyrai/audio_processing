from pydub import AudioSegment, silence
import os
from typing import Optional


def segment_audio(
    file_path: Optional[str] = None,
    *,
    audio: Optional[AudioSegment] = None,
    min_silence_len: int = 1400,
    silence_thresh: int = -40,
    skip_initial: int = 0,
    output_dir: str = "segmented",
    file_name: str = "audio_chunk",
):
    """
    Segments audio into chunks based on silence.

    Args:
        file_path (str, optional): Path to the audio file if audio is not provided.
        audio (AudioSegment, optional): In-memory audio to segment.
        min_silence_len (int): Minimum silence length to consider (ms).
        silence_thresh (int): Threshold for silence detection (dBFS).
        skip_initial (int): Duration to skip from the start (ms).
        output_dir (str): Directory to save segmented chunks.

    Raises:
        ValueError: If neither file_path nor audio is provided.

    Returns:
        List[AudioSegment]: The list of audio chunks.
    """
    if audio is None and file_path is None:
        raise ValueError("Provide either file_path or audio.")

    # Load audio if not provided
    if audio is None:
        audio = AudioSegment.from_file(file_path)

    # Skip initial specified duration
    audio = audio[skip_initial:]

    # Segment audio on silence
    chunks = silence.split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=300,
    )

    # Set up output directory
    os.makedirs(output_dir, exist_ok=True)

    # Determine base name for output chunks
    base_name = (
        os.path.splitext(os.path.basename(file_path))[0] if file_path else file_name
    )

    # Save chunks
    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(output_dir, f"{base_name}_chunk_{i}.wav")
        chunk.export(chunk_path, format="wav")

    print(f"Segmentation complete: {len(chunks)} chunks saved in '{output_dir}'.")

    return chunks
