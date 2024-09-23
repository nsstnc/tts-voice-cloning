from TTS.api import TTS
import torch
from .Text import Text
from pydub import AudioSegment
import re
import os
import tempfile

class TextToSpeech:
    def __init__(self, speaker_path: str) -> None:
        # Определяем устройство (GPU или CPU)
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Загружаем модель
        # self.tts = TTS("tts_models/multilingual/multi-dataset/your_tts").to(device)
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        self.tts_convertion = TTS("voice_conversion_models/multilingual/vctk/freevc24").to(device)
        self.speaker_path = speaker_path

    def _split_text_by_punctuation(self, text):
        pattern = r'([.!?,"\'():;—])'
        parts = re.split(pattern, text)

        # Берем только части без знаков препинания
        result = [part.strip() for part in parts if not re.match(pattern, part)]

        # result = [''.join(pair).strip() for pair in zip(parts[0::2], parts[1::2])]
        #
        # if len(parts) % 2 != 0:
        #     result.append(parts[-1].strip())

        return result

    def synthesize_and_save(self, text: str, output_path: str, pause_duration: int = None) -> None:
        if len(text) == 0:
            print("Пустой абзац")
        else:
            if pause_duration == None:
                self.tts.tts_to_file(text=text,
                                     file_path=output_path,
                                     speaker_wav=self.speaker_path,
                                     language="en"
                                     )
                print("Синтез завершен")
            else:
                pause = AudioSegment.silent(duration=pause_duration)
                text = self._split_text_by_punctuation(text=text)

                with tempfile.TemporaryDirectory() as temp_dir:
                    print(f"Временная папка создана: {temp_dir}")
                    # записываем синтезированные куски во временную папку
                    for index, fragment in enumerate(text):
                        print(fragment)
                        if len(fragment) != 0:
                            temp_file_path = os.path.join(temp_dir, f"{index}.wav")
                            self.tts.tts_to_file(text=fragment,
                                                 file_path=temp_file_path,
                                                 speaker_wav=self.speaker_path,
                                                 language="en"
                                                 )

                    files = sorted(os.listdir(temp_dir), key=lambda x: int(x.split('.')[0]))

                    output_audio = AudioSegment.from_wav(os.path.join(temp_dir, files[0]))
                    # проходимся по синтезированным кускам и соединяем их с паузами
                    for file in files[1:]:
                        file_path = os.path.join(temp_dir, file)
                        audio = AudioSegment.from_wav(file_path)
                        output_audio += pause + audio

                    output_audio.export(output_path, format="wav")

    def voice_conversion(self, output_path: str) -> None:
        # Загрузка исходного аудиофайла
        audio = AudioSegment.from_wav(output_path)

        # Длительность одного фрагмента в миллисекундах (60 секунд)
        chunk_length_ms = 30 * 1000
        chunks = []
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Временная папка создана: {temp_dir}")
            # Разделение файла на фрагменты по 60 секунд
            for i in range(0, len(audio), chunk_length_ms):
                chunk = audio[i:i + chunk_length_ms]
                chunk_file = os.path.join(temp_dir, f"chunk_{i // chunk_length_ms}.wav")
                chunk.export(chunk_file, format="wav")  # Сохранение фрагмента

                # Обработка фрагмента
                processed_chunk_file = self.process_chunk(chunk_file)
                processed_chunk = AudioSegment.from_wav(processed_chunk_file)

                # Добавление обработанного фрагмента в список
                chunks.append(processed_chunk)


        # Объединение всех обработанных фрагментов
        final_audio = AudioSegment.empty()
        for chunk in chunks:
            final_audio += chunk

        # Сохранение объединенного аудиофайла
        file_path = output_path[:-4] + "_conversion.wav"
        final_audio.export(file_path, format="wav")
        print(f"Файл успешно сохранён в {file_path}")

    def process_chunk(self, chunk_file):
        # Функция для обработки каждого фрагмента с использованием voice_conversion_to_file
        processed_chunk_file = chunk_file[:-4] + "_processed.wav"
        self.tts_convertion.voice_conversion_to_file(
            source_wav=chunk_file,
            target_wav=self.speaker_path,
            file_path=processed_chunk_file
        )
        return processed_chunk_file

