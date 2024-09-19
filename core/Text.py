import os
from docx import Document
import num2words
import re


class Text:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.text = self._read_text()

    def _read_text(self) -> [str]:
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"The file at {self.file_path} does not exist.")

        ext = os.path.splitext(self.file_path)[1].lower()

        if ext == '.txt':
            return [self._replace_numbers_with_words(self._read_txt())]
        elif ext == '.docx':
            return [self._replace_numbers_with_words(self._read_docx())]
        else:
            raise ValueError("Unsupported file format")

    def _read_txt(self) -> str:
        with open(self.file_path, 'r', encoding='utf-8') as file:
            input_text = file.read().encode("ascii", "ignore").decode()
            return input_text

    def _read_docx(self) -> str:
        document = Document(self.file_path)
        input_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        input_text = input_text.encode("ascii", "ignore").decode()
        return input_text

    def _replace_numbers_with_words(self, text):
        ''' Замена цифр на слова в тексте '''
        return re.sub(r"(\d+)", lambda x: num2words.num2words(int(x.group(0))), text)

    def split_into_paragraphs(self):
        ''' Разделение текста по параграфам '''
        self.text = self.text[0].split('\n')
        # Удаление пустых строк
        cleaned_list = list(filter(lambda x: x.strip(), self.text))
        self.text = cleaned_list

