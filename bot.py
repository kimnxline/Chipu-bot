#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import logging
import json
import os
from datetime import datetime, timedelta, time
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
format=’%(asctime)s - %(name)s - %(levelname)s - %(message)s’,
level=logging.INFO
)
logger = logging.getLogger(**name**)

BOT_TOKEN = “7955603188:AAEMhEEK2CblnKuQRwDLhdOqSKx1FzvILXc”
ADMIN_ID = 964318020
USDT_ADDRESS = “TNjvqz6Trm9ZGQ6nyPE1eB5wVewmKUQVQh”
DATA_FILE = “chipu_data.json”

PACKAGES = {
“celeron”: {“name”: “Celeron”, “price”: 12, “days”: 20, “total”: 19.20, “daily”: 0.96},
“pentium”: {“name”: “Pentium”, “price”: 21, “days”: 25, “total”: 33.60, “daily”: 1.344},
“ryzen3”: {“name”: “Ryzen 3”, “price”: 29, “days”: 30, “total”: 43.50, “daily”: 1.45},
“corei5”: {“name”: “Core i5”, “price”: 37, “days”: 35, “total”: 55.50, “daily”: 1.586},
“ryzen7”: {“name”: “Ryzen 7”, “price”: 45, “days”: 40, “total”: 63.00, “daily”: 1.575},
“corei9”: {“name”: “Core i9”, “price”: 69, “days”: 45, “total”: 95.22, “daily”: 2.116}
}

def load_data():
if os.path.exists(DATA_FILE):
with open(DATA_FILE, ‘r’, encoding=‘utf-8’) as f:
try:
return json.load(f)
except:
return default_data()
return default_data()

def default_data():
return {
“users”: {},
“pending_payments”: {},
“pending_withdrawals”: {},
“usdt_address”: USDT_ADDRESS,
“payment_counter”: 1000,
“withdrawal_counter”: 2000
}

def save_data(data):
with open(DATA_FILE, ‘w’, encoding=‘utf-8’) as f:
json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

def get_user(user_id):
uid = str(user_id)
if uid not in data[“users”]:
data[“users”][uid] = {
“id”: user_id,
“balance”: 0.0,
“package”: None,
“package_start”: None,
“package_end”: None,
“daily_profit”: 0.0,
“total_earned”: 0.0,
“referrer”: None,
“referrals”: [],
“ref_earnings”: 0.0,
“history”: [],
“last_profit_day”: None
}
save_data(data)
return data[“users”][uid]

def is_withdrawal_time():
tz = pytz.timezone(‘Asia/Tashkent’)
now = datetime.now(tz)
return 12 <= now.hour < 17

def main_keyboard(is_admin=False):
buttons = [
[KeyboardButton(“Paketlar”), KeyboardButton(“Profil”)],
[KeyboardButton(“Balans”), KeyboardButton(“Tarix”)],
[KeyboardButton(“Referal”), KeyboardButton(“Pul yechish”)],
[KeyboardButton(“Malumot”), KeyboardButton(“Yordam”)]
]
if is_admin:
buttons.append([KeyboardButton(“Admin Panel”)])
return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = get_user(update.effective_user.id)

```
if context.args and not user["referrer"]:
    try:
        ref_id = int(context.args[0])
        if ref_id != update.effective_user.id and str(ref_id) in data["users"]:
            user["referrer"] = ref_id
            data["users"][str(ref_id)]["referrals"].append(update.effective_user.id)
            save_data(data)
    except:
        pass

is_admin = update.effective_user.id == ADMIN_ID

await update.message.reply_text(
    f"Assalomu alaykum, {update.effective_user.first_name}!\n\n"
    "CHIP-U Investment Platform ga xush kelibsiz!\n\n"
    "Aksiyalar bozoriga investitsiya qiling va kunlik daromad oling.\n\n"
    "Quyidagi tugmalardan birini tanlang:",
    reply_markup=main_keyboard(is_admin=is_admin)
)
```

async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = get_user(update.effective_user.id)

