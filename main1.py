import requests
import pyttsx3
import pyaudio
import json
import os
import webbrowser
from vosk import Model, KaldiRecognizer

class Speech:
    def __init__(self):
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 170)

    def say(self, text):
        print(f"Assistant: {text}")
        self.tts.say(text)
        self.tts.runAndWait()

class Recognizer:
    def __init__(self):
        if not os.path.exists("model_en"):
            raise FileNotFoundError("English model 'model_en' not found.")
        model = Model("model_en")
        self.rec = KaldiRecognizer(model, 16000)
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paInt16,
                                   channels=1,
                                   rate=16000,
                                   input=True,
                                   frames_per_buffer=8000)
        self.stream.start_stream()

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                text = result.get("text", "")
                if text:
                    return text

class DictionaryAssistant:
    def __init__(self):
        self.speech = Speech()
        self.recognizer = Recognizer()
        self.word_data = None
        self.word = ""

    def find_word(self, word):
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            res = requests.get(url)
            res.raise_for_status()
            self.word_data = res.json()[0]
            self.word = word
            self.speech.say(f"{word} loaded successfully.")
        except Exception:
            self.speech.say(f"Could not find definition for {word}.")

    def meaning(self):
        if self.word_data:
            try:
                meaning = self.word_data['meanings'][0]['definitions'][0]['definition']
                self.speech.say(f"The meaning of {self.word} is: {meaning}")
            except:
                self.speech.say("No meaning found.")
        else:
            self.speech.say("No word loaded. Say: find and the word.")

    def example(self):
        if self.word_data:
            try:
                example = self.word_data['meanings'][0]['definitions'][0]['example']
                self.speech.say(f"Example: {example}")
            except:
                self.speech.say("No example found.")
        else:
            self.speech.say("No word loaded.")

    def open_link(self):
        if self.word:
            webbrowser.open(f"https://www.dictionary.com/browse/{self.word}")
            self.speech.say("Opened link in browser.")
        else:
            self.speech.say("No word loaded.")

    def save_to_file(self):
        if self.word_data:
            try:
                with open("dictionary_saved.txt", "a", encoding="utf-8") as f:
                    definition = self.word_data['meanings'][0]['definitions'][0]['definition']
                    f.write(f"{self.word}:\nDefinition: {definition}\n\n")
                self.speech.say("Saved to file.")
            except:
                self.speech.say("Error saving to file.")
        else:
            self.speech.say("No word loaded.")

    def run(self):
        self.speech.say("Dictionary assistant started. Say a command.")
        while True:
            command = self.recognizer.listen()
            print(f"You said: {command}")

            if command.startswith("find "):
                word = command.replace("find ", "").strip()
                self.find_word(word)
            elif command == "meaning":
                self.meaning()
            elif command == "example":
                self.example()
            elif command == "link":
                self.open_link()
            elif command == "save":
                self.save_to_file()
            elif command in ["exit", "stop"]:
                self.speech.say("Goodbye!")
                break
            else:
                self.speech.say("Command not recognized.")

if __name__ == "__main__":
    assistant = DictionaryAssistant()
    assistant.run()
