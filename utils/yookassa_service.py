from yookassa import Configuration, Payment
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


async def create_payment(user_id, amount, public_id):
    Configuration.configure(Configuration.account_id, Configuration.secret_key, sandbox=True)

    payment_data = {
        "amount": {
            "value": f"{amount:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/your_bot_username"
        },
        "capture": True,
        "description": f"Пополнение лимитов для пользователя {public_id}",
        "metadata": {
            "public_id": public_id,
            "bot_name": "dream_bot"
        }
    }

    payment = Payment.create(payment_data)
    return payment.confirmation.confirmation_url, payment.id