```
if user["package"]:
    pkg = PACKAGES[user["package"]]
    await update.message.reply_text(
        f"Sizda faol paket bor!\n\n"
        f"Paket: {pkg['name']}\n"
        f"Kunlik: ${user['daily_profit']:.3f}\n"
        f"Tugash: {user['package_end']}"
    )
    return

text = "CHIP-U PAKETLARI\n\n"
for key, pkg in PACKAGES.items():
    profit = pkg["total"] - pkg["price"]
    text += f"{pkg['name']}\n"
    text += f"Depozit: ${pkg['price']}\n"
    text += f"Umumiy: ${pkg['total']}\n"
    text += f"Foyda: ${profit:.2f}\n"
    text += f"Kunlik: ${pkg['daily']:.3f}\n"
    text += f"Muddat: {pkg['days']} kun\n\n"

keyboard = []
for key, pkg in PACKAGES.items():
    keyboard.append([InlineKeyboardButton(
        f"{pkg['name']} - ${pkg['price']}", 
        callback_data=f"buy_{key}"
    )])

await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
```

async def buy_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
user = get_user(query.from_user.id)

if user["package"]:
    await query.edit_message_text("Sizda faol paket bor!")
    return

package_key = query.data.replace("buy_", "")
if package_key not in PACKAGES:
    await query.edit_message_text("Paket topilmadi!")
    return

pkg = PACKAGES[package_key]

data["payment_counter"] += 1
payment_id = f"CHIP{data['payment_counter']}"
save_data(data)

data["pending_payments"][payment_id] = {
    "user_id": query.from_user.id,
    "username": query.from_user.username or "none",
    "first_name": query.from_user.first_name,
    "package": package_key,
    "amount": pkg["price"],
    "timestamp": datetime.now().isoformat()
}
save_data(data)

await query.edit_message_text(
    f"{pkg['name']} PAKETI\n\n"
    f"Depozit: ${pkg['price']}\n"
    f"Umumiy: ${pkg['total']}\n"
    f"Kunlik: ${pkg['daily']:.3f}\n"
    f"Muddat: {pkg['days']} kun\n\n"
    f"Tolov ID: {payment_id}\n\n"
    f"USDT (TRC-20):\n"
    f"{data['usdt_address']}\n\n"
    f"KORSATMA:\n"
    f"1. Aynan ${pkg['price']} USDT yuboring\n"
    f"2. Chekni screenshot qiling\n"
    f"3. Screenshot'da ID: {payment_id}\n"
    f"4. Botga yuboring"
)
```

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not update.message.photo:
return

```
user = get_user(update.effective_user.id)

payment_id = None
for pid, pdata in data["pending_payments"].items():
    if pdata["user_id"] == update.effective_user.id and "screenshot" not in pdata:
        payment_id = pid
        break

if not payment_id:
    return

data["pending_payments"][payment_id]["screenshot"] = update.message.photo[-1].file_id
data["pending_payments"][payment_id]["caption"] = update.message.caption or ""
save_data(data)

pkg = PACKAGES[data["pending_payments"][payment_id]["package"]]

keyboard = [[
    InlineKeyboardButton("Tasdiqlash", callback_data=f"approve_{payment_id}"),
    InlineKeyboardButton("Rad etish", callback_data=f"reject_{payment_id}")
]]

await context.bot.send_photo(
    chat_id=ADMIN_ID,
    photo=update.message.photo[-1].file_id,
    caption=f"TOLOV\n\n"
            f"User: {data['pending_payments'][payment_id]['first_name']}\n"
            f"Username: @{data['pending_payments'][payment_id]['username']}\n"
            f"ID: {update.effective_user.id}\n"
            f"Paket: {pkg['name']}\n"
            f"Summa: ${pkg['price']}\n"
            f"ID: {payment_id}",
    reply_markup=InlineKeyboardMarkup(keyboard)
)

