#!pip install tqdm
#!pip install PyArabic

import pyarabic.araby as araby
import pandas as pd
from tqdm import tqdm
import os
import xml.etree.ElementTree as ET
import numpy as np
import re
import torchaudio
import csv

def corrected_extract_data(filename):

    # Parse the XML file and get the root element
    tree = ET.parse(filename)
    root = tree.getroot()

    # Extract the base name of the input file without the file extension
    file_name = os.path.splitext(os.path.basename(filename))[0]

    # Create the "text" folder if it doesn't exist
    output_folder = "text"
    os.makedirs(output_folder, exist_ok=True)

    # Modify the output file path to include the folder and match the input file name
    output_file = os.path.join(output_folder, f"{file_name}.txt")

    # Find all elements with the tag name "event" and "tli"
    events = root.findall(".//event")
    tlis = root.findall(".//tli")

    # Define a list of pause markers
    pauses = ["(تنفس)", "(موسِيقى)", "(تصفيق)", "musique", "(ضحك)", "(تنَفسْ)", "(ضجيج)" ]

    # Define the maximum allowed duration
    duration_max = 10.5

    # Initialize variables
    start_time = "0"
    end_time = "0"
    text_add = ''
    fist_start_time = True

    # Initialize a variable to store the accumulated duration
    duration = 0

    # Iterate over each event element
    for disc in events:
        # Add a space to the accumulated text
        text_add += " "
        # Check if the event text is a pause marker, if yes relace it with "#"
        if disc.text in pauses or np.sum([x in disc.text for x in pauses]):
            disc.text = "#"
        flag_disc = True

        # Iterate over each tli element
        for time_ID in tlis:
            # Check if the start time of the event matches the id of the tli
            if disc.get('start') == time_ID.get('id') :
                # Get the start time of the event
                start_event = time_ID.get("time")

                # Check if it's the first start time
                if fist_start_time == True:
                    # Update the start time and accumulated text
                    start_time = time_ID.get('time')
                    text_add = " "+disc.text+" "
                    fist_start_time = False

                # Check if the event text is a pause
                if disc.text == "#" :
                    # Get the end time of the event
                    end_time = time_ID.get('time')
                    # Calculate the duration between the start and end time
                    final_duration = str(float(start_event) - float(start_time))
                    # Prepare the output data
                    data_out = "Sentence:  " + text_add.replace("#"," ") + "\n" + 'Start time: ' + start_time + "\n" + 'End time: ' + start_event + "\n" + 'Duration: ' + final_duration + "\n\n"
                    # Reset variables for the next event
                    duration=0
                    fist_start_time = True

                    # Write the data to the output file if the accumulated text is not "#"
                    if text_add != "#" :
                        with open(output_file, "a", encoding="utf-8") as f:
                          f.write(data_out)

            else:
                if flag_disc == True:
                    text_add += disc.text
                    flag_disc = False

            # Check if the end time of the event matches the id of the tli
            if disc.get('end') == time_ID.get('id') :
                # Get the end time of the event
                end_event = time_ID.get('time')

        # Update the accumulated duration
        duration += float(end_event) - float(start_event)

        # Check if the accumulated duration exceeds the maximum allowed duration
        if duration >duration_max :
            # Calculate the duration between the start time and end time
            final_duration = str(float(end_event) - float(start_time))
            # Prepare the output data
            data_out = "Sentence:  " + text_add.replace("#"," ") + "\n" + 'Start time: ' + start_time + "\n" + 'End time: ' + end_event + "\n" + 'Duration: ' + final_duration + "\n\n"
            # Reset variables for the next event
            duration=0
            fist_start_time = True

            # Write the data to the output file if the accumulated text is not "#"
            if text_add != "#" :
                with open(output_file, "a", encoding="utf-8") as f:
                  f.write(data_out)

def process_xml_files_in_folder(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)

    # Filter only XML files
    xml_files = [file for file in files if file.endswith('.xml')]

    # Process each XML file using the corrected_extract_data function
    for xml_file in xml_files:
        xml_file_path = os.path.join(folder_path, xml_file)
        corrected_extract_data(xml_file_path)

process_xml_files_in_folder("./xml")

