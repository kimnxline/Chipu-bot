#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CHIP-U Investment Bot

import logging
import json
import os
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== KONFIGURATSIYA ====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Muhit o'zgaruvchilari orqali maxfiy ma'lumotlarni olish
BOT_TOKEN = os.getenv(7955603188:AAEMhEEK2CblnKuQRwDLhdOqSKx1FzvILXc)  # Telegram bot token
ADMIN_ID = int(os.getenv("964318020", "0"))  # Admin ID yoki 0
USDT_ADDRESS = os.getenv("TNjvqz6Trm9ZGQ6nyPE1eB5wVewmKUQVQh", "TRC20")  # Default USDT manzil
DATA_FILE = "chipu_data.json"

# Paketlar
PACKAGES = {
    "celeron": {"name": "Celeron", "price": 12, "days": 20, "total": 19.20, "daily": 0.96},
    "pentium": {"name": "Pentium", "price": 21, "days": 25, "total": 33.60, "daily": 1.344},
    "ryzen3": {"name": "Ryzen 3", "price": 29, "days": 30, "total": 43.50, "daily": 1.45},
    "corei5": {"name": "Core i5", "price": 37, "days": 35, "total": 55.50, "daily": 1.586},
    "ryzen7": {"name": "Ryzen 7", "price": 45, "days": 40, "total": 63.00, "daily": 1.575},
    "corei9": {"name": "Core i9", "price": 69, "days": 45, "total": 95.22, "daily": 2.116}
}

# ==================== DATA MANAGEMENT ====================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_data()
    return default_data()

def default_data():
    return {
        "users": {},
        "pending_payments": {},
        "pending_withdrawals": {},
        "usdt_address": USDT_ADDRESS,
        "payment_counter": 1000,
        "withdrawal_counter": 2000
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

def get_user(user_id):
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "id": user_id,
            "balance": 0.0,
            "package": None,
            "package_start": None,
            "package_end": None,
            "daily_profit": 0.0,
            "total_earned": 0.0,
            "referrer": None,
            "referrals": [],
            "ref_earnings": 0.0,
            "history": [],
            "last_profit_day": None
        }
        save_data(data)
    return data["users"][uid]

def is_withdrawal_time():
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    return 12 <= now.hour < 17

def main_keyboard(is_admin=False):
    buttons = [
        [KeyboardButton("💼 Paketlar"), KeyboardButton("👤 Profil")],
        [KeyboardButton("💰 Balans"), KeyboardButton("📊 Tarix")],
        [KeyboardButton("👥 Referal"), KeyboardButton("💸 Pul yechish")],
        [KeyboardButton("ℹ️ Ma’lumot"), KeyboardButton("📞 Yordam")]
    ]
    if is_admin:
        buttons.append([KeyboardButton("⚙️ Admin Panel")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ==================== START ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    # Referal
    if context.args and not user["referrer"]:
        try:
            ref_id = int(context.args[0])
            if ref_id != update.effective_user.id and str(ref_id) in data["users"]:
                user["referrer"] = ref_id
                data["users"][str(ref_id)]["referrals"].append(update.effective_user.id)
                save_data(data)
        except ValueError:
            pass

    is_admin = update.effective_user.id == ADMIN_ID

    await update.message.reply_text(
        f"Assalomu alaykum, {update.effective_user.first_name}!\n\n"
        "🔷 CHIP-U Investment Platform ga xush kelibsiz!\n\n"
        "💼 Aksiyalar bozoriga investitsiya qiling va kunlik daromad oling.\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=main_keyboard(is_admin=is_admin)
    )

# ==================== BOTNI ISHGA TUSHIRISH ====================

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    # Qo'shimcha handlerlarni bu yerga qo'shishingiz mumkin

    application.run_polling()

if __name__ == "__main__":
    main()
