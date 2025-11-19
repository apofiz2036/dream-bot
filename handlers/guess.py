import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from utils.database import save_divination, deduct_limits, get_user_info_by_user_id
from utils.gpt import ask_gpt
from handlers.base import main_menu
from utils.logging import setup_logging, send_error_to_admin
from utils.prices import load_prices


# Инициализация логгера
logger = logging.getLogger(__name__)
setup_logging()


async def guess_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Активирует режим гадания"""
    try:
        context.user_data['mode'] = 'dreams'
        keyboard = [['Главное меню']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"Опишите ваш сон. Чем больше деталей вы укажете тем лучше будет трактовка. Особенно обратите внимание на свои эмоции во время сна",
            reply_markup=reply_markup
        )
    except Exception as e:
        error_message = f"Ошибка в guess_mode: {e}"
        logger.error(error_message)
        await send_error_to_admin(context.bot, error_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает пользовательские сообщения в зависимости от текущего режима."""
    try:
        # Игнорируем нажатие кнопок в меню    
        if update.message.text in ["Трактовать сон", "Как трактовать", "Главное меню"]:
            return

        current_mode = context.user_data.get('mode')

        # Если режим не установлен возвращаемся в главное меню
        if current_mode != 'dreams':
            await main_menu(update, context)
            return

        user_question = update.message.text   

        handlers = {
            'dreams': lambda: interpretation(update, user_question),
        }

        if current_mode in handlers:
            await handlers[current_mode]()
        
        await main_menu(update, context)
    except Exception as e:
        error_message = f"Ошибка в handle_message: {e}"
        logger.error(error_message)
        await send_error_to_admin(context.bot, error_message)         


async def interpretation(update: Update, question: str) -> None:
    """Обрабатывает запрос для режима трактования"""
    try:
        user_id = update.message.from_user.id
        prices = load_prices()
        price = prices.get("one_dream", 10)
        
        # Проверка лимитов
        success, _, limits = await get_user_info_by_user_id(user_id)
        if not success or limits < price:
            await update.message.reply_text(
                "У вас недостаточно лимитов. "
                "Дождитесь пополнения или напишите админу @Apofiz2036"
            )
            return
        
        # Списываем
        if not await deduct_limits(user_id, price):
            await update.message.reply_text(
                "Не удалось списать лимиты. Попробуйте позже."
            )
            return  
        
        gpt_response = await ask_gpt(question)

        await save_divination(user_id) #ТУТА ВНИМАТЕЛЬНО!

        await update.message.reply_text(gpt_response)
    except Exception as e:
        error_message = f"Ошибка в interpretation: {e}"
        logger.error(error_message)
        await send_error_to_admin(update.get_bot(), error_message)
