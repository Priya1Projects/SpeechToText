from pydub import AudioSegment
import os

def convert_m4a_to_wav(start_num, end_num, directory="."):
    """
    Converts a range of M4A files to WAV format.

    Args:
        start_num (int): The starting number of the M4A files (e.g., 1 for "1.m4a").
        end_num (int): The ending number of the M4A files (e.g., 100 for "100.m4a").
        directory (str, optional): The directory where the M4A files are located
            and where the WAV files will be saved. Defaults to the current directory.
    """
    for i in range(start_num, end_num + 1):
        m4a_file = os.path.join(directory, f"{i}.m4a")
        wav_file = os.path.join(directory, f"{i}.wav")

        if not os.path.exists(m4a_file):
            print(f"Error: File not found: {m4a_file}")
            continue  # Skip to the next file if this one doesn't exist

        try:
            sound = AudioSegment.from_file(m4a_file, format="m4a")
            sound.export(wav_file, format="wav")
            print(f"Converted: {m4a_file} to {wav_file}")
        except Exception as e:
            print(f"Error converting {m4a_file}: {e}")

if __name__ == "__main__":
    # Convert files named 1.m4a to 100.m4a in the current directory
    current_directory = os.getcwd()
    convert_m4a_to_wav(1, 100, directory=current_directory)

    # If your files are in a different directory, specify it here:
    # convert_m4a_to_wav(1, 100, directory="/path/to/your/m4a/files")