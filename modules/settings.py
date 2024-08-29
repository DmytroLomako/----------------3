from aiogram import *
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

api_token = 
bot = Bot(token=api_token)
dispatcher = Dispatcher()

connection = create_engine('sqlite:///data.db')
Base = declarative_base()
Session = sessionmaker(bind = connection)

id_admin = 
answers_dict = {}
test_name = None