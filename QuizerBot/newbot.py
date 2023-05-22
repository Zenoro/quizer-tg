import random as rd
import time
import telebot
from telebot import types

from .file_parser import parce_file
from .user_status import UserStatus


def file_saver(id_):
    """
    Save the user's results locally in a file.
    
    Keyword Arguments:
    id_ -- the user's key to the dictionary status
    """
    global quests_all
    global status
    with open(f"answers_{status[id_].name}.txt", "w", encoding="utf-8") as f:
        res = status[id_].res
        print(f'{status[id_].name}\n{time.ctime()}\nОбщий результат: {res} {round(res*100 / len(quests_all),2)}%\n',
              file=f)
        for num, quest in enumerate(quests_all):
            print(f"Вопрос {num+1}", file=f)
            print(f"Ответ пользователя: {status[id_].user_ans[quest.title]}", file=f)
            print(f"Правильный ответ: {status[id_].true_ans[quest.title]}", file=f)


def ask_question_sm(message, qst):
    """Send a question to the user, indicating the buttons for the answer under the message"""
    global status
    id_ = message.from_user.id

    letters = 'abcdefghijklmnopqrstuvwxyz'
    
    msg = qst.title + '\n'
    for num, i in enumerate(qst.var):
        msg += letters[num] + ') ' + i + '\n'

    if qst.type_of_q == 'S':
        msg += "\nНажмите верный ответ"
    else:
        msg += "\nВыберите верные ответы"
    markup = types.InlineKeyboardMarkup()
    mark = []

    for num, i in enumerate(qst.var):
        button = types.InlineKeyboardButton(letters[num], callback_data=i)
        mark.append(button)
    if qst.type_of_q == 'M':
        mark.append(types.InlineKeyboardButton('Закончить выбор', callback_data='@'))
    markup.add(*mark)

    status[id_].last_markup = markup
    status[id_].last_quest = qst
    status[id_].last_bot_message = bot.send_message(message.from_user.id, msg, reply_markup=markup)
    status[id_].last_user_message = message


def ask_question_o(message, qst):
    """Send a question to the user that requires sending a message from the user"""
    global status
    id_ = message.from_user.id

    status[id_].last_quest = qst
    status[id_].last_user_message = message

    msg = qst.title + "\nНапечатайте верный ответ"
    bot.send_message(message.from_user.id, msg)
    bot.register_next_step_handler(message, handle_o)


def send_quest(message):
    """Select the next question to send to the user and calling the sending functions"""
    global status
    id_ = message.from_user.id

    if not(len(status[id_].quests)):
        get_result(message)
        return
    quest = status[id_].quests[0]
    del status[id_].quests[0]
    if quest.type_of_q in ('S', 'M'):
        return ask_question_sm(message, quest)
    if quest.type_of_q == 'O':
        return ask_question_o(message, quest)


if __name__ == '__main__' or __name__ == 'QuizerBot.newbot':
    print('Hello! Welcome to tester as teacher. Be ready with Telegram bot API, questions-file')

    API_KEY = input("Enter Bot API key, given by Telegram Bot Father    ").strip()
    filedir = input("Enter name of quiz-file (it should be in programm path!)    ")
    while 1:
        try:
            filedir = open(filedir, 'r')
            break
        except FileNotFoundError:
            filedir = input("Wrong directory. Try again.    ")
    new_entering_msg = input("Enter custom hello-message, if it's needed.    ").strip()
else:
    filedir = 'MYQUEST.txt'
    filedir = open(filedir, 'r')
    API_KEY = '6033741551:AAFW7B3eVpEe95aBg81S0cH8t6Cy4XtjocA'
    new_entering_msg = ''

quests_all = parce_file(filedir)
quests = quests_all.copy()
rd.shuffle(quests)

status = dict()


bot = telebot.TeleBot(API_KEY)


def check_answer(quest, user_answer):
    """
    Check the correctness of the answer (depending on the question).
    
    Keyword Arguments:
    quest -- question
    user_answer -- question's answer via user
    """
    if quest.type_of_q in {'S', 'M'}:
        # print(set(user_answer), quest.answer)
        return set(user_answer) == quest.answer
    return set([user_answer.strip().lower()]) == quest.answer


def handle_answer(id_, quest, user_answer):
    """
    Perform verification, save the user response. Start the next question function
    
    Keyword Arguments:
    id_ -- the user's key to the dictionary status
    quest -- question
    user_answer -- question's answer via user
    """
    global status
    # print(check_answer(quest,user_answer))
    status[id_].res += check_answer(quest, user_answer)

    if status[id_].last_quest.type_of_q in {'S', 'M'}:
        status[id_].user_ans[quest.title] = set(user_answer)
    else:
        status[id_].user_ans[quest.title] = set([user_answer.strip().lower()])
    status[id_].true_ans[quest.title] = status[id_].last_quest.answer

    send_quest(status[id_].last_user_message)


