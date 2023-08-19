import speech_recognition as sr
from pydub import AudioSegment
from loguru import logger
from tqdm import tqdm


def convert_m4a_to_wav(m4a_audio_path: str, wav_audio_path: str = "converted_audio.wav"):
    # Convert m4a to wav
    logger.info(f"Converting {m4a_audio_path} to {wav_audio_path}")
    audio = AudioSegment.from_file(m4a_audio_path, format="m4a")
    audio.export(wav_audio_path, format="wav")
    return wav_audio_path


def transcribe_audio_with_timestamps(audio_path: str):
    # Set up the recognizer
    recognizer = sr.Recognizer()

    # Convert m4a to wav file
    wav_audio_file = convert_m4a_to_wav(m4a_audio_path=audio_path)

    # Load the audio file
    audio = AudioSegment.from_wav(wav_audio_file)

    # Initialize variables for speaker and timestamp tracking
    current_speaker = None
    start_timestamp = 0
    end_timestamp = 0

    transcription_text = []

    logger.info(f"Begin processing {wav_audio_file}")
    # Recognize speech in chunks and add timestamps for each new speaker
    for chunk_start in tqdm(range(0, len(audio), 10000), desc="Transcribe audio"):  # Process audio in 10-second chunks
        chunk = audio[chunk_start:chunk_start + 10000]

        with sr.AudioFile(chunk.export(format="wav")) as chunk_audio_file:
            audio_data = recognizer.record(chunk_audio_file)

            try:
                recognized_text = recognizer.recognize_google(audio_data)

                if recognized_text:  # Non-empty text recognized
                    if current_speaker is None:
                        current_speaker = recognized_text
                        start_timestamp = chunk_start / 1000  # Convert milliseconds to seconds
                    elif current_speaker != recognized_text:
                        transcription_text.append(f"Speaker: {current_speaker} | "
                                            f"Start: {start_timestamp:.2f}s | "
                                            f"End: {end_timestamp:.2f}s")
                        current_speaker = recognized_text
                        start_timestamp = chunk_start / 1000
            except sr.UnknownValueError:
                pass  # Ignore unrecognized chunks

            end_timestamp = (chunk_start + 10000) / 1000  # Convert milliseconds to seconds

    # Write the last segment
    transcription_text.append(f"Speaker: {current_speaker} | "
                        f"Start: {start_timestamp:.2f}s | "
                        f"End: {end_timestamp:.2f}s")

    return "\n".join(transcription_text)


if __name__ == "__main__":
    audio_path = "/Users/mikedaly/Desktop/Daly_Joe_Frogcast_Episode_0.m4a"  #"path_to_your_audio_file.wav"
    transcription = transcribe_audio_with_timestamps(audio_path)

    output_path = "transcribed_text_with_timestamps.txt"
    with open(output_path, "w") as output_file:
        output_file.write(transcription)

    print(f"Transcription with timestamps completed. Output saved to {output_path}")
