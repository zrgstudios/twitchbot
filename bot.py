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
import sqlite3
import io
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
    viewerclass,
    get_commands,
    merge_databases,
    send_email,)


class General:
    def __init__(self):
        self.print_chat_count = 0

        self.hourstime_start = time.time()
        self.hourstime_end = 0
        self.hourstime_difference = 0
        self.total_hourstime = 0
        self.prev_iter_time = 0

        self.errorcount = 0

        self.get_viewers_func = False
        self.todaydate = str(datetime.datetime.today().date().strftime("%Y-%m-%d"))
        self.game_name = ''
        self.oursocket = ''

        self.viewer_objects = {}

        self.trivia = trivia_game.TriviaQuestion()
        self.trivia_object = self.trivia

        self.randnum = -1

        # gets commands from get_commands and separates them into two categories (one with random response one without)
        self.str_command_dict = {}
        self.list_command_dict = {}

        self.trivia_bool = True
        self.points_bool = True
        self.gn_bool = True
        self.honor_bool = True
        self.email_bool = True

        self.starting_val = '-'

        self.user_levels = {'Larvae': 120, 'Drone': 240, 'Zergling': 480, 'Baneling': 960, 'Overlord': 1920,
                            'Roach': 3840, 'Ravager': 7680, 'Overseer': 11520, 'Mutalisk': 14400,
                            'Corrupter': 18000, 'Hydralisk': 22500, 'Swarm Host': 28125, 'Locust': 35156,
                            'Infestor': 43945, 'Lurker': 50537, 'Viper': 58117, 'Ultralisk': 66835, 'Broodlord': 75523,
                            'Dark Archon': 123139, 'Cerebrate': 200000, 'The Overmind': 500000, 'Kerrigan': 700000}
        self.errors = []
        self.sent_errors = []
        self.connected = False
        self.ping_timer = time.time()

    def get_patchnumber(self):
        version_number = str(os.path.basename(__file__))
        """for i in os.listdir("./"):
            if "win_twitchbot" in i:
                version_number = re.search("([0-9])(.*)([0-9])", i).group(0)"""
        return version_number

    def create_num(self):
        ourval = random.randrange(0, 100)
        self.randnum = ourval
        return self.randnum


general = General()


def sql_file():
    return pathlib.Path(
        r'MyFiles\ViewerData2_' +
        encryption_key.decrypted_chan +
        '.sqlite')


def printable_logger(e):
    # Create the logger
    logger = logging.getLogger('basic_logger')
    logger.setLevel(logging.DEBUG)

    # Setup the console handler with a StringIO object
    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(level=logging.INFO)

    # Add the console handler to the logger
    logger.addHandler(ch)

    # Send log messages.
    # logger.debug('debug message')
    # logger.info('info message')
    # logger.warning('warning message')
    # logger.error('error message')
    # logger.critical('critical message')

    def info_logger(info_e=e):
        general.errors.append([general.todaydate, formatted_time(), info_e])

    def error_logger():
        log_contents = log_capture_string.getvalue()
        print(log_contents)
        log_capture_string.close()
        if log_contents != "":

            general.errors.append([general.todaydate, formatted_time(), log_contents])

    info_logger()
    error_logger()


def error_log():
    error_file = pathlib.Path('MyFiles/error_log.log')
    logging.basicConfig(filename=error_file, filemode='a', level=logging.INFO)
    curr_time = str(datetime.datetime.today())
    logging.debug(curr_time)
    sys.stderr = open(error_file, 'a')


def logging_line(e):
    printable_logger(e)
    logging.info(general.todaydate + " " + formatted_time() + "\n" + str(e) + "\nEND OF ERROR")


def handle_files():
    sys.stderr.close()
    logging.shutdown()


def formatted_time():
    return str(datetime.datetime.today().now().strftime("%I:%M"))


def connect_socket():
    try:
        s = socket.socket()
        s.connect((encryption_key.cfg_host, int(encryption_key.cfg_port)))
        s.send(
            f'CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n'.encode('utf-8'))
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
        general.connected = True
        general.ping_timer = time.time()
        return s
    except TimeoutError as e:
        logging_line(e)
        connect_socket()


