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
        self.tts = TTS("tts_models/multilingual/multi-dataset/your_tts").to(device)
        self.speaker_path = speaker_path

    def _split_text_by_punctuation(self, text):
        pattern = r'([.!?,"\'():;—])'
        parts = re.split(pattern, text)

        result = [''.join(pair).strip() for pair in zip(parts[0::2], parts[1::2])]

        if len(parts) % 2 != 0:
            result.append(parts[-1].strip())

        return result

    def synthesize_and_save(self, text: str, output_path: str, pause_duration: int) -> None:
        if len(text) == 0:
            print("Пустой абзац")
        else:
            if pause_duration == 0:
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