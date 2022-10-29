import asyncio
import logging
import load_logs
import input_cmd
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


# Машина состояний пользователя
class FSMUser(StatesGroup):
    lesson_type = State()  # тип урока
    name = State()  # ФИО пользователя
    phone_number = State()  # номер телефона пользователя
    visit_time = State()  # удобное время визита


"""
# Машина состояний админов, будет необходима для верификации
# p.s. Админам будут приходить данные введенные пользователями после прохождения записи на занятия
class FSMAdmin(StatesGroup):
    tg_name = State()
    tg_id = State()
    password = State()
"""

# FSM - подгружать будет в оперативку
# Лучше использовать другие способы! Так как при отключении бота все данные обнуляться
# Но в нашем случае данные пользователей нигде не будут хранится
# Кроме самого телеграмма
storage = MemoryStorage()

# Включение логирования -- необходимо для важных сообщений
logging.basicConfig(level=logging.INFO)

# Инициализация объекта бота
bot = Bot(token="")

# Диспетчер
disp = Dispatcher(bot=bot, storage=storage)

"""
# Начало авторизации админа /admin
@disp.message_handler(commands=["admin"], state=None)
async def command_admin_аuthorization(message: types.Message):
    await FSMAdmin.tg_name.set()
    await message.reply("send password:")
    await FSMAdmin.next()


# Проверка пароля
@disp.message_handler(content_types=["text"], state=FSMAdmin.all_states)
async def admin_data_password(message: types.Message, state: FSMAdmin.password):
    async with state.proxy() as data:
        data['password'] = message.text
        data['tg_name'] = message.from_user.first_name
        data['tg_id'] = message.from_user.id
    if data['password'] == "qwerty":
        await message.reply(f"welcome! {data['tg_name']}, {data['tg_id']}")
        await state.finish()
    else:
        await message.reply("sorry!")
        await state.finish()
"""


# Обработка команды /start
@disp.message_handler(commands=["start"])
async def command_start(message: types.Message):
    input_cmd.cmd_log(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    item = "/записаться"
    markup.add(item)
    await message.answer("🤖Вас приветствует телеграм бот созданный учениками🤖\n"
                         "🤖Я помогу вам записаться на занятия🤖", reply_markup=markup)


# Начало диалога записи на занятия
@disp.message_handler(commands=["записаться"], state=None)
async def command_start_registration(message: types.Message):
    input_cmd.cmd_log(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    item1 = "Пробное занятие"
    item2 = "Постоянные занятия"
    markup.add(item1, item2)
    await FSMUser.lesson_type.set()
    await message.reply("На какой из типов занятий вы бы хотели записаться?",
                        reply_markup=markup)


# Ловим первый ответ и записываем в словарь
@disp.message_handler(content_types=["text"], state=FSMUser.lesson_type)
async def load_lesson_type(message: types.Message, state: FSMContext):
    input_cmd.cmd_log(message)
    async with state.proxy() as data:
        data['lesson_type'] = message.text
    await FSMUser.next()
    await message.reply("Теперь введите ваше ФИО", reply_markup=types.ReplyKeyboardRemove())


# Ловим второй ответ и записываем в словарь
@disp.message_handler(state=FSMUser.name)
async def load_name(message: types.Message, state: FSMContext):
    input_cmd.cmd_log(message)
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMUser.next()
    await message.reply("Введите свой номер телефона(Пример: 7-999-999-99-99)")


# Ловим второй ответ и записываем в словарь
@disp.message_handler(state=FSMUser.phone_number)
async def load_name(message: types.Message, state: FSMContext):
    input_cmd.cmd_log(message)
    async with state.proxy() as data:
        data['phone_number'] = message.text
    await FSMUser.next()
    await message.reply("Введите время удобного вам визита(Пример: 17.11.22 18:30)")


# Ловим третий ответ и записываем в словарь
@disp.message_handler(state=FSMUser.visit_time)
async def load_visit_time(message: types.Message, state: FSMContext):
    input_cmd.cmd_log(message)
    async with state.proxy() as data:
        data['visit_time'] = message.text
    await message.answer("Благодарим вас за запись!\n"
                         "💻Мы с вами свяжемся💻")
    await state.finish()
    # Отправляем все данные администраторам, бот не хранит данные в бд
    load_logs.load_txt(data['name'], data['phone_number'], data['lesson_type'], data['visit_time'])

    with open("admins.txt", "r") as admins_file:
        for i in admins_file:
            i = str(i).replace("\n", "")
            await bot.send_message(chat_id=int(i), text="Новый пользователь хочет записаться на занятия!")
            await bot.send_message(chat_id=int(i), text="ФИО - {0}\n"
                                                        "Номер телефона - {1}\n"
                                                        "Тип занятия - {2}\n"
                                                        "Время визита - {3}".format(data['name'],
                                                                                    data['phone_number'],
                                                                                    data['lesson_type'],
                                                                                    data['visit_time']))


# Запуск процесса проверки обновлений
async def main():
    print("[log] - бот успешно запущен")
    await disp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
