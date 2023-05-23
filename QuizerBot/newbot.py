import random as rd
import readline
import time
import telebot
from telebot import types
import os
import gettext

from .file_parser import parce_file
from .user_status import UserStatus


translation = gettext.translation('newbot', 'l10n', ['eng'], fallback=True)
_ = translation.gettext


def file_saver(id_):
    """
    Save the user's results locally in a file.
    
    :param id_: The user's key to the dictionary status
    """
    global quests_all
    global status
    with open(f"local_answers/answers_{status[id_].name}.txt", "w", encoding="utf-8") as f:
        res = status[id_].res
        print(status[id_].name, file=f)
        print(time.ctime(), file=f)
        print(_("Общий результат:"), res, ' ', round(res*100 / len(quests_all), 2), '%', sep='', file=f)
        for num, quest in enumerate(quests_all):
            print(_("Вопрос {}".format(num+1)), file=f)
            print(_("Ответ пользователя: {}".format(status[id_].user_ans[quest.title])), file=f)
            print(_("Правильный ответ: {}".format(status[id_].true_ans[quest.title])), file=f)


def get_result(message):
    """Completing the test, saving the results"""
    global status
    global count_flag
    bot.send_message(message.from_user.id, _('Ваш результат: {}'.format(status[message.from_user.id].res)))
    if count_flag:
        file_saver(message.from_user.id)
        count_flag -= 1


def bot_starter():
    """Start the bot"""
    print(_('Приветствуем администратора! Будьте готовы ввести Телеграм-бот ключ, имя файла вопросов'))

    API_KEY = input(_("Введите ключ API бота, предоставленный Telegram Bot Father    ")).strip()
    filedir = input(_("Введите имя файла теста (файл должен находиться в той же папке, где и программа!)\
                       или его абсолютный путь    "))
    while 1:
        try:
            filedir = open(filedir, 'r')
            break
        except FileNotFoundError:
            filedir = input(_("Неправильный путь или имя файла. Пробуйте снова.    "))
    save_flag = input(_("Нужно ли сохранять результаты участников локально? [n]    "))
    if not os.path.exists('local_answers'):
        os.makedirs('local_answers')
    # os.chdir('local_answers')
    if save_flag and save_flag.strip().lower() not in 'n no нет н т'.split():
        try:
            count_flag = int(input(_('Введите максимальное количество участников для сохранения [5]    ')))
        except ValueError:
            count_flag = 5
    else:
        count_flag = 0
    new_entering_msg = input(_("Введите ваше приветственное сообщение (если это необходимо).    ")).strip()
    bot = telebot.TeleBot(API_KEY)

    quests_all = parce_file(filedir)
    quests = quests_all.copy()
    rd.shuffle(quests)
    return bot, quests, quests_all, new_entering_msg, count_flag


def ask_question_sm(message, qst, _status=None, _bot=None):
    """Send a question to the user, indicating the buttons for the answer under the message"""
    global bot
    if _status is None:  # Костыль
        global status
    else:
        status = _status
    if _bot is not None:  # Костыль
        bot = _bot
    
    id_ = message.from_user.id
    
    letters = 'abcdefghijklmnopqrstuvwxyz'
    
    msg = qst.title + '\n'
    for num, i in enumerate(qst.var):
        msg += letters[num] + ') ' + i + '\n'

    if qst.type_of_q == 'S':
        msg += "\n" + _("Нажмите верный ответ")
    else:
        msg += "\n" + _("Выберите верные ответы")
    markup = types.InlineKeyboardMarkup()
    mark = []

    for num, i in enumerate(qst.var):
        button = types.InlineKeyboardButton(letters[num], callback_data=i)
        mark.append(button)
    if qst.type_of_q == 'M':
        mark.append(types.InlineKeyboardButton(_('Закончить выбор'), callback_data='@'))
    markup.add(*mark)

    status[id_].last_markup = markup
    status[id_].last_quest = qst
    status[id_].last_bot_message = bot.send_message(message.from_user.id, msg, reply_markup=markup)
    status[id_].last_user_message = message


