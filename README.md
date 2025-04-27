# Audio Processing Pipeline

A modular audio processing pipeline for voice-focused enhancement, noise reduction, normalization, and segmentation. Built using Python and `pydub`, with integration of neural noise suppression (DeepFilterNet).

## 📁 Repository Structure

```
.
├── modules/
│   ├── clarity_enhancement.py         # Neural denoising, EQ, limiting
│   ├── format_standardization.py      # Sample rate, bit depth, channel consistency
│   ├── normalization.py               # dBFS loudness normalization
│   ├── silence_detection.py           # Removes silence from speech
│   └── segmentation.py                # Splits speech into chunks
├── audio_processing.py                # Pipeline entry point (CLI)
└── README.md                          # Documentation
```

## 🧠 Features
- Format-independent input support (WAV, MP3, FLAC, etc.)
- Noise reduction using DeepFilterNet
- Equalization and peak limiting for speech clarity
- Silence trimming
- Loudness normalization
- Optional segmentation into speech chunks
- Configurable via command-line

## ⚙️ Requirements

- Python 3.8+
- FFmpeg (required by `pydub`)

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

You may need to install `ffmpeg` via your system package manager:

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg
```

## 🚀 Usage

### Run the pipeline
```bash
python audio_processing.py <path-to-directory> [--save_steps]
```

### Example
```bash
python audio_processing.py ./samples --save_steps
```

This will:
1. Find all audio files in `./samples`
2. Standardize format, remove silence, normalize, and enhance clarity
3. Save intermediate files if `--save_steps` is specified

### Output Structure
```
samples/
├── yourfile.wav
├── format-standardized/
├── silence-removed/
├── normalized/
├── clarity-enhanced/
├── segmented/
```

## ✨ Modules Overview

### `format_standardization.py`
- Ensures consistent sample rate, bit depth, and channel format

### `silence_detection.py`
- Removes long silences to tighten speech pacing

### `normalization.py`
- Brings all audio to a consistent target dBFS

### `clarity_enhancement.py`
- Applies:
  - High-pass filter
  - DeepFilterNet neural noise reduction
  - EQ boost for 2-5kHz (speech clarity)
  - Peak limiting

### `segmentation.py`
- Splits the final audio into chunks at silence points (optional)

## 🧪 Recommended Settings
| Flag          | Purpose                          | Recommended |
|---------------|-----------------------------------|-------------|
| `--save_steps`| For debugging and inspection      | ✅           |

---

Built for scalable and modular audio preprocessing in voice-first AI systems.

