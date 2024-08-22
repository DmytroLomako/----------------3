import json
import os
import aiogram
from .settings import bot

path_to_json = os.path.abspath(__file__ + '/../../quiz.json')
with open(path_to_json, 'r') as file:
    questions = json.load(file)['questions']
    

async def send_question(user, index_question):
    question = questions[index_question]['question']
    answers = questions[index_question]['answers']
    buttons = []
    for i in range(len(answers)):
        button1 = aiogram.types.InlineKeyboardButton(text = answers[i], callback_data = f'answer_{index_question}_{i}')
        buttons.append(button1)
    print(buttons)
    keyboard = aiogram.types.InlineKeyboardMarkup(inline_keyboard = [[buttons[0], buttons[1]],[buttons[2], buttons[3]]])
    await bot.send_message(user.telegram_id, question, reply_markup = keyboard)