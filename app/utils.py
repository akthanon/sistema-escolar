import hmac
import hashlib
from datetime import datetime
import os
from zoneinfo import ZoneInfo

SECRET_KEY = os.environ.get('TOKEN_SECRET', 'my-secret-key-for-token')
TIMEZONE = ZoneInfo("America/Mazatlan")  # Cambia según tu zona

def get_current_hour_slot():
    now = datetime.now(TIMEZONE)
    hour = now.hour
    return f"{hour:02d}-{hour+1:02d}"

def get_current_date():
    return datetime.now(TIMEZONE).date()

def generate_token(slot):
    date_str = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    message = f"{date_str}-{slot}"
    h = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256)
    return h.hexdigest()

def verify_token(token, slot):
    expected = generate_token(slot)
    return hmac.compare_digest(token, expected)
