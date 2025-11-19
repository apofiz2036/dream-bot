from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.database import top_up_limits, get_user_info_by_user_id, get_user_limits
from utils.yookassa_service import create_payment
from handlers.base import main_menu
from handlers.guess import handle_message
from handlers.guess import handle_message
import logging

logger = logging.getLogger(__name__)


async def payment_message(update, context):
    context.user_data['mode'] = 'payment'

    keyboard = [['Главное меню']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Введите сумму, на которую хотите пополнить лимиты (только число):",
        reply_markup=reply_markup
    )


async def get_link_topayment(update, context):
    user_id = update.effective_user.id

    text = update.message.text.strip()
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except:
        await update.message.reply_text("Пожалуйста, введите корректную сумму числом.")
        await main_menu(update, context)
        return

    payment_url, payment_id = await create_payment(user_id, amount)

    context.user_data.pop('mode', None)

    await update.message.reply_text(
        f"💳 Ссылка на оплату {amount:.2f} ₽:\n\n"
        f"{payment_url}\n\n"
        f"После успешной оплаты лимиты будут зачислены автоматически."
    )


async def handle_payment_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ввод суммы для оплаты"""
    try:
        if context.user_data.get('mode') != 'payment':
            await handle_message(update, context)
            return
        
        text = update.message.text.strip()

        if text in ["Главное меню", "Трактовать сон", "Как трактовать", "Мои лимиты", "Пополнить лимиты"]:
            from main import handle_menu  # Импортируем здесь, чтобы избежать циклического импорта
            await handle_menu(update, context)
            return
        
        await get_link_topayment(update, context)
    except Exception as e:
        error_message = f"Ошибка в handle_payment_input: {e}"
        logger.error(error_message)
        await main_menu(update, context)