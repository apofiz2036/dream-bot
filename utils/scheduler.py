import sqlite3
import logging
from datetime import datetime
from pytz import timezone
from config import SQLITE_DB

logger = logging.getLogger(__name__)

def reset_daily_limits():
    """Обновляет лимиты всех пользователей до 10, если они меньше 10."""
    try:
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscribers
            SET limits = 10
            WHERE limits < 10
        """)

        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка в reset_daily_limits: {e}")