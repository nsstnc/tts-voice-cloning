import sys
from cx_Freeze import setup, Executable
import os

# Определяем дополнительные зависимости

# Для использования иконки на Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

options = {
    'build_exe': {
        'include_msvcr': True,
        "packages": ["inspect", "collections", "pygame", "noisereduce", "soundfile", "scipy", "docx", "num2words", "inflect",
                     "pydub"],
        "include_files": [
            ("icon/icon.ico", "icon.ico"),
            "voices/",
        ],

    }
}

setup(
    name="Text to speech",
    version="1.0",
    description="Text to speech application with voice cloning",
    options=options,

    executables=[Executable("main.py", base=base, icon="icon/icon.ico", target_name="Text To Speech")]
)
