import os
import time  # Для измерения времени выполнения
from core.Text import Text
from core.TextToSpeech import TextToSpeech
from core.VoiceEnhancer import VoiceEnhancer
import traceback
import tkinter as tk
import threading  # Для выполнения скрипта в отдельном потоке
from tkinter import filedialog, messagebox, Checkbutton, BooleanVar, Radiobutton
import pygame

# Инициализация pygame для работы с аудио
pygame.mixer.init()

# Пути к сэмплам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Путь к директории, где находится main.py
SAMPLES_DIR = os.path.join(BASE_DIR, "voices")  # Путь к папке voices
MODELS_DIR = os.path.join(BASE_DIR, "models")
sample_files = {f: os.path.join(MODELS_DIR, f.split('.')[0]) for f in os.listdir(SAMPLES_DIR) if f.endswith('.wav') or f.endswith('.mp3')}

def play_sample(sample_path):
    try:
        pygame.mixer.music.load(os.path.join(SAMPLES_DIR, sample_path))
        pygame.mixer.music.play()
    except Exception as e:
        messagebox.showerror("Ошибка воспроизведения", f"Не удалось воспроизвести файл: {str(e)}")


def stop_playing():
    pygame.mixer.music.stop()


def select_file():
    filetypes = [("Text and Word files", "*.txt;*.docx")]
    filepath = filedialog.askopenfilename(title="Выберите файл", filetypes=filetypes)
    if filepath:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filepath)


def select_save_location():
    folder = filedialog.askdirectory(title="Выберите папку для сохранения")
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)


def run_script():
    # Делаем кнопку неактивной
    run_button.config(state="disabled")

    global stop_execution
    stop_execution = False

    selected_file = file_entry.get()
    selected_folder = folder_entry.get()
    split_by_paragraphs = split_var.get()
    need_compression = compression_var.get()
    selected_sample = selected_sample_var.get()
    pause_duration = pause_var.get()
    need_pause = need_pause_var.get()

    if len(selected_file) == 0 or "Файл: " in selected_file:
        messagebox.showerror("Ошибка", "Выберите файл для обработки.")
        return
    if len(selected_folder) == 0 or "Сохранить в: " in selected_folder:
        messagebox.showerror("Ошибка", "Выберите папку для сохранения.")
        return
    if not selected_sample:
        messagebox.showerror("Ошибка", "Выберите сэмпл для озвучки.")
        return

    # Обновление статуса
    status_var.set("Выполняется...")
    start_time = time.time()
    update_time_display(start_time)
    root.update_idletasks()

    try:
        text = Text(selected_file)
        tts = TextToSpeech(os.path.join(SAMPLES_DIR, selected_sample), sample_files[selected_sample])
        name = selected_file.split('/')[-1].split('.')[0]

        if split_by_paragraphs:
            text.split_into_paragraphs()

        total_paragraphs = len(text.text)
        remaining_paragraphs_var.set(f"Осталось абзацев: {total_paragraphs}")

        for index, paragraph in enumerate(text.text):
            output_filepath = selected_folder + f"/{name}{index + 1}.wav"
            if not stop_execution:
                # синтез голоса
                tts.synthesize_and_save(paragraph, output_filepath, pause_duration if need_pause else None)

                # конверсия голоса
                # status_var.set("Конверсия...")
                # tts.voice_conversion(output_filepath)

                voice = VoiceEnhancer(output_filepath)



                # status_var.set("Фильтрация частот...")
                # # фильтрация частот
                # voice.filtering()

                # обработка голоса
                status_var.set("Удаление шумов...")
                # удаление шумов
                voice.reduce_noise()

                if need_compression:
                    status_var.set("Компрессия динамического\n диапазона...")
                    # компрессия динамического диапазона
                    voice.compressing()



                # Обновление оставшихся параграфов
                remaining_paragraphs_var.set(f"Осталось абзацев: {total_paragraphs - (index + 1)}")
                root.update_idletasks()

    except Exception as e:
        status_var.set("Ошибка!")
        messagebox.showerror("Ошибка", f"Произошла ошибка при выполнении скрипта: {str(e)}")
        print(traceback.format_exc())
    finally:
        elapsed_time = time.time() - start_time
        status_var.set("Завершено!")
        elapsed_time_var.set(f"Время выполнения: {elapsed_time:.2f} сек")
        # Запросить переход в папку сохранения
        if messagebox.askyesno("Готово", f"Файлы сохранены в: {selected_folder}. Перейти в папку?"):
            os.startfile(selected_folder)
        # Делаем кнопку снова активной
        run_button.config(state="normal")


