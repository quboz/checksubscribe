import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import json
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error("Файл config.json не найден!")
    exit(1)
except json.JSONDecodeError:
    logger.error("Ошибка в формате config.json!")
    exit(1)

# Получение настроек из переменных окружения или config.json
BOT_TOKEN = os.getenv('BOT_TOKEN') or config.get('bot_token')
CHANNELS = config.get('channels', [])

# Для обратной совместимости с переменными окружения
if os.getenv('CHANNEL_ID') and os.getenv('CHANNEL_URL'):
    CHANNELS = [{
        'id': os.getenv('CHANNEL_ID'),
        'url': os.getenv('CHANNEL_URL'),
        'name': 'Канал'
    }]

if not BOT_TOKEN or not CHANNELS:
    logger.error("Не указаны обязательные параметры: BOT_TOKEN и каналы")
    exit(1)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class BotStates(StatesGroup):
    waiting_subscription = State()

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    
    # Создаем клавиатуру с кнопками
    buttons = []
    
    # Добавляем кнопки для всех каналов
    for channel in CHANNELS:
        buttons.append([InlineKeyboardButton(
            text=f"{config['buttons']['channel_button_text']} {channel['name']}", 
            url=channel['url']
        )])
    
    # Добавляем кнопку проверки подписки
    buttons.append([InlineKeyboardButton(
        text=config['buttons']['check_subscription_text'], 
        callback_data="check_subscription"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(
        config['messages']['welcome_message'],
        reply_markup=keyboard
    )
    await state.set_state(BotStates.waiting_subscription)

@dp.callback_query(lambda c: c.data == 'check_subscription')
async def check_subscription(callback_query: types.CallbackQuery, state: FSMContext):
    """Проверка подписки на канал"""
    user_id = callback_query.from_user.id
    
    try:
        # Проверяем подписку пользователя на все каналы
        all_subscribed = True
        for channel in CHANNELS:
            member = await bot.get_chat_member(channel['id'], user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                all_subscribed = False
                break
        
        if all_subscribed:
            # Пользователь подписан на все каналы - отправляем информацию о приложении
            await callback_query.message.edit_text(
                config['messages']['app_info_message'],
                parse_mode='HTML'
            )
            await state.clear()
        else:
            # Пользователь не подписан на все каналы
            await callback_query.answer(
                config['messages']['not_subscribed_message'],
                show_alert=True
            )
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        await callback_query.answer(
            "Произошла ошибка при проверке подписки. Попробуйте позже.",
            show_alert=True
        )

async def main():
    """Главная функция запуска бота"""
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())