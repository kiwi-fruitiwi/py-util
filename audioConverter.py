import os
from pydub import AudioSegment


def convert_flac_to_wav(folder_path):
    # ensure the folder path ends with a slash
    if not folder_path.endswith('/'):
        folder_path += '/'

    # list all files in the directory
    files = os.listdir(folder_path)

    # iterate through all files
    for file in files:
        if file.endswith('.m4a'):
            # define full file paths
            flac_path = os.path.join(folder_path, file)
            wav_path = os.path.join(folder_path, file.replace('.m4a', '.wav'))

            # convert FLAC to WAV
            audio = AudioSegment.from_file(flac_path, format="m4a")
            audio.export(wav_path, format="wav")

            print(f"Converted {file} to {wav_path}")


# replace 'your_folder_path' with the path to your folder containing FLAC files
convert_flac_to_wav('c:/botw')