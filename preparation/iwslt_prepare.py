import os
import sys
import numpy as np
import random
from tqdm import tqdm
import csv
import pandas as pd
import torch
import torchaudio
import pyarabic.araby as araby
torchaudio.set_audio_backend("soundfile")
​
min_length = 12
min_duration = 1
audio_folder  = "/gpfsscratch/rech/nou/uzn19yk/LDC2022E01_IWSLT22_Tunisian_Arabic_Shared_Task_Training_Data/data/audio/ta/"
text_folder = "/gpfsscratch/rech/nou/uzn19yk/LDC2022E01_IWSLT22_Tunisian_Arabic_Shared_Task_Training_Data/data/transcripts/ta/"
​
def treat_file(filename, out_audios):
    example_file = os.path.join(text_folder, filename+".tsv")
    initial_wav_path = os.path.join(audio_folder, filename+".sph")
    print(initial_wav_path)
    initial_wav,sr = torchaudio.load(initial_wav_path)
    initial_wav = torch.squeeze(initial_wav)
    table = pd.read_csv(example_file, sep='\t', names=["start", "end", "jesaispas", "words"])
    table['words'] = table['words'].astype('str')
    table["words"] = [araby.strip_diacritics(x) for x in list(table["words"])]
​
    table['start'] = table['start'].astype('float')
    table['end'] = table['end'].astype('float')
​
    mask = (table['words'].str.len() > min_length)
​
    table = table.loc[mask]
    mask = (table['end'] - table["start"] > min_duration)
    table = table.loc[mask]
    table = table[~table['words'].str.contains('O')]
    table = table[~table['words'].str.contains('-')]
​
    csvs=[]
    for index, row in table.iterrows():
        start_int = int(row["start"] * 8000)
        end_int = int(row["end"] * 8000)
        duration = row["end"] - row["start"]
        wav = initial_wav[start_int:end_int]
        save_path = os.path.join(out_audios, filename+"_"+str(index)+".wav")
        torchaudio.save(save_path, wav.unsqueeze(0), 8000)
        csv_line = [
            filename+"_"+str(index),
            str(duration),
            save_path,
            8000,
            row["words"]
        ]
        csvs.append(csv_line)
    return csvs
​
def prepare_buckeye(audio_dir, audio_out, csv_file):
​
​
    csv_lines = [["ID", "duration", "wav", "sr", "wrd"]]
    for filename in tqdm(os.listdir(audio_dir)):
        fname = filename.split(".")[0]
        csv_from_wrd = treat_file(fname, audio_out)
        csv_lines += csv_from_wrd
    with open(csv_file, mode="w") as csv_f:
        csv_writer = csv.writer(
            csv_f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
​
        for line in csv_lines:
            csv_writer.writerow(line)
​
​
if __name__=="__main__":
    out_audios = sys.argv[1]
    wavs_dir = sys.argv[2]
    if not os.path.exists(out_audios):
        os.makedirs(out_audios)
    prepare_buckeye(wavs_dir,out_audios, csv_file)
