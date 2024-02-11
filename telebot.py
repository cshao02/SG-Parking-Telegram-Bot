import os

import telebot

import requests

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hi, how may I assist you today?\n\n/avail to see slots for all carparks\n/carpark and input carpark number to see slots for specific carpark\n\nFormat is as follows:\ncarpark number : number of available slots / total number of slots")

@bot.message_handler(commands=['avail'])
def get_avail(message):
    current_date_and_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    url = 'https://api.data.gov.sg/v1/transport/carpark-availability'
    response = requests.get(url, {"date_time": current_date_and_time})

    data = response.json()["items"][0]["carpark_data"]

    string = ""

    for line in data:
        string = string + line["carpark_number"] + ": " + line["carpark_info"][0]["lots_available"] + "/" + line["carpark_info"][0]["total_lots"] + "\n"

    if len(string) > 4095:
        for x in range(0, len(string), 4095):
            bot.reply_to(message, text=string[x:x + 4095])
    else:
        bot.reply_to(message, text=string)

@bot.message_handler(commands=['carpark'])
def sign_handler(message):
    text = "What carpark number can I check for you?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)

def day_handler(message):
    carpark = get_carpark(message.text)
    bot.send_message(message.chat.id, carpark, parse_mode="Markdown")

def get_carpark(input):
    current_date_and_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    url = 'https://api.data.gov.sg/v1/transport/carpark-availability'
    response = requests.get(url, {"date_time": current_date_and_time})

    data = response.json()["items"][0]["carpark_data"]

    for line in data:
        if input.upper() == line["carpark_number"]:
            return line["carpark_number"] + ": " + line["carpark_info"][0]["lots_available"] + "/" + line["carpark_info"][0]["total_lots"] + " " + line["update_datetime"]

    return "Invalid carpark number"

bot.infinity_polling()
