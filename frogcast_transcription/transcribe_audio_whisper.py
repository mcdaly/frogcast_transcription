from pydub import AudioSegment
from loguru import logger
import whisper
import os


def transcribe_and_output_text(audio_path: str, output_filepath: str = None, whisper_model: str = "base", timestamp_increment_s: float = 30):
    transcription = transcribe_audio_with_timestamps(audio_path, whisper_model=whisper_model, timestamp_increment_s=timestamp_increment_s)

    if output_filepath is None:
        output_filepath = "transcribed_text_with_timestamps.txt"

    # Check if the output folder exists, and create parent directories if not
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    with open(output_filepath, "w") as output_file:
        output_file.write(transcription)

    logger.success(f"Transcription with timestamps completed.\nOutput saved to {output_filepath}")


def transcribe_audio_with_timestamps(audio_path: str, whisper_model: str = "base", timestamp_increment_s: float = 30):
    # Convert m4a to wav file
    wav_audio_file = convert_m4a_to_wav(audio_path=audio_path)

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
                    f"Start: {current_group['start']:.2f}s | "
                    f"End: {current_group['end']:.2f}s | "
                    f"Text: {' '.join(current_group['texts'])}"
                )
            current_group = {'start': start_time, 'end': end_time, 'texts': []}
            cur_time = end_time

        current_group['texts'].append(text)
        current_group['end'] = end_time

    if current_group['texts']:
        formatted_text.append(
            f"Start: {current_group['start']:.2f}s | "
            f"End: {current_group['end']:.2f}s | "
            f"Text: {' '.join(current_group['texts'])}"
        )

    return "\n".join(formatted_text)


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
