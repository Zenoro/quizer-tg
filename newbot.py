import random as rd
import readline
import time
import telebot
from telebot import types

from file_parser import parce_file


def file_saver(user_answers, true_answers, name, res):
    """
    Save the user's results locally in a file.
    
    Keyword Arguments:
    user_answers -- user responses' dictionary
    true_answers -- valid answers to questions
    name -- user's name
    res -- user's score
    """
    global quests_all
    with open(f"answers_{name}.txt", "w", encoding="utf-8") as f:
        print(f'{name}\n{time.ctime()}\nОбщий результат: {res} {round(res*100 / len(quests_all),2)}%\n', file=f)
        for num, quest in enumerate(quests_all):
            print(f"Вопрос {num+1}", file=f)
            print(f"Ответ пользователя: {user_answers[quest.title]}", file=f)
            print(f"Правильный ответ: {true_answers[quest.title]}", file=f)


def ask_question_sm(message, qst):
    """Send a question to the user, indicating the buttons for the answer under the message"""
    global last_quest
    global last_bot_message
    global last_user_message
    global last_markup
    if qst.type_of_q=='S':
        msg = qst.title + "\nНажмите верный ответ"
    else:
        msg = qst.title + "\nВыберите верные ответы"
    markup = types.InlineKeyboardMarkup()
    mark = []
    
    for i in qst.var:
        button = types.InlineKeyboardButton(i,callback_data = i)
        mark.append(button)
    if qst.type_of_q=='M':
        mark.append(types.InlineKeyboardButton('Закончить выбор',callback_data = '@'))
    markup.add(*mark)
    
    last_markup = markup
    last_quest = qst
    last_bot_message = bot.send_message(message.from_user.id, msg,reply_markup=markup)
    last_user_message = message
    
def ask_question_o(message, qst):
    """Send a question to the user that requires sending a message from the user"""
    global last_quest
    global last_user_message
    last_quest = qst
    last_user_message = message
    msg = qst.title + "\nНапечатайте верный ответ"
    bot.send_message(message.from_user.id, msg)
    bot.register_next_step_handler(message, handle_o)


def send_quest(message):
    """Select the next question to send to the user and calling the sending functions"""
    global quests

    if not(len(quests)):
        get_result(message)
        return
    quest = quests[0]
    del quests[0]
    if quest.type_of_q in ('S','M'):
        return ask_question_sm(message, quest)
    if quest.type_of_q=='O':
        return ask_question_o(message, quest)


print('Hello! Welcome to tester as teacher. Be ready with Telegram bot API, questions-file')

API_KEY = input("Enter Bot API key, given by Telegram Bot Father    ").strip()
#API_KEY = '6033741551:AAFW7B3eVpEe95aBg81S0cH8t6Cy4XtjocA'
filedir = input("Enter name of quiz-file (it should be in programm path!)    ")
#filedir = 'MYQUEST.txt'
while 1:
    try:
        filedir = open(filedir, 'r')
        break
    except FileNotFoundError:
        filedir = input("Wrong directory. Try again.    ")
new_entering_msg = input("Enter custom hello-message, if it's needed.    ").strip()
#new_entering_msg=None

quests_all = parce_file(filedir)
quests = quests_all.copy()
rd.shuffle(quests)

user_answers = dict()
true_answers = dict()
usr_res = 0
user_name = ''

print('>>BOT STARTED TO WORK<<')
bot = telebot.TeleBot(API_KEY)

def check_answer(quest, user_answer):
    """
    Check the correctness of the answer (depending on the question).
    
    Keyword Arguments:
    quest -- question
    user_answer -- question's answer via user
    """
    if quest.type_of_q in {'S','M'}:
        #print(set(user_answer), quest.answer)
        return set(user_answer) == quest.answer
    return set([user_answer.strip().lower()])==quest.answer

def handle_answer(quest, user_answer):
    """
    Perform verification, save the user response. Start the next question function
    
    Keyword Arguments:
    quest -- question
    user_answer -- question's answer via user
    """
    global usr_res
    global last_user_message
    global user_answers
    global true_answers
    #print(check_answer(quest,user_answer))
    usr_res += check_answer(quest,user_answer)
    if last_quest.type_of_q in {'S','M'}:
        user_answers[quest.title] = set(user_answer)
    else:
        user_answers[quest.title] = set([user_answer.strip().lower()])
    true_answers[quest.title] = last_quest.answer
    
    send_quest(last_user_message)
    
def callback_handle_s(user_ans):
    """TODO"""
    global last_bot_message
    global last_quest

    bot.edit_message_reply_markup(chat_id=last_bot_message.chat.id, 
                                      message_id=last_bot_message.id, 
                                      reply_markup='')
                                      
    bot.edit_message_text(chat_id=last_bot_message.chat.id, 
                              message_id=last_bot_message.id,
                              text=last_bot_message.text + f'\n\nВаш ответ: {user_ans}')
    handle_answer(last_quest, [user_ans])                          
    
    
def callback_handle_m(user_ans):
    """TODO"""
    global last_bot_message
    global last_markup
    global last_quest
    
    row = last_bot_message.text.split('\n')[-1]
    if row.startswith('Вы выбрали:'):
        ans = row.split(' | ')
        ans[0] = ans[0][ans[0].index(':')+2:]
        if ans[0]=='':
            ans=[]
    else:
        ans=[]
        
    if user_ans == "@":
        bot.edit_message_reply_markup(chat_id=last_bot_message.chat.id, 
                                      message_id=last_bot_message.id, 
                                      reply_markup='')
        handle_answer(last_quest,ans) 
        return
        
    new_text = last_bot_message.text
    rows = new_text.split('\n')
    last_row = rows[-1]
    new_text = ''
    for i in rows[0:-1]:
        new_text+=i
    new_text+='\n\nВы выбрали: '
    if user_ans in ans:
        ans.remove(user_ans)
    else:
        ans.append(user_ans)
    if len(ans):
        new_text+=ans[0]
        for i in ans[1:]:
            new_text+=' | '+i
        
    message = bot.edit_message_text(chat_id=last_bot_message.chat.id, 
                              message_id=last_bot_message.id,
                              text=new_text,
                              reply_markup=last_markup)
    last_bot_message = message
    
def handle_o(message):
    """TODO"""
    global last_quest 
    handle_answer(last_quest, message.text)
 
    
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call): 
    """TODO"""
    if call.data:
        global last_quest
        if last_quest.type_of_q == 'S':
            callback_handle_s(call.data)
        elif last_quest.type_of_q == 'M':
            callback_handle_m(call.data)
        elif last_quest.type_of_q == 'O':
            callback_handle_o(call.data)
                

@bot.message_handler(content_types=['text'])
def start(message):
    """Start to host bot, request user's name."""
    #send_quest(message)
    #return
    
    if message.text == '/start':
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
    """TODO"""
    global user_name
    user_name = message.text
    MSG = f"Всего в тесте будет {len(quests)} вопросов трёх типов: \n\
            \tс множественным выбором, \n\
            \tс определенным ответом, \n\
            \tвыбором одного правильного ответа. \n\
            Напишите ответ для начала теста."
    bot.send_message(message.from_user.id, MSG)
    bot.register_next_step_handler(message, send_quest)
    
def get_result(message):
    """TODO"""
    global user_name
    global user_res
    global user_answers
    global true_answers
    
    bot.send_message(message.from_user.id, f'Ваш результат: {usr_res}')
    file_saver(user_answers, true_answers, user_name, usr_res)
    tmp_questions = quests_all.copy()
    rd.shuffle(tmp_questions)

bot.polling(none_stop=True, interval=0)
