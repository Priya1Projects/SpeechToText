import os
from pydub import AudioSegment

def convert_to_mono(input_file, output_file):
    """Converts an audio file to mono using pydub.

    Args:
        input_file (str): Path to the input audio file.
        output_file (str): Path to save the mono audio file.
    """
    try:
        audio = AudioSegment.from_file(input_file)
        mono_audio = audio.set_channels(1)
        mono_audio.export(output_file, format="wav")  # Ensure output is WAV
        print(f"Converted '{input_file}' to mono: '{output_file}'")
    except Exception as e:
        print(f"Error converting '{input_file}': {e}")

if __name__ == "__main__":
    input_directory = "C:\\Users\\priya\\Documents\\code\\audiosamples"  # Replace with the path to your audio files
    output_directory = "C:\\Users\\priya\\Documents\\code"  # Replace with the desired output directory

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.endswith((".wav", ".mp3", ".flac", ".ogg")):  # Add other formats if needed
            input_filepath = os.path.join(input_directory, filename)
            output_filename = f"mono_{filename}"
            output_filepath = os.path.join(output_directory, output_filename)
            convert_to_mono(input_filepath, output_filepath)

    print("Conversion to mono completed.")