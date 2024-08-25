from .settings import Session, bot, dispatcher, id_admin, answers_dict
from .modeles import *
from aiogram import filters, types
from .ask_question import send_question
import os

admin_send_file = False
@dispatcher.message(filters.CommandStart())
async def start_command(message):
    session = Session()
    telegram_id = message.from_user.id
    user = session.query(Users).filter_by(telegram_id = telegram_id).first()
    if user == None:
        user = Users(full_name = message.from_user.first_name, telegram_id = telegram_id)
        session.add(user)
        session.commit()
        await message.answer(f"Ви успішно авторизовані")
    else:
        await message.answer('Ви вже авторизовані')
    session.close()
@dispatcher.message(filters.Command(commands = ['start_quiz']))
async def start_quiz(message):
    session = Session()
    if message.from_user.id != id_admin:
        await message.answer('У вас немає дозволу на проведення тесту')
        return False
    list_buttons = []
    path_quizes = os.path.abspath(__file__ + '/../../quizes')
    for quiz in os.listdir(path_quizes):
        button = types.InlineKeyboardButton(text = quiz.split('.')[0], callback_data = f'start_quiz%{quiz}')
        list_buttons.append([button])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard = list_buttons)
    await message.answer('Виберіть тест', reply_markup = keyboard)
@dispatcher.message(filters.Command(commands = ['quiz_template']))
async def quiz_template(message):
    if message.from_user.id == id_admin:
        path_template = os.path.abspath(__file__ + '/../../quiz.json')
        file = types.FSInputFile(path_template)
        await bot.send_document(message.from_user.id, file, caption = 'Файл приклад тесту')
@dispatcher.message(filters.Command(commands = ['send_quiz']))
async def send_quiz(message):
    global admin_send_file
    if message.from_user.id == id_admin:
        await message.answer('Відправте назву файлу')
        admin_send_file = 'send_text'
@dispatcher.message(filters.Command(commands = ['delete_test']))
async def delete_test(message):
    if message.from_user.id == id_admin:
        path_quizes = os.path.abspath(__file__ + '/../../quizes')
        list_buttons = []
        for quiz in os.listdir(path_quizes):
            button = types.InlineKeyboardButton(text = quiz.split('.')[0], callback_data = f'delete_quiz%{quiz}')
            list_buttons.append([button])
        keyboard = types.InlineKeyboardMarkup(inline_keyboard = list_buttons)
        await message.answer('Виберіть тест для видалення', reply_markup = keyboard)
@dispatcher.message(filters.Command(commands = ['my_result']))
async def my_result(message):
    session = Session()
    user = session.query(Users).filter_by(telegram_id = message.from_user.id).first()
    results = session.query(Results).filter_by(user = user).all()
    string = 'Ваші результати:\n\n'
    for result in results:
        awarage_score = 0
        all_results = session.query(Results).filter_by(quiz_id = result.quiz_id).all()
        for i in all_results:
            awarage_score += i.score
        awarage_score /= len(all_results)
        string += f'У {result.quiz_id} тесті ви набрали - {result.score} бали, середній результат - {awarage_score}\n'
    await message.answer(string)
@dispatcher.message()
async def get_file(message):
    global admin_send_file
    if message.document != None:
        if message.from_user.id == id_admin and 'send_file' in admin_send_file:
            file = await bot.get_file(message.document.file_id)
            print(admin_send_file)
            file_name = admin_send_file.split('%')[-1]
            file_path = file.file_path
            path_to_save = os.path.abspath(__file__ + f'/../../quizes/{file_name}.json')
            await bot.download_file(file_path, path_to_save)
            await message.answer('Файл було завантажено')
            admin_send_file = False
    else:
        if admin_send_file == 'send_text' and message.from_user.id == id_admin:
            admin_send_file = f'send_file%{message.text}'
            await message.answer('Відправте файл')
    