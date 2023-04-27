import unittest
import telebot
from newbot import *
from file_parser import parce_file
from dataclasses import dataclass
import pickle


@dataclass
class DumpUser:
    id: int


@dataclass
class DumpMessage:
    text: str
    from_user: DumpUser


def wrap_bot():
    def decor(func):
        def _wrapper(*args, **kwargs):
            pass
        return _wrapper
    bot.send_message = decor(bot.send_message)
    bot.register_next_step_handler = decor(bot.register_next_step_handler)
    bot.edit_message_text = decor(bot.edit_message_text)
    bot.edit_message_reply_markup = decor(bot.edit_message_reply_markup)


wrap_bot()


def standart_status(status):
    status[-1] = UserStatus(name='', res=0, user_ans=dict(), true_ans=dict(), last_bot_message=None,
                            last_user_message=None, last_markup=None, quests=quests_all, last_quest=None)


"""
Тест на S check
Тест на M check
Тест на O check

Тест на file_parser
Тест на Ask_questt??

"""


class TestDateTime(unittest.TestCase):

    def setUp(self):
        wrap_bot()
        with open('test_data/quest.txt', 'r') as filedir:
            self.quest = parce_file(filedir)
        with open('test_data/parser.txt', 'wb') as handle:
            pickle.dump(self.quest, handle)
        self.set_quest()

    def set_quest(self):
        standart_status(status)
        status[-1].quests = self.quest

    def test_check_s(self):
        self.set_quest()
        ask_question_sm(DumpMessage('hello', DumpUser(-1)), self.quest[0])
        self.assertEqual(check_answer(status[-1].last_quest, ['Гагарин']), False)
        self.assertEqual(check_answer(status[-1].last_quest, ['Спанч Боб']), True)

    def test_check_m(self):
        self.set_quest()
        ask_question_sm(DumpMessage('hello', DumpUser(-1)), self.quest[2])
        self.assertEqual(check_answer(status[-1].last_quest, ['Ургант', 'Цекало']), True)
        self.assertEqual(check_answer(status[-1].last_quest, ['Ургант', 'Цекало', 'Спанч Боб']), False)
        self.assertEqual(check_answer(status[-1].last_quest, ['Цекало', 'Ургант']), True)
        self.assertEqual(check_answer(status[-1].last_quest, []), False)

    def test_check_o(self):
        self.set_quest()
        ask_question_o(DumpMessage('hello', DumpUser(-1)), self.quest[5])
        self.assertEqual(check_answer(status[-1].last_quest, 'Пенициллин'), True)
        self.assertEqual(check_answer(status[-1].last_quest, 'пенициллин'), True)
        self.assertEqual(check_answer(status[-1].last_quest, 'Лол'), False)
        self.assertEqual(check_answer(status[-1].last_quest, 'Что тут еще написать'), False)

    def test_file_parcer(self):
        with open('test_data/quest.txt', 'r') as filedir:
            quest = parce_file(filedir)
        with open('test_data/parser.txt', 'rb') as handle:
            get = pickle.load(handle)
        self.assertEqual(quest, get)

    def test_ask_quest(self):
        self.set_quest()
        ask_question_sm(DumpMessage('hello', DumpUser(-1)), self.quest[0])
        self.assertEqual(status[-1].last_quest.title, 'Кто проживает на дне океана?')

        self.set_quest()
        ask_question_sm(DumpMessage('hello', DumpUser(-1)), self.quest[2])
        self.assertEqual(status[-1].last_quest.title, 'Кому принадлежит ресторан The Сад?')

        self.set_quest()
        ask_question_o(DumpMessage('hello', DumpUser(-1)), self.quest[5])
        self.assertEqual(status[-1].last_quest.title, 'Что было создано благодаря грибам-плесени?')


unittest.main()
