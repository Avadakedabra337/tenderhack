import csv
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import tensorflow_text
import pandas as pd
from telebot import *
import speech_recognition as sr
import soundfile as sf
import os
import datetime



bot = telebot.TeleBot("6249887249:AAEAzjED91yc3KEzhQHi4RKl9zll86fyW2Q")

def markup(par):

	test_markup = types.InlineKeyboardMarkup(row_width=2)
	test_but_1 = types.InlineKeyboardButton(text="➡️", callback_data="next")
	cnt_but = types.InlineKeyboardButton(text=f"{par+1} из 3", callback_data="cnt")
	test_but_2 = types.InlineKeyboardButton(text="⬅️", callback_data="back")
	test_markup.add(test_but_2, cnt_but, test_but_1, row_width=3)

	return test_markup

parameter = 0
ans = []
answers_list = []

def voice_recognizer():
	 # Преобразуем аудиосообщение в текст
    recognizer = sr.Recognizer()

    with sr.AudioFile("D:/Python/tenderhack/file.wav") as source:
        audio = recognizer.record(source)

    text = recognizer.recognize_google(audio, language='ru')
    return text


def ogg_to_wav():
	ogg_file = "D:/Python/tenderhack/audio.ogg"
	wav_file = "D:/Python/tenderhack/file.wav"
	
	# Чтение ogg файла
	ogg_data, ogg_samplerate = sf.read(ogg_file)

	# Запись wav файла
	sf.write(wav_file, ogg_data, ogg_samplerate)


def find_answer(question : str, answers_list):
	final_answer = []
	questions = [question]
	responses = answers_list
	response_contexts = answers_list

	
	module = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/3")

	question_embeddings = module.signatures["question_encoder"](
			tf.constant(questions))
	response_embeddings = module.signatures["response_encoder"](
			input=tf.constant(responses),
			context=tf.constant(response_contexts))
	

	res = np.inner(question_embeddings["outputs"], response_embeddings["outputs"])


	arr = np.array(res.tolist()[0])
	max_indexes = (np.argpartition(arr, -3)[-3:])
	for i in max_indexes:
		final_answer.append(answers_list[i])

	r = list(reversed(final_answer))

	return r


@bot.message_handler(commands=["start"])
def start(message):
	global answers_list
	bot.send_message(message.chat.id, "Ну здарова, Отец")
	# data=pd.read_excel("D:/Python/tenderhack/biddata.xlsx")
	# answers_list = (data["Портал самообслуживания"].to_list())
	data=pd.read_excel("D:/Python/tenderhack/data.xlsx")
	answers_list = (data["ОТВЕТ"].to_list())


 
@bot.callback_query_handler(func=lambda c: True)
def inline(c):    
	global parameter
	if c.data == "next":
		parameter +=1
        
		if parameter >= len(ans) or parameter < 0:
			parameter = 0
                
		bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id, text = ans[parameter], reply_markup = markup(parameter))
        

	if c.data == "back":
		parameter -=1
		if parameter >= len(ans) or parameter < 0:
			parameter = 2
		bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id, text = ans[parameter], reply_markup = markup(parameter))

# Функция для обработки аудиосообщений и отправки текстового ответа
@bot.message_handler(content_types=["voice"])
def handle_audio_message(message):
    global ans, parameter
    # Получаем файл аудиосообщения
    file_info = bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    save_path = "D:/Python/tenderhack/audio.ogg"

    downloaded_file = bot.download_file(file_path)
    with open(save_path, "wb") as f:
        f.write(downloaded_file)

    ogg_to_wav()

    ans = find_answer(voice_recognizer(), answers_list)

    bot.send_message(message.chat.id, ans[parameter], reply_markup = markup(parameter))

@bot.message_handler(content_types = ["text"])
def message(message):
  global ans, parameter

  ans = find_answer(message.text, answers_list)
  bot.send_message(message.chat.id, ans[parameter], reply_markup=markup(parameter))

bot.polling(none_stop=True)