def format_time(seconds):
    """Форматирование времени в часы, минуты и секунды."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours} ч {minutes} мин {secs} сек"
    elif minutes > 0:
        return f"{minutes} мин {secs} сек"
    else:
        return f"{secs} сек"


def update_time_display(start_time):
    current_time = time.time()
    elapsed_time = current_time - start_time
    elapsed_time_var.set(f"Время выполнения: {format_time(elapsed_time)}")
    if (status_var.get() == "Выполняется..." or
            status_var.get() == "Удаление шумов..." or
            status_var.get() == "Фильтрация частот..." or
            status_var.get() == "Компрессия динамического\n диапазона..." or
            status_var.get() == "Конверсия..."
            ):
        root.after(1000, update_time_display, start_time)


def on_closing():
    global stop_execution
    stop_execution = True  # Остановка выполнения скрипта
    pygame.mixer.music.stop()  # Остановка воспроизведения аудио
    root.destroy()  # Закрытие окна


def show_info():
    messagebox.showinfo("Информация",
                        "Компрессия динамического диапазона - это сглаживание перепадов громкости отдельных звуков\n"
                        "(увеличит время обработки до +50%)")


def on_checkbox_toggle():
    if compression_var.get():  # Если чекбокс установлен
        show_info()

def on_pause_checkbox_toggle():
    if need_pause_var.get():
        pause_label.grid()  # Восстанавливаем элемент
        pause_scale.grid()  # Восстанавливаем ползунок
    else:
        pause_label.grid_remove()  # Убираем элемент
        pause_scale.grid_remove()  # Убираем ползунок

def show_value(value):
    pause_label.config(text=f"Паузы: {value} мс")
    pause_var.set(value)  # Обновление переменной со значением ползунка




# Создание основного окна
root = tk.Tk()

root.title("Text To Speech")
# Установка иконки
root.iconphoto(True, tk.PhotoImage(file="./icon/icon.png"))
root.geometry("600x400")
root.minsize(600, 400)
root.maxsize(600, 400)
# Привязка обработчика события закрытия окна
root.protocol("WM_DELETE_WINDOW", on_closing)

head_frame = tk.Frame(root, borderwidth=2, relief="sunken")
head_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

down_frame = tk.Frame(root)
down_frame.grid(row=1, column=0, padx=5, sticky="nsew")

left_down_frame = tk.Frame(down_frame)
left_down_frame.grid(row=0, column=0, sticky="nsew")

right_down_frame = tk.Frame(down_frame)
right_down_frame.grid(row=0, column=1, sticky="nsew")

left_down_header = tk.Frame(left_down_frame, borderwidth=2, relief="sunken")
left_down_header.grid(row=0, column=0, sticky="nsew")

right_down_header = tk.Frame(right_down_frame, borderwidth=2, relief="sunken")
right_down_header.grid(row=0, column=0, sticky="nsew")

left_down_footer = tk.Frame(left_down_frame, borderwidth=2, relief="sunken")
left_down_footer.grid(row=1, column=0, sticky="nsew")

right_down_footer = tk.Frame(right_down_frame, borderwidth=2, relief="sunken")
right_down_footer.grid(row=1, column=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
head_frame.columnconfigure(1, weight=1)
down_frame.columnconfigure(1, weight=1)
down_frame.rowconfigure(0, weight=1)
down_frame.rowconfigure(0, weight=1)
right_down_frame.columnconfigure(0, weight=1)
right_down_frame.rowconfigure(0, weight=1)
left_down_frame.rowconfigure(0, weight=2)
left_down_frame.rowconfigure(1, weight=1)

right_down_header.rowconfigure(0, weight=1)
right_down_header.columnconfigure(0, weight=1)

right_down_footer.columnconfigure(0, weight=1)
right_down_footer.rowconfigure(0, weight=1)

left_down_footer.columnconfigure(0, weight=1)
left_down_footer.columnconfigure(1, weight=1)
left_down_footer.rowconfigure(0, weight=1)

# Поле для выбора файла
file_label = tk.Label(head_frame, text="Файл:")
file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
file_entry = tk.Entry(head_frame)
file_entry.insert(0, "")
file_entry.grid(row=0, column=1, padx=10, sticky='ew')
file_button = tk.Button(head_frame, text="Выбрать файл", command=select_file)
file_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

# Поле для выбора папки для сохранения
folder_label = tk.Label(head_frame, text="Сохранить в:")
folder_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
folder_entry = tk.Entry(head_frame)
folder_entry.grid(row=2, column=1, padx=10, sticky='ew')
folder_entry.insert(0, "")
folder_button = tk.Button(head_frame, text="Выбрать папку", command=select_save_location)
folder_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

# Чекбокс для параметра "Разделить по абзацам"
split_label = tk.Label(left_down_header, text="Разделить по абзацам:")
split_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
split_var = BooleanVar()
split_checkbox = tk.Checkbutton(left_down_header, variable=split_var)
split_checkbox.grid(row=0, column=1, padx=10, pady=5, sticky="w")

# Чекбокс для параметра "Добавить компрессию динамического диапазона"
compression_label = tk.Label(left_down_header, text="Компрессия\n динамического диапазона:")
compression_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
compression_var = BooleanVar(value=True)
compression_checkbox = tk.Checkbutton(left_down_header, variable=compression_var, command=on_checkbox_toggle)
compression_checkbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Выбор сэмпла для озвучки
sample_label = tk.Label(left_down_header, text="Сэмплы для озвучки:")
sample_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
selected_sample_var = tk.StringVar(value=list(sample_files.keys())[0])

sample_menu = tk.OptionMenu(left_down_header, selected_sample_var, *[f for f in sample_files.keys()])
sample_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Чекбокс для параметра "Изменить стандартный темп"
need_pause_label = tk.Label(left_down_header, text="Изменить стандартный темп:")
need_pause_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
need_pause_var = BooleanVar(value=False)
need_pause_checkbox = tk.Checkbutton(left_down_header, variable=need_pause_var, command=on_pause_checkbox_toggle)
need_pause_checkbox.grid(row=3, column=1, padx=10, pady=5, sticky="w")

# параметр для выбора задержки
pause_var = tk.IntVar(value=200)
pause_label = tk.Label(left_down_header, text="Паузы: 200 мс")
pause_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
pause_label.grid_remove()  # Убираем элемент
pause_scale = tk.Scale(left_down_header, from_=0, to=500, orient='horizontal', resolution=50, showvalue=False, command=show_value, variable=pause_var)
pause_scale.grid(row=4, column=1, padx=10, pady=5, sticky="w")
pause_scale.grid_remove()  # Убираем ползунок

# кнопка воспроизведения сэмпла
play_button = tk.Button(left_down_footer, text=f"Прослушать", command=lambda: play_sample(selected_sample_var.get()))
# play_button.grid(row=0, column=0, padx=5, pady=5, sticky="we")
# растянуть по высоте
play_button.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
# Кнопка остановки воспроизведения
stop_button = tk.Button(left_down_footer, text="Остановить", command=stop_playing)
# stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="we")
# растянуть по высоте
stop_button.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

# Индикатор загрузки и время выполнения
status_var = tk.StringVar(value="Ожидание")
status_label = tk.Label(right_down_header, textvariable=status_var, font=("Helvetica", 12))
status_label.grid(row=0, column=0, pady=5, sticky="nsew")

remaining_paragraphs_var = tk.StringVar(value="Осталось абзацев: 0")
remaining_paragraphs_label = tk.Label(right_down_header, textvariable=remaining_paragraphs_var)
remaining_paragraphs_label.grid(row=1, column=0, pady=5, sticky="nsew")

elapsed_time_var = tk.StringVar(value="Время выполнения: 0 сек")
elapsed_time_label = tk.Label(right_down_header, textvariable=elapsed_time_var)
elapsed_time_label.grid(row=2, column=0, pady=5, sticky="nsew")

# Кнопка запуска
run_button = tk.Button(right_down_footer, text="Запустить", command=lambda: threading.Thread(target=run_script).start())
# run_button.grid(row=0, column=10, pady=5, sticky="e")
run_button.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    # Запуск интерфейса
    root.mainloop()
