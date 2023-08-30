from frogcast_transcription.gui_app import AudioTranscriptionApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriptionApp(root)
    root.mainloop()
