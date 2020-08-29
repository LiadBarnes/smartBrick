import json
import functools
import os

#import telebot
#from telebot import *
from threading import Lock
import ast
import traceback
from telebot.apihelper import ApiException
import speech_recognition as sr

class AtmoicResource:
    __slots__ = ['mutex']
    def __init__(self):
        self.mutex = Lock()

    def wrap(func):
        @functools.wraps(func)
        def decorate(self, *args, **kwargs):
            self.mutex.acquire(1)
            res = func(self, *args, **kwargs)
            self.mutex.release()
            if res is not None: return res

        return decorate

class Myjson(AtmoicResource):
    __slots__ = ['file']
    def __init__(self, file_path):
        super().__init__()
        self.file = file_path

    @AtmoicResource.wrap
    def get(self, key = False):
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
            if not key:
                return data
            elif key in data:
                return data[key]
            return None

    @AtmoicResource.wrap
    def set(self, key, value):
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
            data[key] = value
        with open(self.file, 'w', encoding = 'utf8') as outfile:
            json.dump(data, outfile, indent=2)

def btn(text=None, callback_data=None, Home=False, Dummy=False):
    if Home:
        return btn('חזרה לתפריט הראשי', ['Menu', '0'])
    if Dummy:
        return btn(text, ['Dummy_Button'])
    if callback_data:
        callb =  "['"
        for value in callback_data:
            callb += str(value)+"','"
        callb = callb[:-3] + "']"
        return types.InlineKeyboardButton(text=text, callback_data=callb)

def simplify(call):
    try:
        return ast.literal_eval(call.data)
    except:
        return ['0', '0']

class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.commands = Myjson("res/commands.json")
        self.google_Client_id = "421190642899-qde1k8ilnefjpdt2uj170auccko6sn0f.apps.googleusercontent.com"
        self.google_client_secret = "8CQPLzlncyo7Awg8U17ePF_m"
        self.stop_sign = False

    def recognize_speech_from_mic(self):
        """Transcribe speech from recorded from `microphone`.

        Returns a dictionary with three keys:
        "success": a boolean indicating whether or not the API request was
                   successful
        "error":   `None` if no error occured, otherwise a string containing
                   an error message if the API could not be reached or
                   speech was unrecognizable
        "transcription": `None` if speech could not be transcribed,
                   otherwise a string containing the transcribed text
        """
        # check that recognizer and microphone arguments are appropriate type
        if not isinstance(self.recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(self.microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            response["transcription"] = self.recognizer.recognize_google(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"

        return response

    def exec_custom_py(self, file):
        exec(open(f'commands/{file}').read())


    def start(self):
        while not self.stop_sign:
            pharse = self.recognize_speech_from_mic()
            if pharse["transcription"]:
                print(f'You said - {pharse["transcription"]}')
                data = self.commands.get()
                if pharse["transcription"] in data.keys():
                    self.exec_custom_py(data[pharse["transcription"]])
            if not pharse["success"]:
                print('not success')

            # if there was an error, stop the game
            if pharse["error"]:
                if pharse["error"] != "Unable to recognize speech":
                    print("ERROR: {}".format(pharse["error"]))
                    return
                else:
                    print("Listening...")

    def stop(self):
        self.stop_sign = True


