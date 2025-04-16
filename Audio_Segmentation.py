from pydub import AudioSegment, silence
import os

def segment_audio(audio_path, min_silence_len=1000, silence_thresh=-40, skip_initial=10000):
    audio = AudioSegment.from_file(audio_path)

    # Skip the first 10 seconds
    audio = audio[skip_initial:]

    # Detect non-silent chunks
    chunks = silence.split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=300  # preserves prosodic features
    )

    # Extract the directory of the input file
    input_dir = os.path.dirname(audio_path)

    # Define a subdirectory called "segmented_chunks"
    output_dir = os.path.join(input_dir, "segmented_chunks")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Use base name of input file for chunk naming
    base_name = os.path.splitext(os.path.basename(audio_path))[0]

    for i, chunk in enumerate(chunks):
        output_chunk_path = os.path.join(output_dir, f"{base_name}_chunk_{i}.wav")
        chunk.export(output_chunk_path, format="wav")

    print(f" Segmentation complete: {len(chunks)} chunks saved in '{output_dir}'.")

# Example usage
audio_path = r"C:\Users\nadee\Downloads\Download (audio-extractor.net).mp3"
segment_audio(audio_path, min_silence_len=500, silence_thresh=-40, skip_initial=80000) 
