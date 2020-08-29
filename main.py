from CoreFuncs.funcs import *

listener = Listener()
RAM = Myjson('res/properties.json')
bot = telebot.TeleBot('1152150629:AAGcrvSKMQ6OhZRrXXtGywrpLGKHD0v9qNc')


def makeMenu(call, header, keyboard, string='default'):
    try:
        if (string == 'default'):
            Text = header
        else:
            Text = string + '\n\n' + header

        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=Text,
                              message_id=call.message.message_id,
                              reply_markup=keyboard,
                              parse_mode='HTML')
    except ApiException as e:
        print(e.args)

    except:
        traceback.print_exc()
        pass

class Keyborad_Switcher:
    '''
        [kb_name, Admin_func(opt)... ]
    '''
    __slots__ = ['call', 'chat_id']

    def __init__(self, call):
        self.call = call
        self.chat_id = str(call.from_user.id)
        # Menu inside menu
        if simplify(call)[0] == 'Dummy_Button':
            return
        method_name = simplify(call)[1]
        method = eval(f'Admin_{method_name}')
        method(call)


class Admin_Settings:

    __slots__ = ['call', 'chat_id', 'method_name', 'identifier', 'sign', 'user_link']

    def __init__(self, call):
        self.call = call
        self.chat_id = str(call.from_user.id)

        self.method_name = simplify(call)[2]
        try:
            self.identifier = simplify(call)[3]
            self.sign = simplify(call)[4]
        except:
            pass
        method = getattr(self, self.method_name, lambda: 'Invalid')
        method()

    @staticmethod
    def Header():
        text = f"SmartBrick"
        return text

    @staticmethod
    def Keyboard():
        markup = types.InlineKeyboardMarkup()
        V, X = '✅', '☑️'
        # Status
        data = RAM.get()
        Statusbtn = btn('Status', Dummy=True)
        Status = btn(V, ['Admin', 'Settings', 'update', 'Status', '0']) if data['Status'] == 1 \
            else btn(X, ['Admin', 'Settings', 'update', 'Status', '1'])
        markup.add(Statusbtn, Status)

        # Servo PWM

        markup.add(btn('Servo PWM', Dummy=True) , btn(str(data['Current_PWM']), Dummy=True))
        markup.add(btn('⬇️ Change PWM ⬇️', Dummy=True))
        for operator in ['+', '-']:
            val = 1
            markup.add(btn(operator + str(val), ['Admin', 'Settings', 'PWM', operator, val]),
                       btn(operator + str(val * 10), ['Admin', 'Settings', 'PWM', operator, val * 10]),
                       btn(operator + str(val * 100), ['Admin', 'Settings', 'PWM', operator, val * 100]))

        return markup

    def update(self):
        RAM.set(self.identifier, int(self.sign))
        listener.stop_sign = False if self.sign == "1" else True

        return makeMenu(self.call, self.Header(), self.Keyboard())

    def PWM(self):
        temp = RAM.get('Current_PWM')
        temp = int(temp) + int(self.sign) if self.identifier == '+' else int(temp) - int(self.sign)
        min_post_time = RAM.get('Min_Post_Time')
        temp = min_post_time if temp < min_post_time else temp
        RAM.set('Current_PWM', temp)
        return makeMenu(self.call, self.Header(), self.Keyboard())

    def AddGroup(self):
        msg = bot.send_message(self.chat_id, 'Enter Group User-name, whether with @ or with t.me/')
        bot.register_next_step_handler(msg, self.process_add_group)

    def process_add_group(self, group):
        group = group.text
        if 't.me' in group:
            group = f"@{group.split('t.me/')[-1]}"
        elif '@' not in group:
            group = f'@{group}'

        RAM.add_to_list('Groups', group)

    def RemoveGroup(self):
        msg = bot.send_message(self.chat_id, 'הכנס שם קבוצה כולל @')
        bot.register_next_step_handler(msg, self.process_remove_group)

    def process_remove_group(self, group):
        RAM.remove_from_list('Groups', group.html_text)

    def AddUser(self):
        msg = bot.send_message(self.chat_id, 'Enter User name, whether with @ or with t.me/')
        bot.register_next_step_handler(msg, self.process_add_user)

class Bot_Handlers:
    __slots__ = []
    @staticmethod
    @bot.message_handler(commands=['start'])
    def handle_command_on(message):
        chat_id = str(message.chat.id)
        bot.send_message(chat_id, Admin_Settings.Header(), reply_markup=Admin_Settings.Keyboard())

    @staticmethod
    @bot.callback_query_handler(func=lambda call: True)
    def handle_all_button_clicks(call):
        chat_id = str(call.from_user.id)
        try:
                Keyborad_Switcher(call)
        except:
            traceback.print_exc()
            print('chat id -', chat_id, 'in Menu -', simplify(call)[1])

#thread = threading.Thread(target=bot.polling, daemon=True)
#thread.start()

l = Listener()
l.start()

