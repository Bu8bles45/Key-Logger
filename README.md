Keylogger with Screenshot Capture


Description

This Python script logs keystrokes and periodically captures screenshots. It records key presses into a text file and provides a function to analyze the logged data. Screenshots are saved as image files at regular intervals.


Features

Logs all key presses into a keylogger.txt file

Captures screenshots every 5 seconds

Analyzes logged data to count words and characters

Runs in the background with multi-threading support

Stops when the Esc key is released


Requirements

Ensure you have the following dependencies installed:

pip install pynput pillow

Usage


Run the script using:

python keylogger.py


Stopping the Keylogger

Press the Esc key to stop the keylogging process.


Analyzing Logs

Once the script is stopped, you can analyze the logged key data by running:

python keylogger.py


The analysis will display word frequencies and total characters logged.


File Output

Keystrokes: Stored in keylogger.txt

Screenshots: Saved as screenshot_1.png, screenshot_2.png, etc.


Disclaimer

This tool is for educational and authorized security research purposes only. Unauthorized use of keylogging software is illegal and may result in legal consequences. Use responsibly and only with proper consent.

