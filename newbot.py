import random as rd
import readline
import time
import telebot
from telebot import types


def add_helper(qst):
    """
    Функция добавления подсказки к вопросу (в зависимости от вопроса)
    Ввод: тело вопроса + вариантов
    Вывод: вопрос + вариант + подсказка ввода ответов
    """
    if qst.startswith('/S'):
        return qst[3:] + "\nВведите единственный верный вариант ответа:"
    elif qst.startswith('/M'):
        return qst[3:] + "\nВведите все верные варианты ответов через пробел:"
    elif qst.startswith('/O'):
        return qst[3:] + "\nВведите правильный ответ:"


def dict_of_answers(fd):
    """
    Функция создания словаря вопросов и ответов
    Ввод: FileStreamIO
    Вывод: Словарь загадок)
    """
    dd = dict()
    question_name = ""
    variants = ""
    ans = ""
    for line in fd:
        if line.startswith('/S') or line.startswith('/O') or\
                line.startswith('/M') or line.startswith("//"):    # name of question
            question_name += line.lstrip()
        elif not (line.startswith('/Q') or line == '\n'):   # variants
            variants += line.lstrip()
        elif line.startswith('/Q'):
            ans = line[2:].strip()
        else:
            # if not variants:
            #     dd[question_name] = ans
            # else:
            dd[question_name+variants.rstrip()] = ans
            question_name = ""
            variants = ""
            ans = ""
            continue
    return dd


def answer_ruler(quest, pred_answ, train_answ):
    """
    Функция проверки правильности ответа (в зависимости от вопроса)
    Ввод:
        quest - данный вопрос
        pred_answ - ответ на вопрос
        train_answ - верный ответ
    Вывод: Результат проверки (T/F)
    """
    # print(f"{quest=}, {pred_answ=}, {train_answ=}")
    if quest.startswith('/M'):
        tmptrueres = "".join(sorted(train_answ.strip().lower().split()))
        tmpansw = "".join(sorted(pred_answ.strip().lower().split()))
        return tmpansw == tmptrueres
    elif quest.startswith('/S') or quest.startswith('/O'):
        return pred_answ.strip().lower() == train_answ.strip().lower()


def file_saver(used_dict, name, res):
    """
    Функция сохранения результатов пользователя локально в файле
    Ввод:
        used_dict - словарь ответов пользователя
        name - имя пользователя
        res - результат пользователя
    """
    global quest_dict
    with open(f"answers_{name}.txt", "w", encoding="utf-8") as f:
        print(f'{name}\n{time.ctime()}\nОбщий результат: {res} ({res / len(quest_dict)}%)\n', file=f)
        for num, quest in enumerate(quest_dict):
            print(f"Вопрос {num+1}", file=f)
            print(f"Ответ пользователя: {used_dict[quest]}", file=f)
            print(f"Правильный ответ: {quest_dict[quest]}", file=f)


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

quest_dict = dict_of_answers(filedir)
tmp_questions = [i for i in quest_dict.keys()]
rd.shuffle(tmp_questions)

answers_of_users = dict()
usr_res = 0
user_name = ''

print('>>BOT STARTED TO WORK<<')
bot = telebot.TeleBot(API_KEY)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        # print(message.from_user.id)
        if new_entering_msg:
            bot.send_message(message.from_user.id, new_entering_msg)
            bot.register_next_step_handler(message, get_name)
        else:
            bot.send_message(message.from_user.id, "Приветствуем!\
                                                    Представьтесь системе:\n\
                                                    Напишите свои фамилию и имя перед началом тестирования!")
            bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')


def get_name(message):
    global user_name
    user_name = message.text
    MSG = f"Всего в тесте будет {len(quest_dict)} вопросов трёх типов: \n\
            \tс множественным выбором, \n\
            \tс определенным ответом, \n\
            \tвыбором одного правильного ответа. \n\
            Напишите ответ для начала теста."
    bot.send_message(message.from_user.id, MSG)
    bot.register_next_step_handler(message, send_fst_quest)


def send_fst_quest(message):
    global tmp_questions
    msg = add_helper(tmp_questions[0])
    bot.send_message(message.from_user.id, msg)
    bot.register_next_step_handler(message, request_answ)


def request_answ(message):
    global tmp_questions
    global usr_res
    global answers_of_users
    usr_ans = message.text
    answers_of_users[tmp_questions[0]] = message.text
    usr_res += answer_ruler(tmp_questions[0], usr_ans, quest_dict[tmp_questions[0]])
    tmp_questions.pop(0)
    if tmp_questions:
        msg = add_helper(tmp_questions[0])
        bot.send_message(message.from_user.id, msg)
        bot.register_next_step_handler(message, request_answ)
    else:
        bot.send_message(message.from_user.id, f'Ваш результат: {usr_res}')
        file_saver(answers_of_users, user_name, usr_res)
        tmp_questions = [i for i in quest_dict.keys()]
        rd.shuffle(tmp_questions)


bot.polling(none_stop=True, interval=0)
