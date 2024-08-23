from aiogram import *
from .settings import dispatcher, Session, answers_dict, bot, id_admin
from .modeles import Users, Results
from .ask_question import questions, send_question

@dispatcher.callback_query()
async def enter_answer(callback: types.CallbackQuery):
    session = Session()
    user_id = callback.from_user.id
    user = session.query(Users).filter_by(telegram_id = user_id).first()
    question_id = int(callback.data.split('_')[-2])
    all_users = session.query(Users).all()
    count_users = len(all_users)
    if int(callback.data.split('_')[-1]) == questions[question_id]['correct_id']:
        answers_dict[f'question_{question_id}'][f'user_{user.id}'] = True
    else:
        answers_dict[f'question_{question_id}'][f'user_{user.id}'] = False
    count_answers = len(answers_dict[f'question_{question_id}'])
    count_questions = len(questions)
    if count_answers == count_users:
        if question_id + 1 == count_questions:
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
                await bot.send_message(user.telegram_id, f'{user.full_name}, ваш результат - {user_result}/{count_questions}')
                string_to_admin += f'{user.full_name}: {user_result}/{count_questions}\n'
                average_score += user_result
            average_score /= count_users
            string_to_admin += f'\nСередній результат: {average_score}'
            await bot.send_message(id_admin, string_to_admin)
        else:
            answers_dict[f'question_{question_id + 1}'] = {}
            for user in all_users:
                await send_question(user, question_id + 1)