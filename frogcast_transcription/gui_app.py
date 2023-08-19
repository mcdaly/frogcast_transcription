import tkinter as tk
from tkinter import filedialog
import subprocess


class AudioTranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcription with Timestamps")

        self.label = tk.Label(root, text="Select an audio file:")
        self.label.pack(pady=10)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.pack()

        self.transcribe_button = tk.Button(root, text="Transcribe", command=self.transcribe_audio)
        self.transcribe_button.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        if file_path:
            self.audio_path = file_path

    def transcribe_audio(self):
        if hasattr(self, "audio_path"):
            subprocess.run(["python", "transcription_script.py", self.audio_path])


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriptionApp(root)
    root.mainloop()