def get_viewers():
    session = requests.Session()
    retry = Retry(connect=500, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    try:
        channel_json = session.get(url='https://tmi.twitch.tv/group/user/' + encryption_key.decrypted_chan
                                       + '/chatters').json()

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
    except TypeError as e:
        logging_line(e)
        return general.get_viewers_func  # shitty workaround, dont know if this will cause it to get stuck


# need to ensure this thread is inactive before trying to run again
def functionstimethread():
    try:
        t1 = threading.Thread(target=timefunctions, args=())
        t1.start()
    except Exception as e:
        logging_line(e)


def saveviewertimethread():
    try:
        t4 = threading.Thread(target=saveviewertime, args=())
        t4.start()
    except Exception as e:
        logging_line(e)


def saveviewerchatthread():
    try:
        t5 = threading.Thread(target=saveviewerchat, args=())
        t5.start()
    except Exception as e:
        logging_line(e)


# we need to make a switch to check if writing to DB, if we are then write to a temp DB then set the real DB = Temp DB
# once all transactions are finished
def saveviewertime():
    while True:
        # print(168, general.total_hourstime)
        general.hourstime_end = time.time()
        general.hourstime_difference = general.hourstime_end - general.hourstime_start

        general.total_hourstime = general.total_hourstime + \
            (general.hourstime_end - general.prev_iter_time)
        general.prev_iter_time = time.time()

        if general.get_viewers_func is not None:
            if general.get_viewers_func is not False:

                if int(general.total_hourstime) % 5 == 0:
                    game_name = general.game_name

                    viewerclass.save_seconds_for_sql(
                        getviewers=general.get_viewers_func[0] + general.get_viewers_func[1],
                        game=game_name,
                        seconds=general.hourstime_difference,
                        general=general)

                    general.hourstime_start = general.hourstime_end
        time.sleep(1)  # sleep to reduce cpu load


def timefunctions():  # make a counter here so not multiple saves occur
    error_log()
    if general.get_viewers_func is False:
        general.get_viewers_func = get_viewers()

    s = general.oursocket
    while True:
        if int(general.total_hourstime) % 10 == 0:
            #print(277, general.total_hourstime)

            general.get_viewers_func = get_viewers()
            sql_commands.check_if_user_exists(
                get_viewers=(
                        general.get_viewers_func[0] +
                        general.get_viewers_func[1]))

            for viewer in general.viewer_objects:
                if general.viewer_objects[viewer].join_message_check is False:
                    pass
                else:
                    sql_commands.welcome_viewers(
                        s=s,
                        general=general,
                        getviewers=general.get_viewers_func[0] + general.get_viewers_func[1],
                        currtime=int(time.time()))

            if len(general.get_viewers_func[0] + general.get_viewers_func[1]) < 100:
                timer = 300
            elif general.game_name == 'Offline':
                timer = 300*6
            else:
                timer = len(general.get_viewers_func[0] + general.get_viewers_func[1]) * 2
            if general.total_hourstime > timer:
                general.game_name = current_game.game_name()
                viewerclass.create_all_viewerobjects(
                    general.get_viewers_func[0] + general.get_viewers_func[1], general)

                sql_commands.update_all_users_seconds(general=general, todaydate=general.todaydate)
                sql_commands.update_user_points(general=general)
                sql_commands.update_user_chat_lines(
                    date=general.todaydate, general=general)

                sql_commands.check_users_joindate(
                    general.get_viewers_func[0] +
                    general.get_viewers_func[1])
                sql_commands.check_mods(general)  # this was before just mods
                sql_commands.update_bots()
                sql_commands.save_chat(general=general)
                sql_commands.update_invited_by(general)
                sql_commands.write_welcome_viewers(general)
                sql_commands.update_trivia_points(general)
                sql_commands.update_last_seen(general)
                sql_commands.error_log_writing(general)
                sql_commands.error_sent(general)
                print(formatted_time(), "Data finished saving")

                for viewer in general.viewer_objects:
                    if general.viewer_objects[viewer].old_uid == 0:
                        pass
                    else:
                        sql_commands.combine_db_data(general, username=viewer)

                general.total_hourstime = 0
                # should be on a separate thread
        else:
            time.sleep(.5)  # sleeping to reduce load on cpu


def saveviewerchat():
    s = general.oursocket
    try:
        full_regex = re.compile(
            r":([\w|?_]+)!\w+@\w+.tmi.twitch.tv PRIVMSG #\w+ :(.+)")
        #twitchchat.chat(s, 'LET ME LIVE')
        while True:
            response = s.recv(1024).decode("utf-8", 'ignore')
            user_and_message = handle_response(
                s=s, response=response, full_regex=full_regex)

            game_name = general.game_name

            if user_and_message:
                general.todaydate = str(datetime.datetime.today().date())

                # need to check in save_chat_for_sql if the UID exists, and if not
                # THEN call check_if_user_exists
                viewerclass.chat_honor_movement(user_and_message[0], user_and_message[1], general)
                viewerclass.save_chat_for_sql(
                    date=str(
                        general.todaydate),
                    formatted_time=formatted_time(),
                    game=game_name,
                    username=user_and_message[0],
                    message=user_and_message[1],
                    general=general)

                viewerclass.add_one_viewerobject(general, user_and_message[0])
                if user_and_message[0] not in general.viewer_objects:
                    viewerclass.add_one_viewerobject(general, user_and_message[0])
                else:
                    general.viewer_objects[user_and_message[0]].points += .2
                    if game_name not in general.viewer_objects[user_and_message[0]].chat_line_dict:
                        general.viewer_objects[user_and_message[0]].chat_line_dict[game_name] = 1
                    else:
                        general.viewer_objects[user_and_message[0]].chat_line_dict[game_name] += 1

                botcommands.handle_commands(
                    s,
                    username=user_and_message[0],
                    message=user_and_message[1],
                    general=general)
    
                if general.trivia_bool is True:
                    gamefunctions(
                        message=user_and_message[1],
                        s=s,
                        username=user_and_message[0],
                        ourtrivia=general.trivia_object)

    except UnicodeDecodeError as e:
        logging_line(e)


def gamefunctions(message, s, username, ourtrivia):
    # print(319, ourtrivia.trivia_total_time)
    # print(316, username, message)

    if len(ourtrivia.question_list) == 0:
        ourtrivia.get_question_list(ourtrivia)
    if ourtrivia.question == '':
        ourtrivia.get_question(ourtrivia=ourtrivia)
    trivia_game.trivia_question(message=message, s=s, ourtrivia=ourtrivia, starting_val=general.starting_val)

    # - Answer will now be printed out in chat if not answered after 30 seconds regardless of chat
    # (used to be chat based)
    if ourtrivia.was_question_asked is True:
        ourtrivia.trivia_bool = True
        #general.trivia_object.trivia_time_end = time.time()
        trivia_game.trivia_chat_answer(
            message=message,
            s=s,
            ourtrivia=ourtrivia,
            username=username,
            general=general)

        general.trivia_object.trivia_time_end = time.time()
        general.trivia_object.trivia_total_time = general.trivia_object.trivia_time_end - \
                                                  general.trivia_object.trivia_time_start
        trivia_game.trivia_time_answer(
            s=s,
            ourtrivia=general.trivia_object,
            trivia_total_time=general.trivia_object.trivia_total_time)
        # tried moving this from where it was so it could be time based instead of chat based, uncommenting this
        # function causes the rest of the parent function to not run


def streamer_prefs():
    # add no points for trivia option
    streamer_pref_file = 'MyFiles/streamer_prefs.txt'
    with open(streamer_pref_file, 'r') as f:
        all_lines = f.readlines()
    email_bool = False
    for line in all_lines:
        line = line.split()
        #print(line)
        if "Trivia" in line:
            if "off" in line or "Off" in line:  # be careful with this we also have a ourtrivia.trivia_bool
                general.trivia_bool = False
                print('Trivia is off')
            else:
                print('Trivia is on')
        if "Points" in line:
            if "off" in line or "Off" in line:
                general.points_bool = False
                print('Points is off')
            else:
                print('Points is on')
        if "Guessnumber" in line:
            if "off" in line or "Off" in line:
                general.gn_bool = False
                print('Guessnumber is off')
            else:
                print('Guessnumber is on')
        if "Honor" in line:
            if "off" in line or "Off" in line:
                general.honor_bool = False
                print('Honor is off')
            else:
                print('Honor is on')
        if "Email" in line:
            email_bool = True
            if "off" in line or "Off" in line:
                general.email_bool = False
                print('Email error logging is off, if there are errors ZERG3RR will not be able to fix them')
            else:
                print("Email error logging is on")
    if email_bool is False:
        with open(streamer_pref_file, 'a') as f:
            f.write("\nEmail - On\n")


def check_files():
    if not os.path.isfile('MyFiles/streamer_prefs.txt'):
        with open('MyFiles/streamer_prefs.txt', 'w') as f:
            f.write("Trivia - On\n"
                    "Points - On\n"
                    "Guessnumber Game - On\n"
                    "Honor level/Honor/Dishonor - On\n"
                    "Email - On\n")

    if not os.path.isfile('MyFiles/bot_commands.txt'):
        with open('MyFiles/bot_commands.txt', 'w') as f:
            f.write("-hello [hello username]\n-eightball [No; Yes; Leave me alone; I think we already know the "
                    "answer to THAT; I'm not sure; My sources point to yes; Could be yes, could be no, nobody knows!; "
                    "Maybe; Are you kidding me?; You may rely on it; Outlook not so good; Don't count on it; "
                    "Most likely; Without a doubt; As I see it; yes]\n"
                    "-help [https://giphertius.wordpress.com/2018/02/20/giphertius-python-commands/]")


def first_time():
    # this is dead as MyFiles is always made in encryption key now
    """directory_path = 'MyFiles'
    if not os.path.isdir(directory_path):
        print('Setting up initialization files...')
        os.mkdir(directory_path)
        print(directory_path)
        encryption_key.GetUserInput()"""

    if not os.path.isfile('MyFiles/trivia.txt'):
        send_email.new_user_email(general, logging_line)
        with open('MyFiles/trivia.txt', 'w') as f:
            f.write(
                "{Question}[League of Legends] What is Aatrox's Passive ability called?{Answer}Blood Well\n"
            
                "{Question}[League of Legends] What is Ahri's Passive ability called?{Answer}Essence Theft\n")
        print('Creating trivia file...')
        time.sleep(1)

        print('Creating database and setting up...')
        time.sleep(2)
        print('Verifying streamer...')

    verified = verify_streamer.decrypt_streamerbot()
    if verified is None:
        send_email.unverified_user(general, logging_line)
        return False


def db_merge():
    directory = r'MyFiles/'
    try:
        if os.path.isfile(merge_databases.sql_file()):
            print('MERGING DATABASE 1 PLEASE DO NOT CLOSE THE APPLICATION')
            merge_databases.copy_viewerdata()
            os.rename(directory + 'ViewerData_' + encryption_key.decrypted_chan + '.sqlite',
                      directory + 'old_ViewerData_' + encryption_key.decrypted_chan + '.sqlite')
        if os.path.isfile(merge_databases.hours_file()):
            print('MERGING DATABASE 2 PLEASE DO NOT CLOSE THE APPLICATION')
            merge_databases.copy_hoursdata()
            os.rename(directory + 'hours_' + encryption_key.decrypted_chan + '.sqlite',
                      directory + 'old_hours_' + encryption_key.decrypted_chan + '.sqlite')
    except sqlite3.OperationalError as e:
        logging_line(e)


def startup():
    sql_commands.check_table_names()
    sql_commands.get_table_columns()
    check_files()
    db_merge()
    streamer_prefs()
    """rule_check = check_runtime_info.rule_check()
    if rule_check == "":
        check_runtime_info.check_admin(logging_line)"""
    if len(sql_commands.error_log_reading()) != 0:
        send_email.send_email(msg=send_email.get_error(general), general=general, logging_line=logging_line)


def connection_check_handle():
    # this is not currently being used
    threshold = 60 * 5
    while general.connected:
        if (time.time() - general.ping_timer) > threshold:
            general.connected = False
            connect_socket()
            break


def handle_response(s, response, full_regex):
    try:
        if general.print_chat_count < 1:
            print('Connecting to twitch channel %s...' % (encryption_key.decrypted_chan,))
            general.print_chat_count += 1

        # tests connection/reconnects if disconnect occurs
        elif len(response) == 0:
            general.oursocket = connect_socket()

        elif len(response) == 1:  # probably dead ?
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
            username = re.search(r"(?<=!)(.*)(?=@)", response)
            if username is not None:
                username = username.group(0)
            if "JOIN" in response:
                viewerclass.add_one_viewerobject(
                    general=general, viewer=username)
            if username in general.viewer_objects:
                general.viewer_objects[username].last_seen_date = general.todaydate
            return None

        for i in response.split("@badges"):
            compile_match = full_regex.search(i)
            if compile_match is not None:
                username = compile_match.group(1)
                message = compile_match.group(2)
                print("(" + formatted_time() + ")" + username + ": " + message)
                return [username, message]
    except UnicodeEncodeError as e:
        logging_line(e)


def main():  # printing @badges line once, and sometimes skipping messages is a lot sent quickly
    try:
        general.game_name = current_game.game_name()
        general.todaydate = str(datetime.datetime.today().date())
        printable_logger(e="Startup of bot")
        if not os.path.exists('MyFiles/cfg.txt'):
            encryption_key.GetUserInput()
            first_time()
            send_email.new_user_email(general, logging_line=logging_line)
        startup_func = startup()
        if startup_func is False:
            return False

        func_first_time = first_time()

        if func_first_time is False:
            return False
        else:
            get_commands.get_commands(general)
            print("Version number is - ", general.get_patchnumber())
            error_log()
            logging.info(general.todaydate + " " + formatted_time() + " Startup of bot")
            general.oursocket = connect_socket()
            general.create_num()
            saveviewerchatthread()
            functionstimethread()
            saveviewertimethread()
            # print("Successful startup - connected to twitchchat")
            # handle_files()
    except Exception as e:
        print(e)
        logging_line(e)
        input("We've encountered an error, press anything to exit the twitchbot\n")


main()
