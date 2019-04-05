# http://www.instructables.com/id/Twitchtv-Moderator-Bot/
# !/usr/bin/env python3

import time
import datetime
import os
import re
import requests
import socket
import logging
import sys
import threading
import pathlib
import random
from requests.adapters import HTTPAdapter
from urllib3 import Retry
# from queue import Queue  # we will need this later I think when there
# are a lot of messages

# project specific imports
from twitchbot import (
    botcommands,
    current_game,
    encryption_key,
    sql_commands,
    trivia_game,
    verify_streamer,
    viewerclass,)


fkey = encryption_key.fkey


class General:
    def __init__(self):
        self.print_chat_count = 0

        self.chattime_start = time.time()
        self.chattime_end = 0
        self.chattime_difference = 0

        self.hourstime_start = time.time()
        self.hourstime_end = 0
        self.hourstime_difference = 0
        self.total_hourstime = 0
        self.prev_iter_time = 0

        self.errorcount = 0

        self.get_viewers_func = False
        self.todaydate = datetime.datetime.today().date().strftime("%Y-%m-%d")
        self.game_name = ''
        self.oursocket = ''

        self.viewer_objects = {}

        self.trivia = trivia_game.TriviaQuestion()

        self.randnum = -1

    def create_num(self):
        randnum = random.randrange(0, 100)
        self.our_val = randnum
        return self.our_val


general = General()


def sql_file():
    return pathlib.Path(
        r'MyFiles\ViewerData_' +
        encryption_key.decrypted_chan +
        '.sqlite')


def hours_file():
    return pathlib.Path(
        r'MyFiles\hours_' +
        encryption_key.decrypted_chan +
        '.sqlite')


def error_log():
    # need to change logging level, currently captures too much and gets bogged down quickly
    error_file = pathlib.Path('MyFiles/error_log.log')
    logging.basicConfig(filename=error_file, filemode='a', level=logging.ERROR)
    # curr_time = str(datetime.datetime.today())
    # logging.error(curr_time)
    sys.stderr = open(error_file, 'a')


def handle_files():
    sys.stderr.close()
    logging.shutdown()


def formatted_time():
    return datetime.datetime.today().now().strftime("%I:%M")


def connect_socket():
    try:
        s = socket.socket()
        s.connect((encryption_key.cfg_host, int(encryption_key.cfg_port)))
        s.send(
            'raw CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n'.encode('utf-8'))
        s.send(
            "PASS {}\r\n".format(
                encryption_key.decrypted_pass).encode("utf-8"))
        s.send(
            "NICK {}\r\n".format(
                encryption_key.decrypted_nick).encode("utf-8"))  # bot name
        s.send(
            "JOIN {}\r\n".format(
                '#' +
                encryption_key.decrypted_chan).encode("utf-8"))  # channel name
        return s
    except TimeoutError:
        print('Could not connect, retrying')
        connect_socket()


