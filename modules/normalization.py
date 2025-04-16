"""
volume_normalization.py
-----------------------

Ensure consistent loudness across audio files or in‑memory AudioSegment
objects.  Designed for use inside a multi‑step processing pipeline, so
saving to disk is optional.

Dependencies
------------
pip install pydub
# and make sure ffmpeg/avlib is on the system path.
"""

from __future__ import annotations

import os
from typing import Optional
from pydub import AudioSegment


# ----------------------------------------------------------------------
# Utility helpers
# ----------------------------------------------------------------------


def _loudness_dbfs(audio: AudioSegment) -> float:
    """Return average loudness (dBFS) for an AudioSegment."""
    return audio.dBFS


def _apply_peak_limit(
    audio: AudioSegment,
    peak_limit_dbfs: float,
) -> AudioSegment:
    """
    Ensure *peak* level does not exceed `peak_limit_dbfs`.
    If it does, lower the entire signal by the necessary amount.
    """
    peak = audio.max_dBFS
    if peak > peak_limit_dbfs:
        audio = audio.apply_gain(peak_limit_dbfs - peak)
    return audio


def _export_if_requested(
    audio: AudioSegment,
    input_path: Optional[str],
    output_suffix: str,
    save: bool,
    subdir: str = "normalized",
) -> None:
    """
    Save `audio` next to `input_path` inside `<subdir>/`
    only if `save` is True **and** we have a valid `input_path`.
    """
    if not save:
        return

    if input_path is None:
        raise ValueError(
            "Cannot save audio because `input_path` is None. "
            "Either supply the original file path or set save=False."
        )

    in_dir = os.path.dirname(input_path)
    out_dir = os.path.join(in_dir, subdir)
    os.makedirs(out_dir, exist_ok=True)

    basename, _ = os.path.splitext(os.path.basename(input_path))
    out_path = os.path.join(out_dir, f"{basename}{output_suffix}.wav")
    audio.export(out_path, format="wav")


# ----------------------------------------------------------------------
# Core normalisation routine
# ----------------------------------------------------------------------


def normalize_audio(
    *,
    audio: Optional[AudioSegment] = None,
    input_path: Optional[str] = None,
    target_dbfs: float = -20.0,
    peak_limit_dbfs: float = -1.0,
    save: bool = False,
) -> AudioSegment:
    """
    Normalize loudness and optionally save the result.

    Parameters
    ----------
    audio
        In memory AudioSegment. Provide **either** this *or* `input_path`.
    input_path
        Path to an audio file on disk.
    target_dbfs
        Desired average loudness after normalization.
    peak_limit_dbfs
        Maximum allowed peak after processing.
    save
        If True and `input_path` is supplied, write a copy to
        `<input_dir>/normalized/<basename>_normalized.wav`.

    Returns
    -------
    AudioSegment
        The processed (normalized + limited) audio.
    """
    # ------------------------------------------------------------------
    # 1. Load / validate input
    # ------------------------------------------------------------------
    if audio is None and input_path is None:
        raise ValueError("Provide either `audio` or `input_path`.")

    if audio is None:  # load from disk
        audio = AudioSegment.from_file(input_path)

    # ------------------------------------------------------------------
    # 2. Loudness normalisation (RMS‑based dBFS)
    # ------------------------------------------------------------------
    gain_needed = target_dbfs - _loudness_dbfs(audio)
    audio = audio.apply_gain(gain_needed)

    # ------------------------------------------------------------------
    # 3. Peak limiting
    # ------------------------------------------------------------------
    audio = _apply_peak_limit(audio, peak_limit_dbfs)

    # ------------------------------------------------------------------
    # 4. Save if requested
    # ------------------------------------------------------------------
    _export_if_requested(
        audio=audio,
        input_path=input_path,
        output_suffix="_normalized",
        save=save,
        subdir="normalized",
    )

    return audio


# ----------------------------------------------------------------------
# Pipeline entry point
# ----------------------------------------------------------------------


def process_audio(
    *,
    audio: Optional[AudioSegment] = None,
    file_path: Optional[str] = None,
    target_dbfs: float = -20.0,
    peak_limit_dbfs: float = -1.0,
    save: bool = False,
) -> AudioSegment:
    """
    Entry point used by the pipeline.

    Simply forwards to `normalize_audio` so that each module in
    the pipeline exposes the same function signature.
    """

    return normalize_audio(
        audio=audio,
        input_path=file_path,
        target_dbfs=target_dbfs,
        peak_limit_dbfs=peak_limit_dbfs,
        save=save,
    )
