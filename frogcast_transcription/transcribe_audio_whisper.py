from pydub import AudioSegment
from loguru import logger
import whisper
import os


def transcribe_and_output_text(audio_path: str, output_folder: str = None, output_filename: str = None, timestamp_increment_s: float = 30):
    transcription = transcribe_audio_with_timestamps(audio_path, timestamp_increment_s)

    output_filename = "transcribed_text_with_timestamps.txt" if output_filename is None else output_filename
    if output_folder is None:
        output_filepath = output_filename
    else:
        output_filepath = os.path.join(output_folder, output_filename)
    with open(output_filepath, "w") as output_file:
        output_file.write(transcription)

    logger.success(f"Transcription with timestamps completed. Output saved to {output_filepath}")


def transcribe_audio_with_timestamps(audio_path: str, timestamp_increment_s: float = 30):
    # Convert m4a to wav file
    wav_audio_file = convert_m4a_to_wav(m4a_audio_path=audio_path)

    model = whisper.load_model("base")
    result = model.transcribe(wav_audio_file)

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


def convert_m4a_to_wav(m4a_audio_path: str, wav_audio_path: str = "converted_audio.wav"):
    # Convert m4a to wav
    logger.info(f"Converting {m4a_audio_path} to {wav_audio_path}")
    audio = AudioSegment.from_file(m4a_audio_path, format="m4a")
    audio.export(wav_audio_path, format="wav")
    return wav_audio_path


if __name__ == "__main__":
    audio_path = "/Users/mikedaly/Desktop/Daly_Joe_Frogcast_Episode_0.m4a"
    transcription = transcribe_audio_with_timestamps(audio_path)

    output_path = "transcribed_text_with_timestamps.txt"
    with open(output_path, "w") as output_file:
        output_file.write(transcription)

    print(f"Transcription with timestamps completed. Output saved to {output_path}")
