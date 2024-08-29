import json
import os
import aiogram
from .settings import bot

path_to_json = os.path.abspath(__file__ + '/../../quizes/quiz.json')
with open(path_to_json, 'r') as file:
    questions = json.load(file)['questions']
    

async def send_question(user, index_question, edit = None, message_id = None):
    question = questions[index_question]['question']
    answers = questions[index_question]['answers']
    buttons = []
    for i in range(len(answers)):
        button1 = aiogram.types.InlineKeyboardButton(text = answers[i], callback_data = f'answer_{index_question}_{i}')
        if edit != None:
            button1 = aiogram.types.InlineKeyboardButton(text = answers[i], callback_data = f'answer_{index_question}_{i}')
        if i == edit:
            button1 = aiogram.types.InlineKeyboardButton(text = f'🟩 {answers[i]} 🟩', callback_data = f'answer_{index_question}_{i}')  
        buttons.append(button1)
    keyboard = aiogram.types.InlineKeyboardMarkup(inline_keyboard = [[buttons[0], buttons[1]],[buttons[2], buttons[3]]])
    if edit == None:
        message = await bot.send_message(user.telegram_id, question, reply_markup = keyboard)
        return message.message_id
    else:
        await bot.edit_message_text(text = question, chat_id = user.telegram_id, message_id = message_id, reply_markup = keyboard)
        # await bot.edit_message_reply_markup(chat_id = user.telegram_id, message_id = message_id, reply_markup = keyboard)