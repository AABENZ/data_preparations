from pydub import AudioSegment
import os

def convert_audio(audio_file):
    sound = AudioSegment.from_file(audio_file)
    sound = sound.set_frame_rate(16000)
    sound = sound.set_channels(1)
    sound = sound.set_sample_width(2)
    sound.export(audio_file, format="wav")

def process_data(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get a list of all files in the input folder
    files = os.listdir(input_folder)

    for file in files:
        if file.endswith(".mp4"):
            # Convert the audio file to WAV format
            audio_file = os.path.join(input_folder, file)
            convert_audio(audio_file)

            # Load the converted audio file
            sound_file = AudioSegment.from_file(audio_file, format="wav")

            chunk_length_ms = 15000  # 12 seconds
            initial_chunks = sound_file[::chunk_length_ms]

            # Silence splitting settings
            min_silence_len = 500  # Minimum silence length in milliseconds
            silence_thresh = sound_file.dBFS - 16  # Silence threshold in dBFS

            for i, initial_chunk in enumerate(initial_chunks):
                chunks = silence.split_on_silence(initial_chunk, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
                for j, chunk in enumerate(chunks):
                    chunk_name = os.path.join(output_folder, f'{os.path.splitext(file)[0]}_chunk{i}.wav')
                    chunk.export(chunk_name, format="wav")

input_folder = "/content/drive/MyDrive/tunisian_corpora/unlabled_audios/raw"
output_folder = "/content/drive/MyDrive/tunisian_corpora/unlabled_audios/result"

process_data(input_folder, output_folder)