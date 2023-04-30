import pyttsx3

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init('sapi5')
        self.rate = self.engine.getProperty('rate')
        self.volume = self.engine.getProperty('volume')
        self.voices = self.engine.getProperty('voices')
        print(self.rate)
        self.engine.setProperty('rate', 175)
        self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
        print(self.volume)
        print(self.voices)
        self.engine.setProperty('voice', self.voices[1].id)


    def start_text_to_speech(self,text="Hello World!"):
        for voice in self.voices:
            print(voice, voice.id)
            self.engine.setProperty('voice', voice.id)
            self.engine.say('The quick brown fox jumped over the lazy dog.')
            self.engine.runAndWait()
        self.engine.stop()
        '''self.engine.save_to_file('Hello World', 'test.mp3')
        self.engine.runAndWait()'''

if __name__ == '__main__':
    speech = TextToSpeech()
    speech.start_text_to_speech(text="Hello World!")