def get_viewers():
    session = requests.Session()
    retry = Retry(connect=500, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    channel_json = session.get(url='https://tmi.twitch.tv/group/user/' +
                                   encryption_key.decrypted_chan +
                                   '/chatters').json()

    broadcaster = (channel_json['chatters']['broadcaster'])
    viewers = (channel_json['chatters']['viewers'])
    moderators = (channel_json['chatters']['moderators'])
    staff = (channel_json['chatters']['staff'])
    vips = (channel_json['chatters']['vips'])
    global_mods = (channel_json['chatters']['global_mods'])
    admins = (channel_json['chatters']['admins'])
    viewers_list = viewers + staff + vips + global_mods + admins
    viewers_and_mods = [viewers_list, moderators + broadcaster]
    return viewers_and_mods
    # this had multiple try/excepts (typeerror and valueerror, might crash now)


# need to ensure this thread is inactive before trying to run again
def functionstimethread():
    t1 = threading.Thread(target=timefunctions, args=())
    t1.start()


def saveviewertimethread():
    t4 = threading.Thread(target=saveviewertime, args=())
    t4.start()


def functionschatthread():
    t2 = threading.Thread(target=chatfunctions, args=())
    t2.start()


def saveviewerchatthread():
    t5 = threading.Thread(target=saveviewerchat, args=())
    t5.start()


# we need to make a switch to check if writing to DB, if we are then write to a temp DB then set the real DB = Temp DB
# once all transactions are finished
def saveviewertime():
    while True:
        # error_log()
        #print(168, general.total_hourstime)
        general.hourstime_end = time.time()
        general.hourstime_difference = general.hourstime_end - general.hourstime_start

        general.total_hourstime = general.total_hourstime + \
            (general.hourstime_end - general.prev_iter_time)
        general.prev_iter_time = time.time()

        if general.get_viewers_func is not None:
            if general.get_viewers_func is not False:

                if int(general.total_hourstime) % 5 == 0:
                    game_name = general.game_name

                    viewerclass.save_hours_for_sql(
                        getviewers=general.get_viewers_func[0] + general.get_viewers_func[1],
                        game=game_name,
                        seconds=general.hourstime_difference,
                        general=general)

                    general.hourstime_start = general.hourstime_end

                    for viewer in general.viewer_objects:
                        if general.viewer_objects[viewer].join_message_check is False:
                            pass
                        else:
                            general.viewer_objects[viewer].time_before_last_seen += general.hourstime_difference
                            if general.viewer_objects[viewer].time_before_last_seen > 2400:
                                sql_commands.welcome_viewers(
                                    s=general.oursocket,
                                    general=general,
                                    getviewers=general.get_viewers_func[0] +
                                    general.get_viewers_func[1])


def timefunctions():
    if general.get_viewers_func is False:
        general.get_viewers_func = get_viewers()

    while True:
        if int(general.total_hourstime) % 10 == 0:
            general.get_viewers_func = get_viewers()
        if general.total_hourstime > 300:
            general.game_name = current_game.game_name()
            viewerclass.create_all_viewerobjects(
                general.get_viewers_func[0] + general.get_viewers_func[1], general)

            sql_commands.update_all_users_hours(general=general, todaydate=general.todaydate)
            sql_commands.update_user_points(general=general)
            sql_commands.update_user_chat_lines(
                date=general.todaydate, general=general)

            sql_commands.check_users_joindate(
                general.get_viewers_func[0] +
                general.get_viewers_func[1])
            sql_commands.check_mods(general.get_viewers_func[1])
            sql_commands.update_bots()
            print(formatted_time(), "Data finished saving")

            for viewer in general.get_viewers_func[0] + general.get_viewers_func[1]:
                if viewer in general.viewer_objects:
                    general.viewer_objects[viewer].time_before_last_seen = general.viewer_objects[viewer].last_seen
                    general.viewer_objects[viewer].last_seen = int(time.time())

            general.total_hourstime = 0
            # should be on a separate thread
        # handle_files()


def saveviewerchat():
    s = general.oursocket
    full_regex = re.compile(
        r":([\w|?_]+)!\w+@\w+.tmi.twitch.tv PRIVMSG #\w+ :(.+)")
    # twitchchat.chat(s, 'This bot was created by zerg3rr at twitch dot tv')
    while True:
        response = s.recv(1024).decode("utf-8")
        user_and_message = handle_response(
            s=s, response=response, full_regex=full_regex)

        game_name = general.game_name

        if user_and_message:
            general.todaydate = datetime.datetime.today().date()

            # need to check in save_chat_for_sql if the UID exists, and if not
            # THEN call check_if_user_exists
            viewerclass.save_chat_for_sql(
                date=str(
                    general.todaydate),
                formatted_time=formatted_time(),
                game=game_name,
                username=user_and_message[0],
                message=user_and_message[1],
                general=general)
            if game_name not in general.viewer_objects[user_and_message[0]].chat_line_dict:
                general.viewer_objects[user_and_message[0]].chat_line_dict[game_name] = 1
            else:
                general.viewer_objects[user_and_message[0]].chat_line_dict[game_name] += 1

            botcommands.handle_commands(
                s,
                username=user_and_message[0],
                message=user_and_message[1],
                general=general)

            gamefunctions(
                message=user_and_message[1],
                s=s,
                username=user_and_message[0],
                ourtrivia=general.trivia)
        # handle_files()


def chatfunctions():
    if general.get_viewers_func is False:
        general.get_viewers_func = get_viewers()
    while True:
        # error_log()
        general.chattime_end = time.time()
        general.chattime_difference = general.chattime_end - general.chattime_start

        if general.chattime_difference > 60:
            sql_commands.check_if_user_exists(
                get_viewers=(
                    general.get_viewers_func[0] +
                    general.get_viewers_func[1]))

            # set this false before we start writing to database
            # so messages are not lost/saved to placeholder

            sql_commands.save_chat(general=general)
            # once  writing for each key to the db is one, set the main dict to be equal to the placeholder
            # and then reset our placeholder and the bool
            general.chattime_start = general.chattime_end
        else:
            time.sleep(1)
        # handle_files()


def gamefunctions(message, s, username, ourtrivia):
    # error_log()

    general.create_num()


    # print(319, ourtrivia.trivia_total_time)
    if len(ourtrivia.question_list) == 0:
        ourtrivia.get_question_list(ourtrivia)
    if ourtrivia.question == '':
        ourtrivia.get_question(ourtrivia=ourtrivia)
    trivia_game.trivia_question(message=message, s=s, ourtrivia=ourtrivia)

    if ourtrivia.counter == 1:
        ourtrivia.trivia_time_end = time.time()
        ourtrivia.trivia_total_time = ourtrivia.trivia_time_end - ourtrivia.trivia_time_start
        trivia_game.trivia_answer(
            message=message,
            s=s,
            ourtrivia=ourtrivia,
            trivia_total_time=ourtrivia.trivia_total_time,
            username=username)
    # handle_files()


def first_time():
    directory_path = 'MyFiles'
    if not os.path.isdir(directory_path):
        print('Setting up initialization files...')
        os.mkdir(directory_path)
        print(directory_path)
        encryption_key.GetUserInput()

    if not pathlib.Path('MyFiles/trivia.txt'):
        with open('MyFiles/trivia.txt', 'w') as f:
            f.write(
                "{Question}[League of Legends] What is Aatrox's Passive ability called?{Answer}Blood Well\n")
            f.write(
                "{Question}[League of Legends] What is Ahri's Passive ability called?{Answer}Essence Theft\n")
        print('Creating trivia file...')
        time.sleep(1)

    if not pathlib.Path(sql_file()):
        sql_commands.create_viewer_tables()

    if not pathlib.Path(hours_file()):
        sql_commands.insert_hours_table()
        sql_commands.get_table_columns()
        print('Creating database and setting up...')
        time.sleep(2)
        print('Verifying streamer...')

    verified = verify_streamer.decrypt_streamerbot()
    if verified is None:
        return False


def startup():
    sql_commands.get_table_columns()
    sql_commands.check_table_names()


def handle_response(s, response, full_regex):
    try:
        if general.print_chat_count < 1:
            print('Connecting to twitch...')
            general.print_chat_count += 1

        # tests connection/reconnects if disconnect occurs
        elif len(response) == 0:
            general.oursocket = connect_socket()

        elif len(response) == 1:
            general.errorcount += 1

        # tests if we get a ping so we can pong back
        elif "PING :tmi.twitch.tv\r\n" in response:
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            time.sleep(1 / (20 / 30))

        elif ".tmi.twitch.tv WHISPER" in response:
            remove_whisper = re.search(r"(?<=WHISPER )(.*)", response).group(0)
            whisper_message = re.search(
                r"(?<= :)(.*)", remove_whisper).group(0)
            username = re.search(r"(?<=!)(.*)(?=@)", response).group(0)
            print("WHISPER - " + '(' + formatted_time() + ')' +
                  username + ": " + str(whisper_message))
            return [username, whisper_message]

        elif ".tmi.twitch.tv PART" in response or ".tmi.twitch.tv JOIN" in response:
            print(430, response)
            username = re.search(r"(?<=!)(.*)(?=@)", response).group(0)
            sql_commands.update_last_seen(username)
            if "JOIN" in response:
                print(username, 'has joined')
                """if username not in general.recently_joined:
                    general.recently_joined.append(username)"""
                viewerclass.add_one_viewerobject(
                    general=general, viewer=username)
            return None

        for i in response.split("@badges"):
            compile_match = full_regex.search(i)
            if compile_match is not None:
                username = compile_match.group(1)
                message = compile_match.group(2)
                print("(" + formatted_time() + ")" + username + ": " + message)
                return [username, message]
    except UnicodeEncodeError:
        pass


def main():  # printing @badges line once, and sometimes skipping messages is a lot sent quickly
    general.game_name = current_game.game_name()
    if not os.path.exists('MyFiles/cfg.txt'):
        encryption_key.GetUserInput()
        first_time()
    if not sql_file().is_file():
        first_time()
        time.sleep(1)
    startup()

    func_first_time = first_time()

    if func_first_time is False:
        return False
    else:
        # error_log()
        general.oursocket = connect_socket()
        general.create_num()
        functionschatthread()
        saveviewerchatthread()

        functionstimethread()
        saveviewertimethread()
        # handle_files()

    """except AttributeError as e:
        print('AttributeError, no value in response for username:', e)
        time.sleep(.5)
        general.errorcount += 1
        if general.errorcount >= 4:
            return False
    except ConnectionAbortedError as e:
        print('Connection severed:', e)
        time.sleep(.5)
        general.errorcount += 1
        if general.errorcount >= 4:
            return False
    except UnicodeDecodeError as e:
        print('Weird character, passing:', e)
        time.sleep(.5)
    except socket.gaierror as e:
        print('Connection failed to get game, restarting', e)
        return False"""


main()


"""def query_after_break():
    while True:
        func_first_time = first_time()
        if func_first_time is False:
            break
        else:
            if main() is False:
                print('Restarting main')
                main()


query_after_break()"""
