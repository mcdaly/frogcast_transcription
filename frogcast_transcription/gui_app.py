import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading  # Import the threading module
from PIL import Image, ImageTk  # Import Image and ImageTk from PIL (Pillow)
from datetime import datetime
import os
import subprocess
import sys
import io
from frogcast_transcription.transcribe_audio_whisper import transcribe_and_output_text
from frogcast_transcription.definitions import LOGO_FILEPATH


class TextRedirector(io.TextIOBase):
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        self.widget.insert(tk.END, s)
        self.widget.see(tk.END)  # Scroll to the end
        self.widget.update_idletasks()


class AudioTranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcribe Audio")

        original_logo = Image.open(LOGO_FILEPATH)
        resized_logo = original_logo.resize((150, 150), Image.ANTIALIAS)
        self.logo_image = ImageTk.PhotoImage(resized_logo)

        self.logo_label = tk.Label(root, image=self.logo_image)
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        self.model_size_label = tk.Label(root, text="Model Size:")
        self.model_size_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.model_size_var = tk.StringVar(value="base")
        self.model_size_options = ["tiny", "base", "small", "medium", "large"]
        self.model_size_dropdown = ttk.Combobox(root, textvariable=self.model_size_var, values=self.model_size_options, width=8, state="readonly")
        self.model_size_dropdown.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.time_interval_label = tk.Label(root, text="Time Interval (seconds):")
        self.time_interval_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.time_interval_var = tk.IntVar(value=30)
        self.time_interval_spinbox = tk.Spinbox(root, textvariable=self.time_interval_var, from_=1, to=300, width=8, state="readonly")
        self.time_interval_spinbox.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.browse_button = tk.Button(root, text="Select Audio File", command=self.browse_file)
        self.browse_button.config(bg="light blue")
        self.browse_button.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.audio_path_label = tk.Label(root, text="")
        self.audio_path_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.output_folder_button = tk.Button(root, text="Select Output Directory", command=self.browse_output_folder)
        self.output_folder_button.config(bg="light blue")
        self.output_folder_button.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.output_folder_label = tk.Label(root, text="")
        self.output_folder_label.grid(row=1, column=2, padx=10, pady=10, sticky="w")

        self.transcribe_button = tk.Button(root, text="Transcribe", command=self.transcribe_audio)
        self.transcribe_button.config(bg="light blue")
        self.transcribe_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.open_text_button = tk.Button(root, text="Open Transcribed File", command=self.open_text_file)
        self.open_text_button.config(bg="light blue")
        self.open_text_button.grid(row=2, column=2, padx=10, pady=10, sticky="ew")

        self.transcription_text = tk.Text(root, wrap=tk.WORD, height=10, width=80)  # Increase width of Text widget
        self.transcription_text.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Redirect terminal output to the text widget
        sys.stdout = TextRedirector(self.transcription_text)

        # Adjust grid row and column weights for better layout management
        for i in range(5):  # Number of rows
            self.root.grid_rowconfigure(i, weight=1)

        for i in range(3):  # Number of columns
            self.root.grid_columnconfigure(i, weight=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.m4a")])
        if file_path:
            self.audio_path = file_path
            self.audio_path_label.config(text=file_path)

            self.output_folder = os.path.join(os.path.dirname(self.audio_path), "transcriptions")
            self.output_folder_label.config(text=self.output_folder)

    def browse_output_folder(self):
        initial_dir = self.get_initial_output_directory()
        output_folder = filedialog.askdirectory(initialdir=initial_dir)

        if output_folder:
            self.output_folder = output_folder
            self.output_folder_label.config(text=output_folder)

    def get_initial_output_directory(self):
        if hasattr(self, "audio_path"):
            return os.path.dirname(self.audio_path)
        else:
            return os.getcwd()

    def transcribe_audio(self):
        if hasattr(self, "audio_path") and hasattr(self, "output_folder"):
            # Use threading to run the transcribe_audio function in the background
            threading.Thread(target=self.transcribe_and_close_wait).start()

    def transcribe_and_close_wait(self):
        audio_base_name = os.path.basename(self.audio_path)
        audio_name_without_extension = os.path.splitext(audio_base_name)[0]

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        output_filename = f"{audio_name_without_extension}_transcription_{current_date}.txt"
        output_filepath = os.path.join(self.output_folder, output_filename)

        model_size = self.model_size_var.get()
        time_interval = self.time_interval_var.get()

        transcribe_and_output_text(audio_path=self.audio_path, output_filepath=output_filepath,
                                   whisper_model=model_size, timestamp_increment_s=time_interval)

        # Display the transcribed text in the text widget
        with open(os.path.join(self.output_folder, output_filename), "r") as file:
            transcription_text = file.read()
            self.transcription_text.delete("1.0", tk.END)
            self.transcription_text.insert(tk.END, transcription_text)

    def open_text_file(self):
        if hasattr(self, "output_folder"):
            audio_base_name = os.path.basename(self.audio_path)
            audio_name_without_extension = os.path.splitext(audio_base_name)[0]
            current_date = datetime.now().strftime("%Y-%m-%d")
            output_filename = f"{audio_name_without_extension}_transcription_{current_date}.txt"
            text_file_path = os.path.join(self.output_folder, output_filename)

            if os.path.exists(text_file_path):
                subprocess.run(["open", text_file_path], check=True)  # Open the file with the default text editor/browser


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriptionApp(root)
    root.mainloop()
