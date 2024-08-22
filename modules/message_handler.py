from .settings import Session, bot, dispatcher, id_admin
from .modules import *
from aiogram import filters
from .ask_question import send_question

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
    all_users = session.query(Users).all()
    print(all_users)
    for user in all_users:
        await send_question(user, 0)