from dataclasses import dataclass
from telebot.types import Message
from file_parser import Question


@dataclass
class UserStatus:
    name: str
    res: int

    user_ans: dict
    true_ans: dict

    last_bot_message: Message
    last_user_message: Message
    last_markup: list

    quests: list
    last_quest: Question
