from pydub import AudioSegment
from loguru import logger
import whisper
import os


def transcribe_and_output_text(audio_path: str, output_filepath: str = None, whisper_model: str = "base", timestamp_increment_s: float = 30):
    transcription_text = transcribe_audio_with_timestamps(audio_path, whisper_model=whisper_model, timestamp_increment_s=timestamp_increment_s)

    if output_filepath is None:
        output_filepath = "transcribed_text_with_timestamps.txt"

    # Check if the output folder exists, and create parent directories if not
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    with open(output_filepath, "w") as output_file:
        output_file.write(transcription_text)

    logger.success(f"Transcription with timestamps completed.\nOutput saved to {output_filepath}")


def transcribe_audio_with_timestamps(audio_path: str, whisper_model: str = "base", timestamp_increment_s: float = 30):
    # Convert m4a to wav file
    try:
        wav_audio_file = convert_m4a_to_wav(audio_path=audio_path)
    except Exception as e:
        print("Error during audio conversion:", e)
        raise e  # Reraise the exception to see the full traceback

    model = whisper.load_model(whisper_model)
    result = model.transcribe(wav_audio_file, verbose=True)

    final_text = format_transcription(transcription_data=result["segments"],
                                      interval=timestamp_increment_s)
    return final_text


def format_transcription(transcription_data, interval: float = 30):
    formatted_text = []
    current_group = None
    cur_time = 0

    for entry in transcription_data:
        start_time = entry['start']
        end_time = entry['end']
        text = entry['text']

        if current_group is None:
            current_group = {'start': start_time, 'end': end_time, 'texts': []}

        if cur_time + interval < current_group['end']:
            if current_group['texts']:
                formatted_text.append(
                    f"Start: {format_time(current_group['start'])} | "
                    f"End: {format_time(current_group['end'])} | "
                    f"Text: {' '.join(current_group['texts'])}"
                )
            current_group = {'start': start_time, 'end': end_time, 'texts': []}
            cur_time = end_time

        current_group['texts'].append(text)
        current_group['end'] = end_time

    if current_group['texts']:
        formatted_text.append(
            f"Start: {format_time(current_group['start'])} | "
            f"End: {format_time(current_group['end'])} | "
            f"Text: {' '.join(current_group['texts'])}"
        )

    return "\n\n".join(formatted_text)


def format_time(seconds: int) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_str = f"{(seconds % 60):.0f}"
    seconds_zero_padded = seconds_str.zfill(2)  # Total of 2 characters (including decimal point)
    return f"{hours:02d}:{minutes:02d}:{seconds_zero_padded}"


def convert_m4a_to_wav(audio_path: str, wav_audio_path: str = "converted_audio.wav"):
    # Convert m4a to wav
    logger.info(f"Converting {audio_path} to {wav_audio_path}")
    file_extension = os.path.splitext(audio_path)[1][1:]
    audio = AudioSegment.from_file(audio_path, format=file_extension)
    audio.export(wav_audio_path, format="wav")
    return wav_audio_path


if __name__ == "__main__":
    audio_path = "/Users/mikedaly/Desktop/Daly_Joe_Frogcast_Episode_0.m4a"
    transcription = transcribe_audio_with_timestamps(audio_path)

    output_path = "transcribed_text_with_timestamps.txt"
    with open(output_path, "w") as output_file:
        output_file.write(transcription)

    print(f"Transcription with timestamps completed. Output saved to {output_path}")