def callback_handle_s(id_, user_ans):
    """
    Process the callback of a button with the user's answer to a question with one answer
    
    Keyword Arguments:
    id_ -- the user's key to the dictionary status
    user_ans -- users's answer on the last question
    """
    global status
    last_bot_message = status[id_].last_bot_message
    last_quest = status[id_].last_quest

    bot.edit_message_reply_markup(chat_id=last_bot_message.chat.id,
                                  message_id=last_bot_message.id,
                                  reply_markup='')

    text = last_bot_message.text
    split = text.split('\n')
    text = ''
    for i in split[:-1]:
        text += i+'\n'
    bot.edit_message_text(chat_id=last_bot_message.chat.id,
                          message_id=last_bot_message.id,
                          text=text + f'Ваш ответ: {user_ans}')
    handle_answer(id_, last_quest, [user_ans])


def callback_handle_m(id_, user_ans):
    """
    Process the callback of a button with the user's answer to a question with several answers
    
    Keyword Arguments:
    id_ -- the user's key to the dictionary status
    user_ans -- users's answer on the last question
    """
    global status
    last_bot_message = status[id_].last_bot_message
    last_markup = status[id_].last_markup
    last_quest = status[id_].last_quest

    row = last_bot_message.text.split('\n')[-1]
    if row.startswith('Вы выбрали:'):
        ans = row.split(' | ')
        ans[0] = ans[0][ans[0].index(':')+2:]
        if ans[0] == '':
            ans = []
    else:
        ans = []

    if user_ans == "@":
        bot.edit_message_reply_markup(chat_id=last_bot_message.chat.id,
                                      message_id=last_bot_message.id,
                                      reply_markup='')
        handle_answer(id_, last_quest, ans)
        return

    new_text = last_bot_message.text
    rows = new_text.split('\n')
    new_text = ''
    for i in rows[0:-1]:
        new_text += i + '\n'
    new_text += 'Вы выбрали: '
    if user_ans in ans:
        ans.remove(user_ans)
    else:
        ans.append(user_ans)
    if len(ans):
        new_text += ans[0]
        for i in ans[1:]:
            new_text += ' | '+i

    status[id_].last_bot_message = bot.edit_message_text(chat_id=last_bot_message.chat.id,
                                                         message_id=last_bot_message.id,
                                                         text=new_text,
                                                         reply_markup=last_markup)


def handle_o(message):
    """Сheck the user's message for the correctness of the answer to the question"""
    global status
    id_ = message.from_user.id
    handle_answer(id_, status[id_].last_quest, message.text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """The callback function for the user to acquire buttons under the questions"""
    if call.data:
        global status
        last_quest = status[call.from_user.id].last_quest
        id_ = call.from_user.id
        if last_quest.type_of_q == 'S':
            callback_handle_s(id_, call.data)
        elif last_quest.type_of_q == 'M':
            callback_handle_m(id_, call.data)


@bot.message_handler(content_types=['text'])
def start(message):
    """Start to host bot, request user's name."""
    global status
    print(message.from_user.id)
    quests = quests_all.copy()
    rd.shuffle(quests)
    status[message.from_user.id] = UserStatus(name='', res=0, user_ans=dict(), true_ans=dict(), last_bot_message=None,
                                              last_user_message=None, last_markup=None, quests=quests, last_quest=None)

    if message.text == '/start':
        # print(message.from_user.id)
        if new_entering_msg:
            bot.send_message(message.from_user.id, new_entering_msg)
            bot.register_next_step_handler(message, get_name)
        else:
            bot.send_message(message.from_user.id, """Приветствуем!\
                                                    Представьтесь системе:\n\
                                                    Напишите свои фамилию и имя перед началом тестирования!""")
            bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')


def get_name(message):
    """User name registration"""
    global status
    status[message.from_user.id].name = message.text
    MSG = f"Всего в тесте будет {len(quests)} вопросов трёх типов: \n\
            \tс множественным выбором, \n\
            \tс определенным ответом, \n\
            \tвыбором одного правильного ответа. \n\
            Напишите ответ для начала теста."
    bot.send_message(message.from_user.id, MSG)
    bot.register_next_step_handler(message, send_quest)


def get_result(message):
    """Completing the test, saving the results"""
    global status

    bot.send_message(message.from_user.id, f'Ваш результат: {status[message.from_user.id].res}')
    file_saver(message.from_user.id)

def main():
    print('>>BOT STARTED TO WORK<<')
    bot.polling(none_stop=True, interval=0)
    
if __name__ == '__main__':
    print('>>BOT STARTED TO WORK<<')
    bot.polling(none_stop=True, interval=0)
