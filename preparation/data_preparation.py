#This Script prepare the annotation tool & collection tool datasets

import os
import pandas as pd
import torchaudio

folder_path = "path_to_dataset_folder"

# List all files in the folder
files = os.listdir(folder_path)

# Separate .wav and .txt files
wav_files = sorted([file for file in files if file.endswith('.wav')])
txt_files = sorted([file for file in files if file.endswith('.txt')])

# Initialize an empty DataFrame with the desired columns
df = pd.DataFrame(columns=['ID', 'wav', 'wrd', 'duration'])

# Iterate through the .wav and .txt files and populate the DataFrame
for wav_file, txt_file in zip(wav_files, txt_files):
    # Get the ID (file name without extension)
    file_id = os.path.splitext(wav_file)[0]

    # Get the .wav file path
    wav_path = os.path.join(folder_path, wav_file)

    # Get the .txt file path and read its content
    txt_path = os.path.join(folder_path, txt_file)
    with open(txt_path, 'r',encoding="utf-8") as f:
        txt_content = f.read().strip()

    # Calculate the duration of the .wav file using torchaudio
    waveform, sample_rate = torchaudio.load(wav_path)
    duration = waveform.size(1) / sample_rate

    # Append the data to the DataFrame
    df = df.append({'ID': file_id, 'wav': wav_path, 'wrd': txt_content, 'duration': duration}, ignore_index=True)

# Save the DataFrame as a CSV file
df.to_csv('output2.csv', index=False)
