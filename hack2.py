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

bot = telebot.TeleBot('6146992110:AAGO_ksYCCJEl3uK2Hzt8fGr951Ch2dqOSA')

adm = 842558224


def markup(par):
    test_markup = types.InlineKeyboardMarkup(row_width=2)
    test_but_1 = types.InlineKeyboardButton(text="➡️", callback_data='next')
    cnt_but = types.InlineKeyboardButton(text=f"{par + 1} из 3", callback_data='cnt')
    test_but_2 = types.InlineKeyboardButton(text="⬅️", callback_data='back')
    test_markup.add(test_but_2, cnt_but, test_but_1, row_width=3)

    return test_markup


parameter = 0
ans = []
answers_list = []

def voice_recognizer():
	 # Преобразуем аудиосообщение в текст
    recognizer = sr.Recognizer()

    with sr.AudioFile("C:/Users/user/PycharmProjects/testing/bot/file.wav") as source:
        audio = recognizer.record(source)

    text = recognizer.recognize_google(audio, language='ru')
    return text


def ogg_to_wav():
    ogg_file = "C:/Users/user/PycharmProjects/testing/bot/audio.ogg"
    wav_file = "C:/Users/user/PycharmProjects/testing/bot/file.wav"

    # Чтение ogg файла
    ogg_data, ogg_samplerate = sf.read(ogg_file)

    # Запись wav файла
    sf.write(wav_file, ogg_data, ogg_samplerate)

def find_answer(question: str, answers_list):
    final_answer = []
    questions = [question]
    responses = answers_list
    response_contexts = answers_list

    module = hub.load('https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/3')

    question_embeddings = module.signatures['question_encoder'](
        tf.constant(questions))
    response_embeddings = module.signatures['response_encoder'](
        input=tf.constant(responses),
        context=tf.constant(response_contexts))

    res = np.inner(question_embeddings['outputs'], response_embeddings['outputs'])

    arr = np.array(res.tolist()[0])
    max_indexes = (np.argpartition(arr, -3)[-3:])
    for i in max_indexes:
        final_answer.append(answers_list[i])

    r = list(reversed(final_answer))

    return r


@bot.message_handler(commands=['start'])
def start(message):
    global answers_list
    photo = open('фото.webp', 'rb')
    keyboard = types.InlineKeyboardMarkup(
        [
            {
                # types.InlineKeyboardButton(text='Наш сайт', web_app=types.WebAppInfo('https://zakupki.mos.ru/'))#Как  вариант но на пк выглядит плохо
                types.InlineKeyboardButton(text='Наш сайт', url='https://zakupki.mos.ru/')
            },
            {
                types.InlineKeyboardButton(text='Задать вопрос', callback_data='question')
            },
            {
                types.InlineKeyboardButton(text='Вызвать менеджера', callback_data='meneger')
            },
            {
                types.InlineKeyboardButton(text='О нас', callback_data='info')
            }
        ]
    )
    bot.send_photo(message.chat.id, photo, caption='Добро пожаловать в "Портал Поставщиков"',
                   reply_markup=keyboard)  # Как вариант сделать побольше текста, но из меня плохой копирайтер
    data = pd.read_excel('C:/Users/user/PycharmProjects/testing/bot/11.xlsx')
    answers_list = (data["ОТВЕТ"].to_list())
    print(answers_list)




@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    global parameter
    if call.data == 'next':
        parameter += 1

        if parameter >= len(ans) or parameter < 0:
            parameter = 0

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=ans[parameter],
                              reply_markup=markup(parameter))

    if call.data == 'back':
        parameter -= 1
        if parameter >= len(ans) or parameter < 0:
            parameter = 2
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=ans[parameter],
                              reply_markup=markup(parameter))
    if call.data == 'info':
        photo = open('Фото 2.PNG', 'rb')
        keyboard = types.InlineKeyboardMarkup(
            [
                {
                    types.InlineKeyboardButton(text='В меню', callback_data='menu')
                }
            ]
        )
        bot.send_photo(call.message.chat.id, photo, caption='Портал поставщиков — Интернет-ресурс, предназначенный для '
                                                            'автоматизации деятельности заказчиков и поставщиков при '
                                                            'осуществлении оперативных сделок и повышения открытости и '
                                                            'прозрачности контрактных отношений.\n'
                                                            '\n'
                                                            ' Портал обеспечивает '
                                                            'повышение конкурентоспособности потенциальных поставщиков, '
                                                            'а также возможность объективной оценки существующего рынка '
                                                            'предложений и анализа сведений о выполнении обязательств '
                                                            'поставщиками со стороны государственных и коммерческих '
                                                            'заказчиков', reply_markup=keyboard)
    if call.data == 'menu':
        photo = open('фото.webp', 'rb')
        kerboard = types.InlineKeyboardMarkup(
            [
                {
                    # types.InlineKeyboardButton(text='Наш сайт', web_app=types.WebAppInfo('https://zakupki.mos.ru/'))#Как  вариант но на пк выглядит плохо
                    types.InlineKeyboardButton(text='Наш сайт', url='https://zakupki.mos.ru/')
                },
                {
                    types.InlineKeyboardButton(text='Задать вопрос', callback_data='question')
                },
                {
                    types.InlineKeyboardButton(text='Вызвать менеджера', callback_data='meneger')
                },
                {
                    types.InlineKeyboardButton(text='О нас', callback_data='info')
                }
            ]
        )
        bot.send_photo(call.message.chat.id, photo, caption='Выбирите интересующий вас раздел',reply_markup=kerboard)
    if call.data == 'meneger':
        keyboard = types.InlineKeyboardMarkup(
            [
                {
                    types.InlineKeyboardButton(text='В меню', callback_data='menu')
                }
            ]
        )
        msg = bot.send_message(call.message.chat.id, 'Введите свой вопрос',reply_markup=keyboard)
        bot.register_next_step_handler(msg, forward_adm)
    if call.data == 'question':
        keyboard = types.InlineKeyboardMarkup(
            [
                {
                    types.InlineKeyboardButton(text='В меню', callback_data='menu')
                }
            ]
        )
        bot.send_message(call.message.chat.id, 'Введите свой вопрос', reply_markup=keyboard)


@bot.message_handler(content_types=["voice"])
def handle_audio_message(message):
    global ans, parameter
    # Получаем файл аудиосообщения
    file_info = bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    save_path = "C:/Users/user/PycharmProjects/testing/bot/audio.ogg"

    downloaded_file = bot.download_file(file_path)
    with open(save_path, "wb") as f:
        f.write(downloaded_file)

    ogg_to_wav()

    ans = find_answer(voice_recognizer(), answers_list)

    bot.send_message(message.chat.id, ans[parameter], reply_markup = markup(parameter))


@bot.message_handler(content_types=['text'])
def message(message):
    global ans, parameter

    ans = find_answer(message.text, answers_list)
    bot.send_message(message.chat.id, ans[parameter], reply_markup=markup(parameter))

def forward_adm(message):
    print('forward_adm')
    print(message.chat.id)
    bot.send_message(adm, 'Новый вопрос :{}'.format(message.text))





bot.polling(none_stop=True, interval=0)