def ask_question_o(message, qst, _status=None, _bot=None):
    """Send a question to the user that requires sending a message from the user"""
    global bot
    if _status is None:  # Костыль
        global status
    else:
        status = _status
    
    if _bot is not None:  # Костыль
        bot = _bot
    id_ = message.from_user.id

    status[id_].last_quest = qst
    status[id_].last_user_message = message

    msg = qst.title + "\n"+_("Напечатайте верный ответ")
    bot.send_message(message.from_user.id, msg)
    if _status is None:  # Костыль
        bot.register_next_step_handler(message, handle_o)

        
def send_quest(message):
    """Select the next question to send to the user and calling the sending functions"""
    global status
    id_ = message.from_user.id

    if not len(status[id_].quests):
        get_result(message)
        return
    quest = status[id_].quests[0]
    del status[id_].quests[0]
    if quest.type_of_q in ('S', 'M'):
        return ask_question_sm(message, quest)
    if quest.type_of_q == 'O':
        return ask_question_o(message, quest)

        
def handle_answer(id_, quest: str, user_answer: str):
    """
    Perform verification, save the user response. Start the next question function
    
    :param id_: The user's key to the dictionary status
    :param quest: Question string
    :param user_answer: Question's answer via user
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

        
def handle_o(message):
    """Сheck the user's message for the correctness of the answer to the question"""
    global status
    id_ = message.from_user.id
    handle_answer(id_, status[id_].last_quest, message.text)

        
def check_answer(quest: str, user_answer: str) -> set:
    """
    Check the correctness of the answer (depending on the question).
    
    :param quest: Question string
    :param user_answer: Question's answer via user
    """
    if quest.type_of_q in {'S', 'M'}:
        # print(set(user_answer), quest.answer)
        return set(user_answer) == quest.answer
    return set([user_answer.strip().lower()]) == quest.answer


def main():
    global status
    global bot
    global count_flag
    global quests_all
    status = dict()
    bot, quests, quests_all, new_entering_msg, count_flag = bot_starter()

    def callback_handle_s(id_, user_ans):
        """
        Process the callback of a button with the user's answer to a question with one answer
        
        :param id_: The user's key to the dictionary status
        :param user_ans: Users's answer on the last question
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
                              text=text + _('Ваш ответ: {}'.format(user_ans)))
        handle_answer(id_, last_quest, [user_ans])

    def callback_handle_m(id_, user_ans):
        """
        Process the callback of a button with the user's answer to a question with several answers
        
        :param id_: The user's key to the dictionary status
        :param user_ans:  Users's answer on the last question
        """
        global status
        last_bot_message = status[id_].last_bot_message
        last_markup = status[id_].last_markup
        last_quest = status[id_].last_quest

        row = last_bot_message.text.split('\n')[-1]
        if row.startswith(_('Вы выбрали:')):
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
        new_text += _('Вы выбрали:') + ' '
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
        quests = quests_all.copy()
        rd.shuffle(quests)
        status[message.from_user.id] = UserStatus(name='', res=0, user_ans=dict(), true_ans=dict(),
                                                  last_bot_message=None, last_user_message=None,
                                                  last_markup=None, quests=quests, last_quest=None)

        if message.text == '/start':
            print(message.from_user.id, _('подключился'))
            if new_entering_msg:
                bot.send_message(message.from_user.id, new_entering_msg)
            else:
                bot.send_message(message.from_user.id, _("Приветствуем!"))
            bot.send_message(message.from_user.id, _("Напишите свои фамилию и имя перед началом тестирования!"))
            bot.register_next_step_handler(message, get_name)
        else:
            bot.send_message(message.from_user.id, _('Напиши /start'))

    def get_name(message):
        """User name registration"""
        global status
        print(message.from_user.id, 'connected as', message.text)
        status[message.from_user.id].name = message.text
        MSG = _("Всего в тесте будет {} вопросов трёх типов:".format(len(quests))) + "\n\t"\
            + _("с множественным выбором,") + "\n\t"\
            + _("с определенным ответом,") + "\n\t"\
            + _("с выбором одного правильного ответа.") + "\n"\
            + _("Напишите ответ для начала теста.")
        bot.send_message(message.from_user.id, MSG)
        bot.register_next_step_handler(message, send_quest)

    print('>>', _('БОТ НАЧАЛ СВОЮ РАБОТУ'), '<<', sep='')
    bot.polling(none_stop=True, interval=0)
    

if __name__ == '__main__':
    main()
