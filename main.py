from aiogram import Bot, Dispatcher, types
import logging
import asyncio
import filejob_student
from config import *
from aiogram.dispatcher.filters import Command, Text
from models import *
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
engine = create_engine(DATA_BASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

COURSE = [x[0] for x in session.query(Groups.course).distinct().all()]
command_table = ['Расписание на завтра', 'Расписание', "Расписание на неделю", "this_day", 'next_day', 'all_week']


@dp.message_handler(Command(commands=["start", 'reset']))
async def start(message: types.Message):
    try:
        new_user = Users(chat_id=message.chat.id, username=message.from_user.username)
        session.add(new_user)
        session.commit()
    except Exception:
        pass
    buttons = [types.InlineKeyboardButton(text="Бот в ВК", url='https://vk.com/kspguti_bot'),
               types.InlineKeyboardButton(text='Создатель бота в тг', url='https://vk.com/ultimap'),
               types.InlineKeyboardButton(text='Создатель бота в вк', url='https://vk.com/ky43err8')]
    markup = types.InlineKeyboardMarkup(row_width=1).add(*buttons)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text='Пройти регистрацию'))
    await message.answer('Вас приветсвует бот рассписания КС ПГУТИ', reply_markup=markup)
    await message.answer('Для начала необходимо пройти регистрацию', reply_markup=keyboard)


# РЕГИСТРАЦИЯ И ИЗМЕНЕНИЯ ГРУППЫ
@dp.message_handler(Command(commands=['register', 'edit_group']))
@dp.message_handler(Text('Пройти регистрацию'))
async def register(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2).add(
        *[types.InlineKeyboardButton(text=x, callback_data=x) for x in COURSE])
    await message.answer('Выберете курс', reply_markup=markup)


@dp.callback_query_handler(lambda c: True)
async def course_to_group(cb: types.CallbackQuery):
    try:
        if int(cb.data) in COURSE:
            groups = [x.group_name for x in
                      session.query(Groups.group_name).filter(Groups.course == int(cb.data)).all()]
            markup = types.InlineKeyboardMarkup(row_width=3).add(
                *[types.InlineKeyboardButton(text=x, callback_data=x) for x in groups])
            await bot.edit_message_text(chat_id=cb.message.chat.id, message_id=cb.message.message_id,
                                        text="Выберите группу",
                                        reply_markup=markup)
    except Exception as e:
        pass
    if cb.data in [x[0] for x in session.query(Groups.group_name).all()]:
        group = session.query(Groups).filter(Groups.group_name == cb.data).first().group_url
        user = session.query(Users).where(Users.chat_id == cb.message.chat.id).first()
        user.group_url = group
        session.commit()
        command = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
            *[types.KeyboardButton(text=x) for x in command_table[0:3]])
        await bot.delete_message(chat_id=cb.message.chat.id, message_id=cb.message.message_id)
        await bot.send_message(chat_id=cb.message.chat.id, text="Регистрация успешно пройдена",
                               reply_markup=command)


# КОНЕЦ РЕГИСТРАЦИИ


# ВЫДАЧА РАСПИСАНИЯ
@dp.message_handler(Text(equals=command_table))
@dp.message_handler(Command(commands=command_table))
async def send_this_day(message: types.Message):
    if session.query(Users).where(Users.chat_id == message.chat.id).first().group_url:
        url = session.query(Users).where(Users.chat_id == message.chat.id).first().group_url
        group_name = session.query(Groups).where(Groups.group_url == url).first().group_name
        if message.text in ("Расписание", '/this_day'):
            await message.answer(
                filejob_student.send_this_day(url, group_name))
        elif message.text in ('Расписание на завтра', '/next_day'):
            await message.answer(
                filejob_student.send_next_day(url, group_name))
        elif message.text in ("Расписание на неделю", '/all_week'):
            await message.answer(
                filejob_student.send_all_week(url, group_name))
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text='Пройти регистрацию'))
        await message.answer('Для начала необходимо пройти регистрацию', reply_markup=keyboard)


# КОНЕЦ ВЫДАЧИ РАСПИСАНИЯ

# УДАЛИТЬ ВЫБРАННУЮ ПОЛЬЗОВАТЕЛЕМ ГРУППУ ИЗ БАЗЫ ДАННЫХ
@dp.message_handler(Command('delete'))
async def delete(message: types.Message):
    user = session.query(Users).where(Users.chat_id == message.chat.id).first()
    user.group_url = None
    session.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text='Пройти регистрацию'))
    await message.answer("Выбранная группа успешно удалена", reply_markup=markup)


# СКРЫТЬ ПОКАЗАТЬ КНОПКИ
@dp.message_handler(Command('hide_button'))
async def hide(message: types.Message):
    markup = types.ReplyKeyboardRemove()
    await message.answer('Кнопки скрыты', reply_markup=markup)


@dp.message_handler(Command('show_button'))
async def show(message: types.Message):
    if session.query(Users).where(Users.chat_id == message.chat.id).first().group_url:
        command = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
            *[types.KeyboardButton(text=x) for x in command_table[0:3]])
    else:
        command = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text='Пройти регистрацию'))
    await message.answer("Кнопки снова позываются", reply_markup=command)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
