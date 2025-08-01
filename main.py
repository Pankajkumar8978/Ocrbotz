import telebot
from telebot import types
import requests
import os

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER = os.getenv("OWNER")
bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

def send_typing_action(chat_id):
    bot.send_chat_action(chat_id, 'typing')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_typing_action(message.chat.id)
    first = message.chat.first_name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Owner 👨‍💻", url=f"https://t.me/{OWNER}"))
    keyboard.add(types.InlineKeyboardButton("Tutorial 📺", url="https://youtu.be/7yqjm-DCaXE"))
    bot.reply_to(
        message,
        f'Hi! {first}\n\nWelcome to OCR Bot.\n\nJust send a clear image to me and I will recognize the text in the image and send it as a message!\n\nCheck /help for more...\n\nCreate your Own Bot by Watching Tutorial',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    send_typing_action(message.chat.id)
    first = message.chat.first_name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Owner 👨‍💻", url=f"https://t.me/{OWNER}"))
    keyboard.add(types.InlineKeyboardButton("Tutorial 📺", url="https://youtu.be/@sitesadda"))
    bot.reply_to(
        message,
        f'Hi! {first}\n\nFollow these steps...\n➥ First send me a clear image\n➥ Select the language to extract text\n➥ Extracted text will be sent as a message!',
        reply_markup=keyboard
    )

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    send_typing_action(message.chat.id)
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    user_data[message.chat.id] = file_url

    keyboard = types.InlineKeyboardMarkup()
    languages = [
        ("Arabic", 'ara'), ("Bulgarian", 'bul'), ("Chinese", 'chs'),
        ("Croatian", 'hrv'), ("Danish", 'dan'), ("Dutch", 'dut'),
        ("English", 'eng'), ("Finnish", 'fin'), ("French", 'fre'),
        ("German", 'ger'), ("Greek", 'gre'), ("Hungarian", 'hun'),
        ("Korean", 'kor'), ("Italian", 'ita'), ("Japanese", 'jpn'),
        ("Polish", 'pol'), ("Portuguese", 'por'), ("Russian", 'rus'),
        ("Spanish", 'spa'), ("Swedish", 'swe'), ("Turkish", 'tur')
    ]
    for lang_name, lang_code in languages:
        keyboard.add(types.InlineKeyboardButton(lang_name, callback_data=lang_code))

    bot.reply_to(message, "Select the language here 👇", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    send_typing_action(call.message.chat.id)
    file_url = user_data.get(call.message.chat.id)

    if not file_url:
        bot.answer_callback_query(call.id, "Error: File URL not found.")
        return

    query_lang = call.data
    response = requests.get(
        f"https://api.ocr.space/parse/imageurl?apikey={API_KEY}&url={file_url}&language={query_lang}&detectOrientation=True&filetype=JPG&OCREngine=1&isTable=True&scale=True"
    )
    data = response.json()

    if not data['IsErroredOnProcessing']:
        message = data['ParsedResults'][0]['ParsedText']
        bot.edit_message_text(message, chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.edit_message_text("⚠️ Something went wrong", chat_id=call.message.chat.id, message_id=call.message.message_id)

bot.polling()
