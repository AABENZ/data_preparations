# Audio Processing Script

This script performs audio processing tasks such as extracting transcripts from XML files and then slicing the audio files.

Usage:

1. Place your XML files in the 'xml' directory.
2. The script performs the following tasks:
	- Extracts data from XML files in the 'xml' directory.
	- Processes the extracted data to create text files in the 'text' directory.
	- Slices the audio waveforms based on the extracted data and saves the sliced waveforms as individual WAV files in a separate directory.
	- Generates a CSV file named 'output.csv'