await update.message.reply_text("Screenshot yuborildi! Admin tekshiradi.")
```

async def approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
if query.from_user.id != ADMIN_ID:
    return

payment_id = query.data.replace("approve_", "")

if payment_id not in data["pending_payments"]:
    await query.edit_message_caption(caption="Tolov topilmadi!")
    return

payment = data["pending_payments"][payment_id]
user = get_user(payment["user_id"])
package_key = payment["package"]
pkg = PACKAGES[package_key]

tz = pytz.timezone('Asia/Tashkent')
start_date = datetime.now(tz)
end_date = start_date + timedelta(days=pkg["days"])

user["package"] = package_key
user["package_start"] = start_date.isoformat()
user["package_end"] = end_date.strftime("%Y-%m-%d")
user["daily_profit"] = pkg["daily"]
user["last_profit_day"] = start_date.strftime("%Y-%m-%d")
user["history"].append({
    "type": "investment",
    "package": pkg["name"],
    "amount": pkg["price"],
    "date": start_date.isoformat()
})

if user["referrer"]:
    ref_user = get_user(user["referrer"])
    bonus = round(pkg["price"] * 0.10, 2)
    ref_user["balance"] += bonus
    ref_user["ref_earnings"] += bonus
    ref_user["history"].append({
        "type": "referral",
        "level": "A",
        "amount": bonus,
        "date": datetime.now(tz).isoformat()
    })
    
    try:
        await context.bot.send_message(
            chat_id=user["referrer"],
            text=f"Referal bonus!\n\n+${bonus}\nBalans: ${ref_user['balance']:.2f}"
        )
    except:
        pass
    
    if ref_user["referrer"]:
        ref2_user = get_user(ref_user["referrer"])
        bonus2 = round(pkg["price"] * 0.03, 2)
        ref2_user["balance"] += bonus2
        ref2_user["ref_earnings"] += bonus2
        ref2_user["history"].append({
            "type": "referral",
            "level": "B",
            "amount": bonus2,
            "date": datetime.now(tz).isoformat()
        })
        
        try:
            await context.bot.send_message(
                chat_id=ref_user["referrer"],
                text=f"Referal bonus!\n\n+${bonus2}\nBalans: ${ref2_user['balance']:.2f}"
            )
        except:
            pass

del data["pending_payments"][payment_id]
save_data(data)

await query.edit_message_caption(caption=query.message.caption + "\n\nTASDIQLANDI!")

await context.bot.send_message(
    chat_id=payment["user_id"],
    text=f"TABRIKLAYMIZ!\n\n"
         f"Tolov tasdiqlandi!\n\n"
         f"Paket: {pkg['name']}\n"
         f"Summa: ${pkg['price']}\n"
         f"Kunlik: ${user['daily_profit']:.3f}\n"
         f"Muddat: {pkg['days']} kun\n"
         f"Tugash: {user['package_end']}\n\n"
         f"Har kuni 14:00 da tolov!"
)
```

async def reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
if query.from_user.id != ADMIN_ID:
    return

payment_id = query.data.replace("reject_", "")

if payment_id not in data["pending_payments"]:
    await query.edit_message_caption(caption="Topilmadi!")
    return

payment = data["pending_payments"][payment_id]
pkg = PACKAGES[payment["package"]]

await query.edit_message_caption(caption=query.message.caption + "\n\nRAD ETILDI!")

await context.bot.send_message(
    chat_id=payment["user_id"],
    text=f"Tolov rad etildi!\n\nPaket: {pkg['name']}\nQayta urinib koring."
)

del data["pending_payments"][payment_id]
save_data(data)
```

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = get_user(update.effective_user.id)

```
text = f"PROFIL\n\n"
text += f"ID: {user['id']}\n"
text += f"Balans: ${user['balance']:.2f}\n"
text += f"Jami: ${user['total_earned']:.2f}\n"
text += f"Referal: ${user['ref_earnings']:.2f}\n\n"

if user["package"]:
    pkg = PACKAGES[user["package"]]
    text += f"Paket: {pkg['name']}\n"
    text += f"Kunlik: ${user['daily_profit']:.3f}\n"
    text += f"Tugash: {user['package_end']}\n"
else:
    text += f"Faol paket yoq"

await update.message.reply_text(text)
```

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = get_user(update.effective_user.id)

```
text = f"BALANS\n\n"
text += f"${user['balance']:.2f}\n"
text += f"Jami: ${user['total_earned']:.2f}\n"
text += f"Referal: ${user['ref_earnings']:.2f}\n\n"

if user["balance"] >= 3:
    text += f"Yechish mumkin!\n12:00-17:00"
else:
    text += f"Minimal: $3"

await update.message.reply_text(text)
```

async def withdraw_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = get_user(update.effective_user.id)

```
if user["balance"] < 3:
    await update.message.reply_text(f"Minimal: $3\nSizda: ${user['balance']:.2f}")
    return

tz = pytz.timezone('Asia/Tashkent')
now = datetime.now(tz)
if not (12 <= now.hour < 17):
    await update.message.reply_text(
        f"Yechish faqat 12:00-17:00!\nHozir: {now.strftime('%H:%M')}"
    )
    return

