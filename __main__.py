import os
import argparse
from pydub import AudioSegment
from modules import (
    format_standardization,
    silence_detection,
    normalization,
    clarity_enhancement,
    segmentation,
)


def is_audio_file(filename):
    return any(
        filename.lower().endswith(ext)
        for ext in [".wav", ".mp3", ".flac", ".aac", ".m4a", ".ogg"]
    )


def process_all_audios(input_dir: str, save_steps: bool):
    input_dir = os.path.abspath(input_dir)

    for filename in os.listdir(input_dir):
        path = os.path.join(input_dir, filename)

        if not os.path.isfile(path) or not is_audio_file(filename):
            continue

        print(f"\nProcessing file: {filename}")

        # Step 1: Format Standardization
        audio = format_standardization.process_audio(
            file_path=path,
            save=save_steps,
            target_sample_rate=16000,
            target_bit_depth=16,
            target_channels=1,
        )

        segmentation.segment_audio(
            audio=audio, file_path=path, output_dir=f"{input_dir}/segmented"
        )

        for file in os.listdir(f"{input_dir}/segmented"):
            file_path = os.path.join(f"{input_dir}/segmented", file)

            if not os.path.isfile(file_path) or not is_audio_file(file):
                continue

            print(f"\nProcessing chunk: {file}")
            # Step 2: Silence Removal
            audio = silence_detection.process_audio(
                file_path=file_path, save=save_steps
            )

            # Step 3: Volume Normalization
            audio = normalization.process_audio(
                audio=audio, file_path=file_path, save=save_steps
            )

            # Step 4: Clarity Enhancement
            audio = clarity_enhancement.process_audio(
                audio=audio, file_path=file_path, save=save_steps
            )

            # Save the processed audio
            output_dir = os.path.join(input_dir, "processed")
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, file)
            audio.export(output_file_path, format="wav")
            print(f"Processed audio saved to: {output_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio Processing Pipeline")
    parser.add_argument(
        "directory",
        type=str,
        help="Relative path to the directory containing audio files.",
    )
    parser.add_argument(
        "--save_steps",
        action="store_true",
        help="If set, saves intermediate results after each processing step.",
    )

    args = parser.parse_args()

    process_all_audios(
        input_dir=args.directory,
        save_steps=args.save_steps,
    )