def slice_waveform(input_file,text_file):

    # Load the text file
    with open(text_file, 'r') as file:
        data = file.read()

    # Splitting the data by new lines
    first_split_by_new_line = data.split("\n")

    # Extract the sentence from the text file
    sentences = re.findall('Sentence: (.+)', data)
    #Remove diacritics
    sentences  = [araby.strip_diacritics(x) for x in list(sentences)]

    #Extract the start times
    start_times = re.findall('Start time: (.+)', data)
    start_times = [float(element.strip()) for element in start_times]

    #Extract the end times
    end_times = re.findall('End time: (.+)', data)
    end_times = [float(element.strip()) for element in end_times]

    #Extract the durations
    durations = re.findall('Duration: (.+)', data)
    durations = [float(element.strip()) for element in durations]

    # Cleaning the extracted strings
    cleaned_strings = []

    for input_string in sentences:
        # Replace [lan:FR, word] pattern with <fr>word</fr>
        cleaned_text = re.sub(r'\[lan:FR, (.*?)\]', r'<fr>\1</fr>', input_string)

        # Replace [lan:MSA, word] pattern with the word directly
        cleaned_text = re.sub(r'\[lan:MSA, (.*?)\]', r'\1', cleaned_text)

        # Replace [lan:EN, word] pattern with <en>word</en>
        cleaned_text = re.sub(r'\[lan:EN, (.*?)\]', r'<en>\1</en>', cleaned_text)

        # Replace <word, tag> pattern for Arabic words (including spaces) with the word directly
        cleaned_text = re.sub(r'<(.*?)[,،]\s*.*?>', r'\1', cleaned_text)

        # # Remove Punctuation marks
        cleaned_text = re.sub(r'[.,?؟!;:"()\[\]{}\-…&*%$#@+\=÷]', '', cleaned_text)
        
        #Lower case characters
        cleaned_text = re.sub(r'[A-Z]', lambda match: match.group().lower(), cleaned_text)

        # # Replace multiple spaces with a single space
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

        cleaned_strings.append(cleaned_text)

    # Load the WAV file
    waveform, sample_rate = torchaudio.load(input_file)

    # Create the output directory if it doesn't exist
    output_dir = f"{os.path.splitext(input_file)[0]}_chunks"
    os.makedirs(output_dir, exist_ok=True)

    #Get file name
    file_name = os.path.splitext(os.path.basename(input_file))[0]

    # Initializing an empty list to store CSV lines
    csvs=[]

    #Iterate over the start and end times and slice the waveform
    for i, (start_time, end_time, duration, sentence) in enumerate(zip(start_times, end_times, durations, cleaned_strings)):

        # Calculate the number of letters per second
        if duration > 0 :
            letters_per_second = len(sentence) / duration
        else :
            letters_per_second = 0

        # Checking the duration and letters per second
        if (1.5 <= duration <= 12) and (letters_per_second > 3):
          # Convert start and end times to sample indices
          start_index = int(start_time * sample_rate)
          end_index = int(end_time * sample_rate)

          # Slice the waveform
          sliced_waveform = waveform[:, start_index:end_index]
          # print(sliced_waveform.shape)

          # Save the sliced waveform to a new WAV file in the current directory
          output_file = f"{output_dir}/{file_name}_chunk_{i}.wav"
          torchaudio.save(output_file, sliced_waveform, sample_rate)

          # Create a CSV line for the sliced waveform
          csv_line = [
                      output_file,
                      str(duration),
                      output_file,
                      sentence
                  ]
          csvs.append(csv_line)
    return csvs

def prepare_buckeye(audio_dir, text_dir):
    csv_lines = [["ID", "duration", "wav", "wrd"]]

    # Iterate over the files in the audio directory
    for filename in tqdm(os.listdir(audio_dir)):
        if not filename.endswith(".wav"):
            continue

        # Get the file name without the extension
        fname = filename.split(".")[0]
        # Construct the paths for the audio file and the corresponding text file
        audio_file = os.path.join(audio_dir, filename)
        text_file = os.path.join(text_dir, f"{fname}.txt")

        # Check if the text file exists
        if os.path.exists(text_file):
            # Call the slice_waveform function to process the audio and text files
            csv_from_wrd = slice_waveform(audio_file, text_file)
            # Append the resulting CSV lines to the main list
            csv_lines += csv_from_wrd
        else:
            # Print error if the text file is not found
            print(f"Text file not found for {filename}. Expected file: {text_file}")

    # Write the CSV lines to the final CSV file
    with open("output.csv", mode="w") as csv_f:
        csv_writer = csv.writer(
            csv_f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in csv_lines:
            csv_writer.writerow(line)

prepare_buckeye("./audio","./text")