commission = round(user["balance"] * 0.14, 2)
final = round(user["balance"] - commission, 2)

await update.message.reply_text(
    f"PUL YECHISH\n\n"
    f"Balans: ${user['balance']:.2f}\n"
    f"Komissia: ${commission}\n"
    f"Olasiz: ${final}\n\n"
    f"USDT manzilini yuboring:"
)

context.user_data["withdraw_pending"] = True
```

async def process_withdraw_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.user_data.get(“withdraw_pending”):
return

```
if update.message.photo:
    return

user = get_user(update.effective_user.id)
address = update.message.text.strip()

if len(address) < 20 or not address.startswith('T'):
    await update.message.reply_text("Notogri USDT manzil!")
    return

commission = round(user["balance"] * 0.14, 2)
final = round(user["balance"] - commission, 2)

data["withdrawal_counter"] += 1
withdrawal_id = f"WD{data['withdrawal_counter']}"

data["pending_withdrawals"][withdrawal_id] = {
    "user_id": update.effective_user.id,
    "username": update.effective_user.username or "none",
    "first_name": update.effective_user.first_name,
    "balance": user["balance"],
    "commission": commission,
    "final_amount": final,
    "address": address,
    "timestamp": datetime.now().isoformat()
}
save_data(data)

context.user_data["withdraw_pending"] = False

keyboard = [[
    InlineKeyboardButton("Tolandi", callback_data=f"wd_approve_{withdrawal_id}"),
    InlineKeyboardButton("Bekor", callback_data=f"wd_reject_{withdrawal_id}")
]]

await context.bot.send_message(
    chat_id=ADMIN_ID,
    text=f"YECHISH\n\n"
         f"User: {data['pending_withdrawals'][withdrawal_id]['first_name']}\n"
         f"Username: @{data['pending_withdrawals'][withdrawal_id]['username']}\n"
         f"ID: {update.effective_user.id}\n"
         f"Balans: ${user['balance']:.2f}\n"
         f"Komissia: ${commission}\n"
         f"Final: ${final}\n"
         f"Manzil: {address}\n"
         f"ID: {withdrawal_id}",
    reply_markup=InlineKeyboardMarkup(keyboard)
)

await update.message.reply_text(f"Sorov yuborildi!\n${final}\nAdmin tekshiradi.")
```

async def approve_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
if query.from_user.id != ADMIN_ID:
    return

withdrawal_id = query.data.replace("wd_approve_", "")

if withdrawal_id not in data["pending_withdrawals"]:
    await query.edit_message_text("Topilmadi!")
    return

wd = data["pending_withdrawals"][withdrawal_id]
user = get_user(wd["user_id"])

user["balance"] = 0
user["history"].append({
    "type": "withdrawal",
    "amount": wd["final_amount"],
    "date": datetime.now().isoformat()
})

del data["pending_withdrawals"][withdrawal_id]
save_data(data)

await query.edit_message_text(query.message.text + "\n\nTOLANDI!")

await context.bot.send_message(
    chat_id=wd["user_id"],
    text=f"PULINGIZ YUBORILDI!\n\n${wd['final_amount']}\nTez orada tushadi!"
)
```

async def reject_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
if query.from_user.id != ADMIN_ID:
    return

withdrawal_id = query.data.replace("wd_reject_", "")

if withdrawal_id not in data["pending_withdrawals"]:
    await query.edit_message_text("Topilmadi!")
    return

wd = data["pending_withdrawals"][withdrawal_id]

await query.edit_message_text(query.message.text + "\n\nBEKOR!")

await context.bot.send_message(
    chat_id=wd["user_id"],
    text="Yechish rad etildi."
)

del data["pending_withdrawals"][withdrawal_id]
save_data(data)
```

async def show_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = get_user(update.effective_user.id)
bot_username = (await context.bot.get_me()).username
ref_link = f”https://t.me/{bot_username}?start={user[‘id’]}”

```
text = f"REFERAL\n\n"
text += f"Link:\n{ref_link}\n\n"
text += f"A-daraja: 10%\n"
text += f"B-daraja: 3%\n\n"
text += f"Referallar: {len(user['referrals'])}\n"
text += f"Daromad: ${user['ref_earnings']:.2f}"

await update.message.reply_text(text)
```

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = get_user(update.effective_user.id)

```
if not user["history"]:
    await update.message.reply_text("Tarix bosh")
    return

