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


def process_audio(
    file_path=None,
    *,
    audio=None,
    silence_thresh: int = -40,
    min_silence_len: int = 1000,
    save: bool = False,
):
    """
    Entry‑point for the silence‑detection / removal stage.

    Parameters
    ----------
    file_path : str | None
        Path to an audio file on disk.  Required if `audio` is not given.
        When `save=True`, the silence‑removed file is written next to
        this path inside a "silence-removed/" sub‑folder.
    audio : AudioSegment | None
        In‑memory audio from a previous pipeline step.  Supply this
        instead of `file_path` when chaining modules.
    silence_thresh : int
        Silence threshold in dBFS (default ‑40 dB).
    min_silence_len : int
        Minimum length of a silent region (ms) (default 1000 ms).
    save : bool
        If True **and** `file_path` is supplied, write the processed file
        to disk as "<input_dir>/silence-removed/<name>_silence_removed.wav".

    Returns
    -------
    AudioSegment
        The audio with silent sections removed, suitable for the next
        step in the pipeline.
    """
    # --------------------------------------------------------------- #
    # 0. Validate inputs
    # --------------------------------------------------------------- #
    if audio is None and file_path is None:
        raise ValueError("Provide either `file_path` or `audio`.")

    # --------------------------------------------------------------- #
    # 1. Load if necessary
    # --------------------------------------------------------------- #
    if audio is None:
        audio = AudioSegment.from_file(file_path)

    # --------------------------------------------------------------- #
    # 2. Detect non‑silent segments
    # --------------------------------------------------------------- #
    non_silent_segments = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
    )
    print(f"Found {len(non_silent_segments)} non-silent segments.")

    # --------------------------------------------------------------- #
    # 3. Recombine into a single track
    # --------------------------------------------------------------- #
    processed_audio = AudioSegment.empty()
    for segment in non_silent_segments:
        processed_audio += segment

    # --------------------------------------------------------------- #
    # 4. Optionally save to disk
    # --------------------------------------------------------------- #
    if save:
        if file_path is None:
            raise ValueError(
                "save=True was requested but no `file_path` supplied. "
                "Either pass the original path or set save=False."
            )
        input_dir = os.path.dirname(file_path)
        output_dir = os.path.join(input_dir, "silence-removed")
        os.makedirs(output_dir, exist_ok=True)

        base = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, f"{base}_silence_removed.wav")
        processed_audio.export(output_path, format="wav")
        print(f"New audio file saved as: {output_path}")

    # --------------------------------------------------------------- #
    # 5. Return result for further pipeline stages
    # --------------------------------------------------------------- #
    return processed_audio
