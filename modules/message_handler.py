from .settings import Session, bot, dispatcher, id_admin, answers_dict
from .modeles import *
from aiogram import filters, types
from .ask_question import send_question
import os, json

admin_send_file = False
admin_add_test = False
count = 0
count_question = 0
questions = {}
list_questions = []
list_answers_one = []
list_answers = []
file_dict = {'questions': []}
@dispatcher.message(filters.CommandStart())
async def start_command(message):
    session = Session()
    telegram_id = message.from_user.id
    user = session.query(Users).filter_by(telegram_id = telegram_id).first()
    if user == None:
        user = Users(full_name = message.from_user.first_name, telegram_id = telegram_id)
        session.add(user)
        session.commit()
        await message.answer(f"Ви успішно зареєстрованя, чекайте на запуск тесту")
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
@dispatcher.message(filters.Command(commands = ['add_test']))
async def add_test(message: types.Message):
    global admin_add_test, admin_send_file
    if message.from_user.id == id_admin:
        admin_send_file = False
        admin_add_test = 'add_questions_count'
        await message.answer('Скільки питань буде у тесті?')
@dispatcher.message(filters.Command(commands = ['result']))
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
async def get_file(message: types.Message):
    global admin_send_file, admin_add_test, questions_count, count, list_questions, list_answers, list_answers_one, count_question, correct_answer_index
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
        elif admin_add_test == 'add_questions_count':
            questions_count = int(message.text)
            count = 0
            count += 1
            await message.answer(f'Введіть {count} питання')
            admin_add_test = f'add_question_{count}'
        elif 'add_question_' in admin_add_test:
            if count < questions_count:
                print(questions_count)
                count += 1
                question = message.text
                list_questions.append(question)
                await message.answer(f'Введіть {count} питання')
            elif count == questions_count:
                question = message.text
                list_questions.append(question)
                print(list_questions)
                count = 1
                await message.answer(f'Напишіть {count} варіант відповіді до питання:\n{list_questions[0]}')
                admin_add_test = 'add_answers'
        elif 'add_answers' in admin_add_test:
            if count < 4:
                count += 1
                answer = message.text
                list_answers_one.append(answer)
                await message.answer(f'Напишіть {count} варіант відповіді до питання:\n{list_questions[count_question]}')
            else:
                if count_question < len(list_questions) - 1:
                    count = 1
                    answer = message.text
                    list_answers_one.append(answer)
                    list_answers.append([])
                    list_answers[count_question].append(list_answers_one)
                    list_answers_one = []
                    count_question += 1
                    await message.answer(f'Напишіть {count} варіант відповіді до питання:\n{list_questions[count_question]}')
                else:
                    answer = message.text
                    list_answers_one.append(answer)
                    list_answers.append([])
                    list_answers[count_question].append(list_answers_one)
                    count = 0
                    list_answers_one = []
                    for i in list_answers:
                        for j in i:
                            list_answers_one.append(j)
                    print(list_answers_one)
                    list_buttons = []
                    button1 = types.KeyboardButton(text = list_answers_one[count][0])
                    button2 = types.KeyboardButton(text = list_answers_one[count][1])
                    button3 = types.KeyboardButton(text = list_answers_one[count][2])
                    button4 = types.KeyboardButton(text = list_answers_one[count][3])
                    list_buttons.append(button1)
                    list_buttons.append(button2)
                    list_buttons.append(button3)
                    list_buttons.append(button4)
                    print(list_buttons)
                    keyboard = types.ReplyKeyboardMarkup(keyboard = [[list_buttons[0], list_buttons[1]], [list_buttons[2], list_buttons[3]]])
                    await message.answer(text = f'Оберіть правильну відповідь\n\n{list_questions[0]}', reply_markup = keyboard)
                    admin_add_test = 'add_correct_answer'
        elif 'add_correct_answer' in admin_add_test:
            print(count, questions_count)
            if count < questions_count - 1:
                correct_answer = message.text
                for i in list_answers_one[count]:
                    print(i)
                    if correct_answer == i:
                        correct_answer_index = f'{list_answers_one[count].index(i)}'
                        break
                file_dict['questions'].append({"question": list_questions[count], "answers": list_answers_one[count], "correcrt_id": correct_answer_index})
                print(file_dict)
                count += 1
                list_buttons = []
                button1 = types.KeyboardButton(text = list_answers_one[count][0])
                button2 = types.KeyboardButton(text = list_answers_one[count][1])
                button3 = types.KeyboardButton(text = list_answers_one[count][2])
                button4 = types.KeyboardButton(text = list_answers_one[count][3])
                list_buttons.append(button1)
                list_buttons.append(button2)
                list_buttons.append(button3)
                list_buttons.append(button4)
                keyboard = types.ReplyKeyboardMarkup(keyboard = [[list_buttons[0], list_buttons[1]], [list_buttons[2], list_buttons[3]]])
                await message.answer(text = f'Оберіть правильну відповідь\n\n{list_questions[count]}', reply_markup = keyboard)
            elif count == questions_count - 1:
                correct_answer = message.text
                for i in list_answers_one[count]:
                    print(i)
                    if correct_answer == i:
                        correct_answer_index = f'{list_answers_one[count].index(i)}'
                        break
                file_dict['questions'].append({"question": list_questions[count], "answers": list_answers_one[count], "correcrt_id": correct_answer_index})
                count += 1
                await message.answer('Дайте назву вашому тесту')
                admin_add_test = 'add_test_name'
        elif 'add_test_name' in admin_add_test:
            test_name = message.text + '.json'
            path_folder = os.path.abspath(__file__ + f'/../../quizes/{test_name}')
            with open(path_folder, 'w', encoding = 'utf-8') as file:
                json.dump(file_dict, file, indent = 4, ensure_ascii = False) 
            await message.answer(f'Тест "{test_name}" успішно створено', reply_markup = types.ReplyKeyboardRemove())
            admin_add_test = False