text = "TARIX\n\n"

for h in reversed(user["history"][-15:]):
    date = h["date"][:10]
    
    if h["type"] == "investment":
        text += f"{date}: {h['package']} - ${h['amount']}\n"
    elif h["type"] == "daily_profit":
        text += f"{date}: +${h['amount']:.3f}\n"
    elif h["type"] == "referral":
        text += f"{date}: Referal ({h['level']}) +${h['amount']}\n"
    elif h["type"] == "withdrawal":
        text += f"{date}: -${h['amount']:.2f}\n"

await update.message.reply_text(text)
```

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = “”“CHIP-U Investment

Aksiyalar bozoriga investitsiya qiling va kunlik daromad oling.

QANDAY ISHLAYDI?

- Paket tanlang
- USDT tolang
- Kunlik tolov oling

AFZALLIKLAR:

- Kunlik avtomatik tolov
- 1.38x - 1.6x daromad
- Referal: 10% + 3%
- 20-45 kun muddat

Xavfsiz. Foydali.”””

```
await update.message.reply_text(text)
```

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = “”“YORDAM

Admin: @admin
Email: support@chipu.com

Ish vaqti: 09:00-22:00”””

```
await update.message.reply_text(text)
```

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.effective_user.id != ADMIN_ID:
return

```
total = len(data["users"])
active = sum(1 for u in data["users"].values() if u["package"])
balance = sum(u["balance"] for u in data["users"].values())

text = f"ADMIN\n\n"
text += f"Userlar: {total}\n"
text += f"Faol: {active}\n"
text += f"Balans: ${balance:.2f}\n"
text += f"Tolovlar: {len(data['pending_payments'])}\n"
text += f"Yechishlar: {len(data['pending_withdrawals'])}\n\n"
text += f"Komandalar:\n"
text += f"/balance [id] [sum]\n"
text += f"/activate [id] [paket]"

await update.message.reply_text(text)
```

async def admin_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.effective_user.id != ADMIN_ID:
return

```
if len(context.args) != 2:
    await update.message.reply_text("Format: /balance [id] [sum]")
    return

try:
    user_id = str(int(context.args[0]))
    amount = float(context.args[1])
except:
    await update.message.reply_text("Xato format!")
    return

if user_id not in data["users"]:
    await update.message.reply_text("User topilmadi!")
    return

data["users"][user_id]["balance"] += amount
data["users"][user_id]["balance"] = max(0, data["users"][user_id]["balance"])
save_data(data)

await update.message.reply_text(f"Balans ozgartirildi!")
```

async def admin_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.effective_user.id != ADMIN_ID:
return

```
if len(context.args) != 2:
    await update.message.reply_text("Format: /activate [id] [paket]")
    return

try:
    user_id = str(int(context.args[0]))
    package_key = context.args[1].lower()
except:
    await update.message.reply_text("Xato format!")
    return

if user_id not in data["users"]:
    await update.message.reply_text("User topilmadi!")
    return

if package_key not in PACKAGES:
    await update.message.reply_text("Paket topilmadi!")
    return

user = data["users"][user_id]
pkg = PACKAGES[package_key]

tz = pytz.timezone('Asia/Tashkent')
start_date = datetime.now(tz)
end_date = start_date + timedelta(days=pkg["days"])

user["package"] = package_key
user["package_start"] = start_date.isoformat()
user["package_end"] = end_date.strftime("%Y-%m-%d")
user["daily_profit"] = pkg["daily"]
user["last_profit_day"] = start_date.strftime("%Y-%m-%d")
save_data(data)

await update.message.reply_text("Paket yoqildi!")
```

async def daily_profit_job(context: ContextTypes.DEFAULT_TYPE):
tz = pytz.timezone(‘Asia/Tashkent’)
today = datetime.now(tz).strftime(”%Y-%m-%d”)

```
for user_id, user in data["users"].items():
    if not user["package"]:
        continue
    
    if user.get("last_profit_day") == today:
        continue
    
    if user["package_end"] < today:
        user["package"] = None
        user["package_start"] = None
        user["package_end"] = None
        user["daily_profit"] = 0.0
        save_data(data)
        
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"Paketingiz tugadi!\n\nBalans: ${user['balance']:.2f}\n\nYangi paket sotib olishingiz mumkin!"
            )
        except:
            pass
        continue
```
