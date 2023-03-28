from yeelight import Bulb
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

import socketserver

bulb_ip = '...'
bulb = Bulb(bulb_ip)
bot = TeleBot('...')
white_list = {'...'}


def create_main_keyboard_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    color_button = KeyboardButton('Color')
    bright_button = KeyboardButton('Bright')
    temperature_button = KeyboardButton('Temperature')
    power_button = KeyboardButton('Power')
    markup.row(color_button, temperature_button)
    markup.row(bright_button, power_button)
    return markup


def create_bright_keyboard_markup():
    markup = ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)
    button_1 = KeyboardButton('0')
    button_2 = KeyboardButton('20')
    button_3 = KeyboardButton('50')
    button_4 = KeyboardButton('80')
    button_5 = KeyboardButton('100')
    markup.row(button_1, button_2, button_3, button_4, button_5)
    return markup


def create_color_keyboard_markup():
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    button_1 = KeyboardButton('🔴')
    button_2 = KeyboardButton('🔵')
    button_3 = KeyboardButton('🟢')
    markup.row(button_1, button_2, button_3)
    return markup


def create_power_keyboard_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_1 = KeyboardButton('On')
    button_2 = KeyboardButton('Off')
    markup.row(button_1, button_2)
    return markup


def create_temperature_keyboard_markup():
    markup = ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    button_1 = KeyboardButton('Свет свечи') # 1600
    button_2 = KeyboardButton('Рассвет/Закат') # 3000
    button_3 = KeyboardButton('Свет луны') #4000
    button_4 = KeyboardButton('Дневной свет') #5200
    button_5 = KeyboardButton('Облачное небо') #6000
    button_6 = KeyboardButton('Пасмурно') # 6600
    markup.row(button_1, button_2, button_3)
    markup.row(button_4, button_5, button_6)
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if (message.from_user.id != 313819897):
        reply = bot.reply_to(message, f"Not safe")
        bot.register_next_step_handler(reply, loop)
    else:
        bot.reply_to(message, "I am bulb controller bot!", reply_markup=create_main_keyboard_markup())


def loop(message):
    reply = bot.reply_to(message, f"Not safe")
    bot.register_next_step_handler(reply, loop)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == 'Bright':
        reply = bot.reply_to(message, f"Set bright",
                             reply_markup=create_bright_keyboard_markup())
        bot.register_next_step_handler(reply, bright_menu_handler)
    elif message.text == 'Color':
        reply = bot.reply_to(message, f"Set color",
                             reply_markup=create_color_keyboard_markup())
        bot.register_next_step_handler(reply, color_menu_handler)
    elif message.text == 'Temperature':
        reply = bot.reply_to(message, f"Set color",
                             reply_markup=create_temperature_keyboard_markup())
        bot.register_next_step_handler(reply, temperature_menu_handler)
    elif message.text == 'Power':
        reply = bot.reply_to(message, f"Set power",
                             reply_markup=create_power_keyboard_markup())
        bot.register_next_step_handler(reply, power_menu_handler)
    else:
        bot.reply_to(message, "Main menu", reply_markup=create_main_keyboard_markup())


def color_menu_handler(message):
    if message.text == '🔴':
        bulb.set_rgb(255, 0, 0)
    if message.text == '🟢':
        bulb.set_rgb(0, 255, 0)
    if message.text == '🔵':
        bulb.set_rgb(0, 0, 255)

    bot.reply_to(message, "Main menu",
                 reply_markup=create_main_keyboard_markup())


def temperature_menu_handler(message):
    value = 5400

    if message.text == 'Свет свечи':
        value = 1600
    elif message.text == 'Рассвет/Закат':
        value = 3000
    elif message.text == 'Свет луны':
        value = 4000
    elif message.text == 'Дневной свет':
        value = 5400
    elif message.text == 'Облачное небо':
        value = 6000
    elif message.text == 'Пасмурно':
        value = 6600
    elif message.text.isdigit():
        value = int(message.text)

    bulb.set_color_temp(value)
    bot.reply_to(message, "Main menu",
                 reply_markup=create_main_keyboard_markup())


def power_menu_handler(message):
    if message.text == 'On':
        bulb.turn_on()
    elif message.text == 'Off':
        bulb.turn_off()

    bot.reply_to(message, "Main menu",
                 reply_markup=create_main_keyboard_markup())


def bright_menu_handler(message):
    if message.text.isdigit():
        bulb.set_brightness(brightness=int(message.text))

    bot.reply_to(message, "Main menu",
                 reply_markup=create_main_keyboard_markup())


bot.infinity_polling()


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


HOST, PORT = "localhost", 9999

# Create the server, binding to localhost on port 9999
with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
