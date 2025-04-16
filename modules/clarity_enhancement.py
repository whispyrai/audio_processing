# clarity_enhancement.py

import os
from typing import Optional
from pydub import AudioSegment, effects
import scipy.signal as signal
import numpy as np
import torch
from df.enhance import enhance, init_df

# Load DeepFilterNet once to reduce overhead.
DF_MODEL, DF_STATE, _ = init_df()


def high_pass_filter(audio: AudioSegment, cutoff: float = 80.0) -> AudioSegment:
    """
    Applies a high-pass filter to remove low-frequency noise (rumble).

    Args:
        audio (AudioSegment): The input audio segment.
        cutoff (float): Cutoff frequency in Hz. Defaults to 80 Hz.

    Returns:
        AudioSegment: Filtered audio segment.
    """
    samples = np.array(audio.get_array_of_samples())
    sos = signal.butter(10, cutoff, "hp", fs=audio.frame_rate, output="sos")
    filtered = signal.sosfilt(sos, samples).astype(np.int16)
    return audio._spawn(filtered.tobytes())


def neural_noise_reduction(audio: AudioSegment) -> AudioSegment:
    """
    Performs noise reduction using DeepFilterNet neural network.

    Args:
        audio (AudioSegment): The input audio segment.

    Returns:
        AudioSegment: Noise-reduced audio.
    """
    samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
    samples_tensor = torch.from_numpy(samples).unsqueeze(0)
    enhanced_tensor = enhance(DF_MODEL, DF_STATE, samples_tensor)
    enhanced_samples = enhanced_tensor.squeeze(0).numpy() * 32768.0
    enhanced_samples = enhanced_samples.clip(-32768, 32767).astype(np.int16)
    return audio._spawn(enhanced_samples.tobytes())


def apply_equalization(audio: AudioSegment) -> AudioSegment:
    """
    Applies equalization to enhance vocal clarity by emphasizing the speech frequency band.

    Args:
        audio (AudioSegment): The input audio segment.

    Returns:
        AudioSegment: Equalized audio.
    """
    audio = effects.low_pass_filter(audio, 5000)  # Reduce harshness above 5 kHz
    audio = effects.high_pass_filter(audio, 2000)  # Remove muddiness below 2 kHz
    audio += 3  # Slight overall presence boost
    return audio


def apply_limiter(audio: AudioSegment, max_dbfs: float = -1.0) -> AudioSegment:
    """
    Limits the audio peaks to prevent clipping.

    Args:
        audio (AudioSegment): The input audio segment.
        max_dbfs (float): Maximum allowed dBFS after limiting. Defaults to -1.0 dBFS.

    Returns:
        AudioSegment: Peak-limited audio.
    """
    peak = audio.max_dBFS
    if peak > max_dbfs:
        audio = audio.apply_gain(max_dbfs - peak)
    return audio


def process_audio(
    file_path: Optional[str] = None,
    *,
    audio: Optional[AudioSegment] = None,
    save: bool = False,
) -> AudioSegment:
    """
    Entry-point for voice clarity enhancement pipeline.

    Args:
        file_path (str, optional): Path to the input audio file if audio is not provided.
        audio (AudioSegment, optional): Pre-loaded audio segment to process.
        save (bool): If True and file_path is provided, saves the enhanced audio to disk.

    Returns:
        AudioSegment: The enhanced audio segment.

    Raises:
        ValueError: If neither file_path nor audio is provided, or if save is True without file_path.
    """
    if audio is None and file_path is None:
        raise ValueError("Provide either file_path or audio.")

    # Load audio if needed
    if audio is None:
        audio = AudioSegment.from_file(file_path)

    # Step 1: Remove low-frequency rumble
    audio = high_pass_filter(audio)

    # Step 2: Neural-based noise reduction (DeepFilterNet)
    audio = neural_noise_reduction(audio)

    # Step 3: Equalization to enhance clarity
    audio = apply_equalization(audio)

    # Step 4: Limit peaks to avoid clipping
    audio = apply_limiter(audio)

    # Optionally save the enhanced audio
    if save:
        if file_path is None:
            raise ValueError("save=True but file_path is not provided.")

        input_dir = os.path.dirname(file_path)
        output_dir = os.path.join(input_dir, "clarity-enhanced")
        os.makedirs(output_dir, exist_ok=True)

        base = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, f"{base}_clarity_enhanced.wav")

        audio.export(output_path, format="wav")
        print(f"Enhanced audio saved as: {output_path}")

    return audio
