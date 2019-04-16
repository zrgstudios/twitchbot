from fuzzywuzzy import fuzz
import random
import re
import time

from twitchbot import twitchchat


starting_val = '-'


class TriviaQuestion:
    def __init__(self):
        self.question = ''
        self.question_list = []
        self.trivia_total_time = 0
        self.trivia_time_start = time.time()
        self.trivia_time_end = 0
        self.answered = False  # switch to determine if we need to get a new question or not
        self.was_question_asked = False

        trivia_bool = False

    def get_question(self, ourtrivia):
        self.question = trivia_qa(ourtrivia=ourtrivia)

    def get_question_list(self, ourtrivia):
        self.question_list = question_list_generator(ourtrivia=ourtrivia)


def question_list_generator(ourtrivia):
    file_list = ourtrivia.question_list
    trivia_file = r'MyFiles\trivia.txt'
    if len(file_list) == 0:
        with open(trivia_file, 'r') as f:
            for i in f:
                file_list.append(i)
    return file_list


def trivia_qa(ourtrivia):
    randline = random.choice(ourtrivia.question_list)
    question = re.search(r"(?<=)(.*)(?={Answer}.*)", randline)
    question = question.group(0)
    answer = re.search(r"(?<={Answer})(.*)", randline)
    answer = answer.group(0)
    ourtrivia.question_list.remove(randline)
    forthread = [question, answer]
    return forthread


def trivia_question(s, message, ourtrivia):
    if message.startswith(starting_val + 'trivia'):
        if ourtrivia.was_question_asked is False:
            if ourtrivia.answered is True:
                ourtrivia.trivia_total_time = 0
                ourtrivia.trivia_time_start = time.time()
                ourtrivia.trivia_time_end = time.time()
                ourtrivia.get_question(ourtrivia)
                ourtrivia.answered = False
        print("The answer to this triviaquestion is -", ourtrivia.question[1])
        question = ourtrivia.question[0].rstrip()
        twitchchat.chat(s, question)
        ourtrivia.was_question_asked = True


def trivia_answer(s, username, message, trivia_total_time, ourtrivia, general):
    answer = str(ourtrivia.question[1])

    if fuzz.ratio(answer.lower(), message.lower()) >= 87:
        twitchchat.chat(s, 'Nice guess ' + username + '! The answer was ' + answer + '! You got 3 points!')
        general.viewer_objects[username].trivia_answers += 1
        general.viewer_objects[username].points += 3
        ourtrivia.trivia_time_start = time.time()
        ourtrivia.trivia_total_time = 0
        ourtrivia.answered = True
        ourtrivia.was_question_asked = False

    elif trivia_total_time > 30:
        if ourtrivia.trivia_bool is True:
            twitchchat.chat(s, 'No one guessed it right! The answer was: ' + answer)
            ourtrivia.trivia_time_start = time.time()
            ourtrivia.trivia_total_time = 0
            ourtrivia.answered = True
            ourtrivia.was_question_asked = False
        else:
            ourtrivia.trivia_total_time = 0
