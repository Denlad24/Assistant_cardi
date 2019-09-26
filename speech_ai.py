# Библиотеки распознавания и синтеза речи
import speech_recognition as sr
from gtts import gTTS
import numpy as np
import pyaudio
import win32com.client as wincl
# Воспроизведение речи
import os
import sys
import wmi
from win32com.client import GetObject
import time
import datetime
import logging
import webbrowser
import subprocess
from winreg import *
import win32file
import win32con
import ctypes
import wave
from array import array

# Import the SendInput object
SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBoardInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]


class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort)
    ]


class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]


class Input_I(ctypes.Union):
    _fields_ = [
        ("ki", KeyBoardInput),
        ("mi", MouseInput),
        ("hi", HardwareInput)
    ]


class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", Input_I)
    ]


VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF


def key_down(keyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBoardInput(keyCode, 0x48, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def key_up(keyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBoardInput(keyCode, 0x48, 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def key(key_code, length=0):
    key_down(key_code)
    time.sleep(length)
    key_up(key_code)


def mute():
    key(VK_VOLUME_MUTE)


def volume_up():
    key(VK_VOLUME_UP)


def volume_down():
    key(VK_VOLUME_DOWN)


def set_volume(vol):
    vol1 = int(vol / 2)
    for _ in range(0, 50):
        volume_down()
    for _ in range(vol1):
        volume_up()


class Speech_AI:

    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()

        now_time = datetime.datetime.now()
        self._mp3_name = now_time.strftime("%d%m%Y%I%M%S") + ".mp3"
        self._mp3_nameold = '111'

    def work(self):
        print("Минутку тишины, пожалуйста...")
        speak = wincl.Dispatch("SAPI.SpVoice")

        # subprocess.Popen('C:/Users/Denis/Documents/ден питон(ассистент)/find file/live_change.exe')

        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source)

        # i = 0
        # my_file = open('test.txt', 'w', encoding='utf-8')
        # for root, dirs, files in os.walk("C:/"):
        #     for file in files:
        #         j = os.path.join(root, file)
        #         my_file.write(j + '|' + file + '\n')
        #         i = i + 1
        # my_file.close()

        try:
            while True:
                print("Скажи что - нибудь!")

                maxvalue = 2 ** 16
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100,
                                input=True, frames_per_buffer=1024)
                data = np.fromstring(stream.read(1024), dtype=np.int16)
                dataL = data[0::2]
                dataR = data[1::2]
                peakL = np.abs(np.max(dataL) - np.min(dataL)) / maxvalue
                peakR = np.abs(np.max(dataR) - np.min(dataR)) / maxvalue
                if peakL > 0.3:
                    with self._microphone as source:
                        audio = self._recognizer.listen(source)
                    print("Понял, идет распознавание...")
                    try:
                        # statement = self._recognizer.recognize_google(audio, language="ru_RU")
                        statement = self._recognizer.recognize_google(audio, language="ru_RU")
                        statement = statement.lower()
                        # Команды для открытия различных внешних приложений
                        s = str(statement)
                        aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
                        aKey = OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
                        for i in range(1024):
                            try:
                                asubkey_name = EnumKey(aKey, i)
                                asubkey = OpenKey(aKey, asubkey_name)
                                val = str(QueryValueEx(asubkey, "DisplayName"))
                                b = "!@#$,01'"
                                for char in b:
                                    val = val.replace(char, "")
                                r = len(val)
                                val = str(val[1:r - 2])
                                val2 = str(QueryValueEx(asubkey, "DisplayIcon"))
                                if s.lower() in val.lower():
                                    r = len(val2)
                                    val2 = str(val2[2:r - 5])
                                    # print(val2)
                                    subprocess.Popen(val2)
                                    break
                                # print(val, val2)
                            except EnvironmentError:
                                continue
                        aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
                        aKey = OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
                        for i in range(1024):
                            try:
                                asubkey_name = EnumKey(aKey, i)
                                asubkey = OpenKey(aKey, asubkey_name)
                                val = str(QueryValueEx(asubkey, "DisplayName"))
                                b = "!@#$,01'"
                                for char in b:
                                    val = val.replace(char, "")
                                r = len(val)
                                val = str(val[1:r - 2])
                                val2 = str(QueryValueEx(asubkey, "DisplayIcon"))
                                if s.lower() in val.lower():
                                    r = len(val2)
                                    val2 = str(val2[2:r - 7])
                                    subprocess.Popen(val2)
                                    break
                                # print(val, val2)
                            except EnvironmentError:
                                continue
                        print("next iteration")
                        aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
                        aKey = OpenKey(aReg, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
                        for i in range(1024):
                            try:
                                asubkey_name = EnumKey(aKey, i)
                                asubkey = OpenKey(aKey, asubkey_name)
                                val = str(QueryValueEx(asubkey, "DisplayName"))
                                b = "!@#$,01'"
                                for char in b:
                                    val = val.replace(char, "")
                                r = len(val)
                                val = str(val[1:r - 2])
                                val2 = str(QueryValueEx(asubkey, "DisplayIcon"))
                                if s.lower() in val.lower():
                                    r = len(val2)
                                    val2 = str(val2[2:r - 5])
                                    # print(val2)
                                    subprocess.Popen(val2)
                                    break
                                # print(val, val2)
                            except EnvironmentError:
                                continue
                        for i in range(1024):
                            try:
                                asubkey_name = EnumKey(aKey, i)
                                asubkey = OpenKey(aKey, asubkey_name)
                                val = str(QueryValueEx(asubkey, "DisplayName"))
                                b = "!@#$,01'"
                                for char in b:
                                    val = val.replace(char, "")
                                r = len(val)
                                val = str(val[1:r - 2])
                                val2 = str(QueryValueEx(asubkey, "DisplayIcon"))
                                if s.lower() in val.lower():
                                    r = len(val2)
                                    val2 = str(val2[2:r - 7])
                                    # print(val2)
                                    subprocess.Popen(val2)
                                    break
                                # print(val, val2)
                            except EnvironmentError:
                                continue

                        if (((statement.find("калькулятор") != -1) or (statement.find("calculator") != -1)) and (
                                statement.find("открой") != -1)):
                            self.osrun('calc')

                        if ((statement.find("блокнот") != -1) or (statement.find("notepad") != -1)):
                            self.osrun('notepad')

                        if ((statement.find("paint") != -1) or (statement.find("паинт") != -1)):
                            self.osrun('mspaint')

                        if ((statement.find("browser") != -1) or (statement.find("браузер") != -1)):
                            self.openurl('http://google.ru', 'Открываю браузер')

                        # Команды для открытия URL в браузере

                        if (((statement.find("youtube") != -1) or (statement.find("youtub") != -1) or (
                                statement.find("ютуб") != -1) or (statement.find("you tube") != -1)) and (
                                statement.find("смотреть") == -1)):
                            self.openurl('http://youtube.com', 'Открываю ютуб')

                        if (((statement.find("новости") != -1) or (statement.find("новость") != -1) or (
                                statement.find("на усть") != -1)) and (
                                (statement.find("youtube") == -1) and (statement.find("youtub") != -1) and (
                                statement.find("ютуб") == -1) and (statement.find("you tube") == -1))):
                            self.openurl('https://www.youtube.com/user/rtrussian/videos', 'Открываю новости')

                        if ((statement.find("mail") != -1) or (statement.find("почту") != -1)):
                            self.openurl('https://e.mail.ru/messages/inbox/', 'Открываю почту')

                        if ((statement.find("вконтакте") != -1) or (statement.find("в контакте") != -1)):
                            self.openurl('http://vk.com', 'Открываю Вконтакте')

                        # Команды для поиска в сети интернет

                        if ((statement.find("найти") != -1) or (statement.find("поиск") != -1) or (
                                statement.find("найди") != -1) or (statement.find("дайте") != -1) or (
                                statement.find("mighty") != -1)):
                            statement = statement.replace('найди', '')
                            statement = statement.replace('найти', '')
                            statement = statement.strip()
                            self.openurl('https://www.google.ru/search?q=' + statement, "Я нашла следующие результаты")

                        if ((statement.find("смотреть") != -1) and (
                                (statement.find("фильм") != -1) or (statement.find("film") != -1))):
                            statement = statement.replace('посмотреть', '')
                            statement = statement.replace('смотреть', '')
                            statement = statement.replace('хочу', '')
                            statement = statement.replace('фильм', '')
                            statement = statement.replace('film', '')
                            statement = statement.strip()
                            self.openurl('https://yandex.ru/yandsearch?text=Смотреть+онлайн+фильм+' + statement,
                                         "Выберите сайт где смотреть фильм")

                        if (((statement.find("youtube") != -1) or (statement.find("ютуб") != -1) or (
                                statement.find("you tube") != -1)) and (statement.find("смотреть") != -1)):
                            statement = statement.replace('хочу', '')
                            statement = statement.replace('на ютубе', '')
                            statement = statement.replace('на ютуб', '')
                            statement = statement.replace('на youtube', '')
                            statement = statement.replace('на you tube', '')
                            statement = statement.replace('на youtub', '')
                            statement = statement.replace('youtube', '')
                            statement = statement.replace('ютуб', '')
                            statement = statement.replace('ютубе', '')
                            statement = statement.replace('посмотреть', '')
                            statement = statement.replace('смотреть', '')
                            statement = statement.strip()
                            self.openurl('http://www.youtube.com/results?search_query=' + statement, 'Ищу в ютуб')

                        if ((statement.find("слушать") != -1) and (statement.find("песн") != -1)):
                            statement = statement.replace('песню', '')
                            statement = statement.replace('песни', '')
                            statement = statement.replace('песня', '')
                            statement = statement.replace('песней', '')
                            statement = statement.replace('послушать', '')
                            statement = statement.replace('слушать', '')
                            statement = statement.replace('хочу', '')
                            statement = statement.strip()
                            self.openurl('https://my.mail.ru/music/search/' + statement, "Нажмите плэй")

                        if ((statement.find("открой") != -1) and (statement.find("документ") != -1)):
                            speak.Speak("Назовите файл")
                            print("Назовите файл")
                            r = sr.Recognizer()
                            with sr.Microphone() as source:  # use the default microphone as the audio source
                                audio = r.listen(source)
                            statement2 = r.recognize_google(audio, language="ru_RU")
                            filenames = str(statement2.lower())
                            print('название файла', filenames)
                            a = []
                            i = 0
                            d3 = {}
                            with open('test5.txt', encoding='utf-8') as inp:
                                for b in inp.readlines():
                                    key, val = b.strip().split('|')
                                    d3[key] = val
                                    if (filenames.lower() == val[0:val.rfind('.')].lower()):
                                        i = i + 1
                                        print(i, ")", key)
                                        a.append([key])
                            speak.Speak("Какой файл вы хотите открыть?")
                            print("Какой файл вы хотите открыть?")
                            with sr.Microphone() as source:  # use the default microphone as the audio source
                                audio = r.listen(source)
                            statement3 = r.recognize_google(audio, language="ru_RU")
                            if str(statement3).isdigit():
                                speak.Speak("Открываю")
                                q = int(statement3)
                                st = str(a[q - 1])
                                l = len(st)
                                subprocess.Popen([st[2:l - 2]], shell=True)
                            else:
                                speak.Speak("Вы сказали что-то не то")

                        if (statement.find("яркость") != -1):
                            objWMI = GetObject('winmgmts:\\\\.\\root\\WMI').InstancesOf('WmiMonitorBrightness')

                            q = 0
                            for obj in objWMI:
                                if obj.CurrentBrightness != None:
                                    q = int(obj.CurrentBrightness)
                            s = str(statement)
                            if "больше" in s:
                                print("super")
                                d = q + 10
                                wmi.WMI(namespace="wmi").WmiMonitorBrightnessMethods()[0].WmiSetBrightness(d, 0)
                            if "меньше" in s:
                                d = q - 10
                                wmi.WMI(namespace="wmi").WmiMonitorBrightnessMethods()[0].WmiSetBrightness(d, 0)

                        if (statement.find("сделай яркость") != -1):
                            objWMI = GetObject('winmgmts:\\\\.\\root\\WMI').InstancesOf('WmiMonitorBrightness')

                            q = 0
                            d = 0
                            for obj in objWMI:
                                if obj.CurrentBrightness != None:
                                    q = int(obj.CurrentBrightness)
                            s = str(statement)
                            s = s.split()
                            for i in range(len(s)):
                                if s[i].isdigit():
                                    d = s[i]
                            wmi.WMI(namespace="wmi").WmiMonitorBrightnessMethods()[0].WmiSetBrightness(int(d), 0)

                        if (statement.find("выключи звук") != -1 or statement.find("включи звук") != -1):
                            mute()

                            if 'меньше' in statement:
                                volume_down()

                        if ((statement.find('сделай громче') != -1) or (statement.find('громкость больше') != -1) or (
                                statement.find('сделай погромче') != -1)):
                            volume_up()

                        if ((statement.find('сделай тише') != -1) or (statement.find('громкость меньше') != -1) or (
                                statement.find('сделай потише') != -1)):
                            volume_down()

                        if ((statement.find('сделай громкость') != -1) or (statement.find('сделай звук') != -1)):
                            s = str(statement)
                            s = s.split()
                            q = int(0)
                            for i in range(len(s)):
                                if s[i].isdigit():
                                    q = s[i]
                            print(q)
                            a = int(q)
                            set_volume(a)

                        # Поддержание диалога

                        if (statement.find("создать заметку") != -1):
                            dir_path = os.getcwd()
                            print(dir_path)
                            os.makedirs(str(dir_path) + "/zamet/tekst/")
                            os.makedirs(str(dir_path) + "/zamet/voice/")
                            speak.Speak("Какую заметку вы хотите создать? Текстовую или голосовую")
                            r = sr.Recognizer()
                            with sr.Microphone() as source:  # use the default microphone as the audio source
                                audio = r.listen(source)
                            statement2 = r.recognize_google(audio, language="ru_RU")
                            print(statement2)
                            if statement2.find("голосовую") != -1:
                                """PyAudio example: Record a few seconds of audio and save to a WAVE file."""

                                CHUNK = 1024
                                FORMAT = pyaudio.paInt16
                                CHANNELS = 2
                                RATE = 44100
                                RECORD_SECONDS = 500000

                                p = pyaudio.PyAudio()

                                stream = p.open(format=FORMAT,
                                                channels=CHANNELS,
                                                rate=RATE,
                                                input=True,
                                                frames_per_buffer=CHUNK)

                                speak.Speak("Начинается запись")

                                frames = []
                                start_time = time.time()
                                timer = 0

                                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                                    data = stream.read(CHUNK)
                                    data_chunk = array('h', data)
                                    vol = max(data_chunk)
                                    print(vol)
                                    if (vol >= 1500):
                                        print("something said")
                                        timer = 0
                                        print(timer)
                                        frames.append(data)
                                    else:
                                        timer = timer + time.time() - start_time
                                        print(timer)
                                        print("nothing")
                                    print("\n")
                                    if timer > 500:
                                        print("stop")
                                        break

                                speak.Speak("Запись закончена")

                                stream.stop_stream()
                                stream.close()
                                p.terminate()
                                speak.Speak("Как вы хотите назвать файл?")
                                with sr.Microphone() as source:  # use the default microphone as the audio source
                                    audio = r.listen(source)
                                WAVE_OUTPUT_FILENAME = r.recognize_google(audio, language="ru_RU")
                                completeName = os.path.join(dir_path + "/zamet/voice/", WAVE_OUTPUT_FILENAME + ".wav")
                                wf = wave.open(completeName, 'wb')
                                wf.setnchannels(CHANNELS)
                                wf.setsampwidth(p.get_sample_size(FORMAT))
                                wf.setframerate(RATE)
                                wf.writeframes(b''.join(frames))
                                wf.close()
                            if (statement2.find("текст") != -1):
                                speak.Speak("Скажите, что вы хотите записать")
                                with sr.Microphone() as source:  # use the default microphone as the audio source
                                    audio = r.listen(source)
                                statement3 = r.recognize_google(audio, language="ru_RU")
                                a = str(statement3)
                                speak.Speak("Как вы хотите назвать файл?")
                                with sr.Microphone() as source:  # use the default microphone as the audio source
                                    audio = r.listen(source)
                                WAVE_OUTPUT_FILENAME = r.recognize_google(audio, language="ru_RU")

                                completeName = os.path.join(dir_path + "/zamet/tekst/", WAVE_OUTPUT_FILENAME + ".txt")
                                f = open(completeName, 'w')
                                f.write(a)
                                f.close()

                        if(statement.find("сохранить") != -1 and statement.find("пароль") != -1):
                            speak.Speak("В каком виде вы хотите сохранить пароль?")
                            r = sr.Recognizer()
                            with sr.Microphone() as source:  # use the default microphone as the audio source
                                audio = r.listen(source)
                            statement2 = r.recognize_google(audio, language="ru_RU")
                            if statement2.find("") == "шифрованный":
                                speak.Speak("Назовите для чего будет пароль")
                                with sr.Microphone() as source:  # use the default microphone as the audio source
                                    audio = r.listen(source)
                                statement3 = r.recognize_google(audio, language="ru_RU")
                                speak.Speak("Назовите сам пароль")
                                with sr.Microphone() as source:  # use the default microphone as the audio source
                                    audio = r.listen(source)
                                statement4 = r.recognize_google(audio, language="ru_RU")

                            if statement2.find() == "в обычном":
                                speak.Speak("Назовите для чего будет пароль")
                                with sr.Microphone() as source:  # use the default microphone as the audio source
                                    audio = r.listen(source)
                                statement3 = r.recognize_google(audio, language="ru_RU")
                                speak.Speak("Назовите сам пароль")
                                with sr.Microphone() as source:  # use the default microphone as the audio source
                                    audio = r.listen(source)
                                statement4 = r.recognize_google(audio, language="ru_RU")
                                f = open(statement3 + ".txt", 'w')
                                f.write(statement4)
                                f.close()

                        if (((statement.find("до свидания") != -1) or (statement.find("досвидания") != -1) or (
                                statement.find("спи") != -1)) and (statement.find("система") != -1)):
                            sys.exit()

                        print("Вы сказали: {}".format(statement))

                    except sr.UnknownValueError:
                        print("Упс! Кажется, я тебя не поняла, повтори еще раз")
                    except sr.RequestError as e:
                        print("Не могу получить данные от сервиса Google Speech Recognition; {0}".format(e))
            #
            #     ACTIONS = {
            #         1: "Создан",
            #         2: "Удален",
            #         3: "Обновлен",
            #         4: "Переименован из чего-то",
            #         5: "Переименован во что-то"
            #     }
            #     # Thanks to Claudio Grondi for the correct set of numbers
            #     FILE_LIST_DIRECTORY = 0x0001
            #
            #     path_to_watch = "C:/"
            #     hDir = win32file.CreateFile(
            #         path_to_watch,
            #         FILE_LIST_DIRECTORY,
            #         win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            #         None,
            #         win32con.OPEN_EXISTING,
            #         win32con.FILE_FLAG_BACKUP_SEMANTICS,
            #         None
            #     )
            # #
            # # ReadDirectoryChangesW takes a previously-created
            # # handle to a directory, a buffer size for results,
            #     # a flag to indicate whether to watch subtrees and
            #     # a filter of what changes to notify.
            #     #
            #     # NB Tim Juchcinski reports that he needed to up
            #     # the buffer size to be sure of picking up all
            #     # events when a large number of files were
            #     # deleted at once.
            #     #
            #     results = win32file.ReadDirectoryChangesW(
            #         hDir,
            #         1024,
            #         True,
            #         win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            #         win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            #         win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            #         win32con.FILE_NOTIFY_CHANGE_SIZE |
            #         win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            #         win32con.FILE_NOTIFY_CHANGE_SECURITY,
            #         None,
            #         None
            #     )
            #     for action, file in results:
            #         full_filename = os.path.join(path_to_watch, file)
            #         # print(full_filename, ACTIONS.get(action, "Unknown"))
            #         test1 = full_filename[full_filename.rfind('\\') + 1:].lower()
            #         # print(test1)
            #         if ACTIONS.get(action) == 'Создан':
            #             my_file = open('test5.txt', 'a', encoding='utf-8')
            #             # print(full_filename, ACTIONS.get(action, "Unknown"))
            #             my_file.write(str(full_filename) + '|' + str(test1) + '\n')
            #             my_file.close()
            #         if ACTIONS.get(action) == 'Удален':
            #             my_file = open('test5.txt', 'a', encoding='utf-8')
            #             # print(full_filename, ACTIONS.get(action, "Unknown"))
            #             stroka = (str(full_filename) + '|' + str(test1) + '\n')
            #             temp = []
            #             # print('Имя по которому я сравниваю удаление=', stroka)
            #             with open('test5.txt', encoding='utf-8') as inp:
            #                 for i in inp.readlines():
            #                     # print(i)
            #                     if i != r'' + stroka:
            #                         temp.append(i)
            #             my_file.close()
            #
            #             file_out = open('test5.txt', 'w', encoding="utf-8", errors='ignore')
            #             for i in temp:
            #                 file_out.write(i)
            #             file_out.close()

        except KeyboardInterrupt:
            self._clean_up()
            print("Пока!")

    def osrun(self, cmd):
        PIPE = subprocess.PIPE
        p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)

    def openurl(self, url, ans):
        webbrowser.open(url)
        self.say(str(ans))
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    def say(self, phrase):
        tts = gTTS(text=phrase, lang="ru")
        tts.save(self._mp3_name)

        # Play answer
        mixer.music.load(self._mp3_name)
        mixer.music.play()
        if (os.path.exists(self._mp3_nameold)):
            os.remove(self._mp3_nameold)

        now_time = datetime.datetime.now()
        self._mp3_nameold = self._mp3_name
        self._mp3_name = now_time.strftime("%d%m%Y%I%M%S") + ".mp3"

    def _clean_up(self):
        def clean_up():
            os.remove(self._mp3_name)


def main():
    ai = Speech_AI()
    ai.work()


main()
