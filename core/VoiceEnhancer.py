import noisereduce as nr
import librosa
import numpy as np
import soundfile as sf
from scipy.io import wavfile
from scipy.signal import butter, lfilter, savgol_filter, filtfilt
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize, speedup


class VoiceEnhancer:
    def __init__(self, filepath):
        self.filepath = filepath

    def reduce_noise(self):
        # Загружаем аудиофайл
        audio_data, sr = librosa.load(self.filepath, sr=None)

        # Убираем шум
        reduced_noise = nr.reduce_noise(
            y=audio_data,
            sr=sr,
            n_fft=4096 * 2,  # Количество точек для КВФТ (увеличение может улучшить качество)
            hop_length=4096,  # Шаг между сегментами (уменьшение может дать лучшее качество)
            prop_decrease=0.5,  # Уровень подавления шума (чем ближе к 1, тем меньше подавляется шум)
            time_mask_smooth_ms=256  # Сглаживание маски по времени (100 мс для плавного подавления шума)
        )

        # Сохраняем очищенную запись с помощью soundfile
        sf.write(self.filepath, reduced_noise, sr)

    def filtering(self):
        # Функция для применения высокочастотного фильтра
        def butter_highpass(cutoff, fs, order=5):
            nyq = 0.5 * fs  # Частота Найквиста
            normal_cutoff = cutoff / nyq  # Нормализуем частоту среза
            b, a = butter(order, normal_cutoff, btype='high', analog=False)
            return b, a

        # Функция для применения низкочастотного фильтра
        def butter_lowpass(cutoff, fs, order=4):
            nyq = 0.5 * fs  # Частота Найквиста
            normal_cutoff = cutoff / nyq  # Нормализуем частоту среза
            b, a = butter(order, normal_cutoff, btype='low', analog=False)
            return b, a

        # Применение высокочастотного фильтра
        def highpass_filter(data, cutoff, fs, order=5):
            b, a = butter_highpass(cutoff, fs, order=order)
            y = filtfilt(b, a, data)
            return y

        # Применение низкочастотного фильтра
        def lowpass_filter(data, cutoff, fs, order=4):
            b, a = butter_lowpass(cutoff, fs, order=order)
            y = filtfilt(b, a, data)
            return y

        # Загружаем аудиофайл
        fs, data = wavfile.read(self.filepath)

        # Применяем высокочастотный фильтр (например, срез ниже 100 Гц)
        filtered_data = highpass_filter(data, cutoff=70, fs=fs, order=3)

        # Применяем низкочастотный фильтр (например, срез выше 3000 Гц)
        filtered_data = lowpass_filter(filtered_data, cutoff=3000, fs=fs, order=2)

        # Сохраняем отфильтрованное аудио
        wavfile.write(self.filepath, fs, filtered_data.astype(data.dtype))





    def compressing(self):
        # Загружаем файл
        audio = AudioSegment.from_file(self.filepath)

        # Применяем компрессию
        compressed_audio = compress_dynamic_range(audio)

        # Сохраняем результат
        compressed_audio.export(self.filepath, format="wav")




