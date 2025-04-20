import os
from pydub import AudioSegment
import whisper
from phonemizer import phonemize
import json

# --- CONFIGURATIONS --- #
DATASET_DIR = r"C:\\Your\\Dataset\\Path"  # Set your dataset path here
MIN_DURATION_MINUTES = 10
TARGET_PHONEMES = set([
    'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش',
    'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه',
    'و', 'ي', 'ء', 'آ', 'أ', 'إ', 'ئ', 'ؤ', 'ى', 'ة'
])  # Common Arabic characters as phoneme approximations

# --- UTILITY FUNCTIONS --- #
def is_valid_audio(file_path):
    """
    Automated quality assessment:
    This checks that each audio file can be loaded and is longer than 1 second.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) > 1000  # Valid if more than 1 second
    except:
        print("Audio is too short, should be atleast 1 second")
        return False

def get_total_duration(dataset_path):
    """
    Calculates the total duration of valid audio files.
    Used for minimum viable sample determination.
    """
    total = 0
    for file in os.listdir(dataset_path):
        if file.endswith(('.wav', '.mp3', '.ogg')):
            path = os.path.join(dataset_path, file)
            audio = AudioSegment.from_file(path)
            total += len(audio)
    return total / 1000  # seconds

def transcribe_file(path, model):
    """
    Uses Whisper to transcribe Arabic speech from audio files.
    Required for extracting phonemes.
    """
    result = model.transcribe(path, language='ar')
    return result['text']

def extract_phonemes(text):
    """
    Phonetic coverage verification:
    Converts transcribed text into a set of Arabic characters.
    """
    try:
        phonemes = phonemize(text, language='ar', backend='espeak', strip=True, punctuation_marks=';:,.!?')
        phoneme_set = set(phonemes.replace(' ', ''))
        return phoneme_set
    except:
        return set()

# --- MAIN VALIDATION FUNCTION --- #
def validate_dataset(dataset_dir):
    model = whisper.load_model("base")
    results = {
        "valid_files": [],
        "invalid_files": [],  # Identification of problematic samples
        "total_duration_sec": 0,
        "phonemes_covered": set(),  # Phonetic coverage verification
        "missing_phonemes": set(),
        "recommendations": []  # Recommendations for additional recordings
    }

    for file in os.listdir(dataset_dir):
        if not file.endswith((".wav", ".mp3", ".ogg")):
            continue

        path = os.path.join(dataset_dir, file)

        if not is_valid_audio(path):
            results['invalid_files'].append(file)
            continue

        text = transcribe_file(path, model)
        phonemes = extract_phonemes(text)

        results['valid_files'].append(file)
        results['phonemes_covered'].update(phonemes)

    duration = get_total_duration(dataset_dir)
    results['total_duration_sec'] = duration

    # Minimum viable sample determination
    if duration < MIN_DURATION_MINUTES * 60:
        results['recommendations'].append(
            f"Dataset is too short. Add at least {MIN_DURATION_MINUTES - duration // 60:.1f} more minutes of audio.")

    # Phonetic coverage verification
    missing = TARGET_PHONEMES - results['phonemes_covered']
    if missing:
        results['missing_phonemes'] = list(missing)
        results['recommendations'].append(
            f"Missing phonemes: {', '.join(missing)}. Add sentences containing these.")

    # Save report with all validation results
    with open("validation_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("Validation complete. Report saved to validation_report.json")

# Run the validation
if __name__ == "__main__":
    validate_dataset(DATASET_DIR)
    print("Dataset validation completed.")