import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading  # Import the threading module
from PIL import Image, ImageTk  # Import Image and ImageTk from PIL (Pillow)
from datetime import datetime
import os
from frogcast_transcription.transcribe_audio_whisper import transcribe_and_output_text


class AudioTranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcription with Timestamps")

        original_logo = Image.open("/Users/mikedaly/frogcast_transcription/daly_joe_frogcast_logo.png")
        resized_logo = original_logo.resize((150, 150), Image.ANTIALIAS)
        self.logo_image = ImageTk.PhotoImage(resized_logo)

        self.logo_label = tk.Label(root, image=self.logo_image)
        self.logo_label.grid(row=0, column=0, rowspan=3, padx=10, pady=0)

        self.label = tk.Label(root, text="Selected audio file:")
        self.label.grid(row=0, column=1, columnspan=2, padx=10, pady=10)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.config(bg="light blue")  # Set button background color
        self.browse_button.grid(row=0, column=3, padx=10, pady=10)

        self.audio_path_label = tk.Label(root, text="")
        self.audio_path_label.grid(row=1, column=1, columnspan=2, padx=10, pady=10)

        self.output_label = tk.Label(root, text="Select output folder:")
        self.output_label.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

        self.output_folder_button = tk.Button(root, text="Browse", command=self.browse_output_folder)
        self.output_folder_button.config(bg="light blue")  # Set button background color
        self.output_folder_button.grid(row=2, column=3, padx=10, pady=10)

        self.output_folder_label = tk.Label(root, text="")
        self.output_folder_label.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

        self.transcribe_button = tk.Button(root, text="Transcribe", command=self.transcribe_audio)
        self.transcribe_button.config(bg="light blue")  # Set button background color
        self.transcribe_button.grid(row=4, column=1, columnspan=2, padx=10, pady=10)

        self.transcription_text = tk.Text(root, wrap=tk.WORD, height=10, width=60)  # Text widget for displaying transcription
        self.transcription_text.grid(row=5, column=0, columnspan=4, padx=10, pady=10, sticky="ew")  # Use sticky option to expand widget horizontally

        # Adjust grid row and column weights for better layout management
        for i in range(6):  # Number of rows
            self.root.grid_rowconfigure(i, weight=1)

        for i in range(4):  # Number of columns
            self.root.grid_columnconfigure(i, weight=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.m4a")])
        if file_path:
            self.audio_path = file_path
            self.audio_path_label.config(text=file_path)

    def browse_output_folder(self):
        output_folder = filedialog.askdirectory()
        if output_folder:
            self.output_folder = output_folder
            self.output_folder_label.config(text=output_folder)

    def transcribe_audio(self):
        if hasattr(self, "audio_path") and hasattr(self, "output_folder"):
            # Open the wait indicator window
            self.wait_window = tk.Toplevel(self.root)
            self.wait_window.title("Please wait...")
            self.wait_label = ttk.Label(self.wait_window, text="Transcribing, please wait...")
            self.wait_label.pack(padx=20, pady=20)

            # Use threading to run the transcribe_audio function in the background
            threading.Thread(target=self.transcribe_and_close_wait).start()

    def transcribe_and_close_wait(self):
        audio_base_name = os.path.basename(self.audio_path)
        audio_name_without_extension = os.path.splitext(audio_base_name)[0]

        current_date = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"{audio_name_without_extension}_transcription_{current_date}.txt"

        transcribe_and_output_text(audio_path=self.audio_path, output_folder=self.output_folder, output_filename=output_filename)

        # Display the transcribed text in the text widget
        with open(os.path.join(self.output_folder, output_filename), "r") as file:
            transcription_text = file.read()
            self.transcription_text.delete("1.0", tk.END)  # Clear existing text
            self.transcription_text.insert(tk.END, transcription_text)  # Insert transcribed text

        # Close the wait indicator window after the subprocess completes
        self.wait_window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriptionApp(root)
    root.mainloop()
