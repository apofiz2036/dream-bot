import os
import aiohttp
import logging
from pathlib import Path
from typing import Dict, Union, List
from utils.logging import setup_logging, send_error_to_admin
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID


# Инициализация логгера
logger = logging.getLogger(__name__)
setup_logging()

def load_prompt() -> str:
    """Загружает промпт из файла по указанному типу."""
    try:
        file_name = f'text/prompt.txt'
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        error_message = f"Ошибка в load_prompt: {e}"
        logger.error(error_message)
        return ""
    

async def ask_gpt(user_question: str) -> str:
    """Отправляет запрос к Yandex GPT API для интерпретации"""
    try:
        prompt = load_prompt().format(question=user_question)

        # Подготовка данных для запроса к Yandex GPT API
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "x-folder-id": YANDEX_FOLDER_ID,
        }
        data = {
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
            "messages": [
                {
                    "role": "system", 
                    "text": "Ты профессиональный психолог. Твоя задача — интерпретировать сон пользователя, опираясь на современные психологические знания о сновидениях."
                },
                {"role": "user", "text": prompt},
            ],
        }      

        # Отправка асинхронного запроса
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=data) as response:
                    response.raise_for_status()
                    json_data = await response.json()
                    return json_data["result"]["alternatives"][0]["message"]["text"]
            except Exception as e:
                error_message = f"Ошибка в aiohttp.ClientSession(): {e}"
                logger.error(error_message)
    except Exception as e:
        error_message = f"Ошибка в ask_gpt: {e}"
        logger.error(error_message)
        
