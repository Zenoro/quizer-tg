import re
from dataclasses import dataclass




@dataclass
class Question:
	type_of_q: str
	title: str
	var: list | None
	answer: set
	
	
	
def handle_s_question(text):
    title = text[0][3:]
    var = []
    temp = {}
    for row in text[1:len(text)-1]:
        temp[row[0]] = row[3:]
        var.append(row[3:])
    ans = text[-1].split()[1:]
    answer = []
    for i in ans:
        answer.append(temp[i])
    return Question('S', title, var, set(answer))
    
def handle_m_question(text):
    title = text[0][3:]
    var = []
    temp = {}
    for row in text[1:len(text)-1]:
        temp[row[0]] = row[3:]
        var.append(row[3:])
    ans = text[-1].split()[1:]
    answer = []
    for i in ans:
        answer.append(temp[i])
    return Question('M', title, var, set(answer))
    
def handle_o_question(text):
    title = text[0][3:]
    answer = text[1][3:].strip().lower()
    return Question('O', title, None, set([answer]))
	
	
def parce_file(fd):
    """
    Функция создания словаря вопросов и ответов
    Ввод: FileStreamIO
    Вывод: Словарь загадок)
    """
    text = ''
    for line in fd:
    	text+=line
    text = text.replace('\n','@')
    questions = []
    while len(text):
        match = re.search('/[SMO].*?/Q.*?@',text)
        if not match:
            break
        questions.append(match[0])
        end = match.end()
        text=text[end:]
    quenstions = [q.split('@')[0:-1] for q in questions]
    res = []
    for quest in quenstions:
        if quest[0].startswith('/S'):
            #continue
            res.append(handle_s_question(quest))
        if quest[0].startswith('/M'):
            #continue
            res.append(handle_m_question(quest))
        if quest[0].startswith('/O'):
            res.append(handle_o_question(quest))
    #for i in res:
    
    #    print(i)
    return res


