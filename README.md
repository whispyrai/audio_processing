# 🎧 Audio Format Processor for Voice Cloning (Fish Speech Compatible)

This project is a Python-based audio preprocessing utility designed to **analyze and convert audio files** into the standard format required by **voice cloning systems**—particularly compatible with **Fish Speech** requirements.

It ensures audio files meet strict criteria by:
- Detecting current format
- Converting to standard sample rate, bit depth, and channels
- Handling corrupted or incompatible audio gracefully

---

## 🐟 Fish Speech Format Requirements

Voice cloning systems like Fish Speech require audio in the following format:

- **Sample Rate**: 44.1 kHz
- **Bit Depth**: 16-bit (or 24-bit)
- **Channels**: Stereo (2 channels)
- **Format**: WAV

This tool prepares any supported audio file (e.g., MP3, WAV) for use in these systems.

---

## 🚀 Features

- 🔍 Detects audio format using:
  - **fleep** (byte-level analysis)
  - **pydub.mediainfo**
- 🛠 Converts:
  - Sample Rate → 44.1 kHz
  - Bit Depth → 16-bit or 24-bit
  - Mono ↔ Stereo channels
- 🔐 Validates audio integrity before processing
- ⚠️ Error handling for:
  - Corrupt files
  - Unsupported formats
- 📤 Exports output as high-quality `.wav`

---

## 📁 Functions Overview

### `detect_audio_format_fleep(file_path: str) -> Optional[str]`
- **Description**: Uses the `fleep` library to detect the file format by analyzing its first 128 bytes.
- **Input**: `file_path` – path to the audio file.
- **Output**: Audio format extension (e.g., "mp3") or `None`.

---

### `detect_audio_format_mediainfo(file_path: str) -> Optional[str]`
- **Description**: Retrieves format details using `pydub.utils.mediainfo`.
- **Input**: `file_path` – path to the audio file.
- **Output**: Format name (e.g., "mp3", "wav") or `None`.

---

### `check_audio_integrity(file_path: str) -> bool`
- **Description**: Checks if the file is a valid, readable, and non-empty audio file.
- **Input**: `file_path` – path to the audio file.
- **Output**: `True` if the audio is valid, raises an error otherwise.

---

### `convert_sample_rate(audio: AudioSegment, target_sample_rate: int) -> AudioSegment`
- **Description**: Converts the sample rate of the audio.
- **Input**: 
  - `audio` – the audio segment.
  - `target_sample_rate` – desired sample rate (e.g., 44100).
- **Output**: Modified `AudioSegment` with the new sample rate.

---

### `convert_bit_depth(audio: AudioSegment, target_bit_depth: int) -> AudioSegment`
- **Description**: Converts the bit depth of the audio.
- **Input**: 
  - `audio` – the audio segment.
  - `target_bit_depth` – must be 16 or 24.
- **Output**: Modified `AudioSegment` with the new bit depth.

---

### `convert_channels(audio: AudioSegment, target_channels: int) -> AudioSegment`
- **Description**: Converts the number of channels (mono/stereo).
- **Input**: 
  - `audio` – the audio segment.
  - `target_channels` – 1 (mono) or 2 (stereo).
- **Output**: Modified `AudioSegment` with the new channel count.

---

### `process_audio_file(file_path: str, target_sample_rate: int = 44100, target_bit_depth: int = 16, target_channels: int = 2) -> None`
- **Description**: Orchestrates the full audio pipeline: detection, integrity check, conversion, and saving output.
- **Input**:
  - `file_path` – path to the original audio file.
  - `target_sample_rate` – default is 44100 Hz.
  - `target_bit_depth` – default is 16-bit.
  - `target_channels` – default is 2 (stereo).
- **Output**: None (writes converted file to disk).

---


