from aiogram import *
from .settings import dispatcher, Session, answers_dict, bot, id_admin, test_name
from .modeles import Users, Results
from .ask_question import send_question
import modules.ask_question as ask_question
import json, os
from .message_handler import list_answers_one

dict_message_id = {}
@dispatcher.callback_query()
async def enter_answer(callback: types.CallbackQuery):
    global test_name
    if 'start_quiz' in callback.data:
        session = Session()
        all_users = session.query(Users).all()
        answers_dict['question_0'] = {}
        path_to_json = os.path.abspath(__file__ + f'/../../quizes/{callback.data.split('%')[-1]}')
        test_name = callback.data.split('%')[-1].split('.')[-2]
        with open(path_to_json, 'r') as file:
            ask_question.questions = json.load(file)['questions']
        for user in all_users:
            dict_message_id[user.id] = await send_question(user, 0)
    elif 'delete_quiz' in callback.data:
        file_name = callback.data.split('%')[-1]
        path_to_file = os.path.abspath(__file__ + f'/../../quizes/{file_name}')
        os.remove(path_to_file)
        await callback.answer('Тест видалено')
    else:
        session = Session()
        user_id = callback.from_user.id
        user = session.query(Users).filter_by(telegram_id = user_id).first()
        question_id = int(callback.data.split('_')[-2])
        all_users = session.query(Users).all()
        count_users = len(all_users)
        if int(callback.data.split('_')[-1]) == ask_question.questions[question_id]['correct_id']:
            answers_dict[f'question_{question_id}'][f'user_{user.id}'] = True
        else:
            answers_dict[f'question_{question_id}'][f'user_{user.id}'] = f'select_answer_{(int(callback.data.split('_')[-1]))}'
        answer_id = int(callback.data.split('_')[-1])
        await send_question(user, question_id, answer_id, callback.message.message_id)
        count_answers = len(answers_dict[f'question_{question_id}'])
        count_questions = len(ask_question.questions)
        if count_answers == count_users:
            if question_id + 1 == count_questions:
                for user in all_users:
                    message_id = dict_message_id[user.id]
                    user_tg_id = user.telegram_id
                    await bot.delete_message(user_tg_id, message_id)
                string_to_admin = 'Результати:\n\n'
                average_score = 0
                quiz_id = 1
                all_results = session.query(Results).all()
                if len(all_results) > 0:
                    quiz_id = all_results[-1].quiz_id + 1 
                for user in all_users:
                    user_result = 0
                    for key in answers_dict.keys():
                        if answers_dict[key][f'user_{user.id}'] == True:
                            user_result += 1
                    result = Results(score = user_result, user = user, quiz_id = quiz_id)
                    session.add(result)
                    session.commit()
                    string_result = f'{user.full_name}, ваш результат у тесті {test_name} - {user_result}/{count_questions}\n\n'
                    await bot.send_message(user.telegram_id, string_result)
                    for i in range(count_questions):
                        list_buttons2 = []
                        correct_id = ask_question.questions[i]['correct_id']
                        correct_answer = ask_question.questions[i]['answers']
                        correct_question = ask_question.questions[i]['question']
                        for j in range(len(correct_answer)):
                            button = types.InlineKeyboardButton(text = correct_answer[j], callback_data = f'answer_{i}')
                            if j == correct_id:
                                button = types.InlineKeyboardButton(text = f'✅ {correct_answer[j]} ✅', callback_data = f'answer_{i}')
                            if answers_dict[f'question_{i}'][f'user_{user.id}'] != True:
                                if j == int(answers_dict[f'question_{i}'][f'user_{user.id}'].split('_')[-1]):
                                    button = types.InlineKeyboardButton(text = f'❌ {correct_answer[j]} ❌', callback_data = f'answer_{i}')
                            list_buttons2.append(button)
                        keyboard = types.InlineKeyboardMarkup(inline_keyboard = [[list_buttons2[0], list_buttons2[1]],[list_buttons2[2], list_buttons2[3]]])
                        message_id_result = await bot.send_message(user.telegram_id, correct_question, reply_markup = keyboard)
                        if answers_dict[f'question_{i}'][f'user_{user.id}'] == True:
                            string_result += f'Ваша відповідь на {i} питання - {correct_answer[correct_id]} ✅\n'
                            
                        else:
                            select_id = answers_dict[f'question_{i}'][f'user_{user.id}'].split('_')[-1]
                            string_result += f'Ваша відповідь на {i} питання - {correct_answer[int(select_id)]} ❌, правильна відповідь - {correct_answer[correct_id]}\n'
                    string_to_admin += f'{user.full_name}: {user_result}/{count_questions}\n'
                    average_score += user_result
                average_score /= count_users
                string_to_admin += f'\nСередній результат: {round(average_score, 2)}'
                await bot.send_message(id_admin, string_to_admin)
            else:
                answers_dict[f'question_{question_id + 1}'] = {}
                answer_id = 5
                question_id = int(callback.data.split('_')[-2])
                for user in all_users:
                    message_id = dict_message_id[user.id]
                    await send_question(user, question_id + 1, answer_id, message_id)
    