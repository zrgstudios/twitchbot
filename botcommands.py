# defining commands to be used in chat

# !/usr/bin/env python3
import random
import sqlite3
import re
from twitchbot import (
    twitchchat,
    encryption_key,
    current_game,
    sql_commands,
    viewerclass,)


def sql_file():
    sqlite_file = r'MyFiles\ViewerData_' + encryption_key.decrypted_chan + '.sqlite'
    return sqlite_file


def hours_file():
    hrs_file = r'MyFiles\hours_' + encryption_key.decrypted_chan + '.sqlite'
    return hrs_file


starting_val = '-'


def handle_commands(s, username, message, general):

    if message.startswith(starting_val + 'pythoncommands'):
        twitchchat.chat(s, python_commands())

    elif message.startswith(starting_val + "hello"):
        twitchchat.chat(s, hello() + ' ' + username)

    elif message.startswith(starting_val + "eightball"):
        twitchchat.chat(s, random.choice(eight_ball()))

    elif message.startswith(starting_val + "bm"):
        twitchchat.chat(s, bm(username))

    elif message.startswith(starting_val + 'github'):
        twitchchat.chat(s, github())

    elif message.startswith(starting_val + 'feelgood'):
        twitchchat.chat(s, feel_good(username))

    elif message.startswith(starting_val + 'joinmessage'):
        try:
            message_regex = re.search(r"(" + starting_val + "joinmessage .+)", message)
            join_message = message_regex.group(0).split(" ", 1)[1].strip() + ' - ' + username

            conn = sqlite3.connect(sql_file())
            c = conn.cursor()
            c.execute("UPDATE ViewerData Set Join_Message = ? WHERE User_Name = ?", (join_message, username))
            twitchchat.chat(s, username + ', your message has been saved!')
            if username in general.no_joinmessage:
                general.no_joinmessage.remove(username)
            conn.commit()
            conn.close()
        except AttributeError:
            pass

    elif message.startswith(starting_val + 'thecastlegame'):
        twitchchat.whisper(s, '.w ' + username + ' A test whisper message')

    elif message.startswith(starting_val + 'joindate'):
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        sql_date = c.execute('SELECT Join_Date FROM ViewerData WHERE User_Name = ?', (username,))
        string_date = sql_date.fetchone()
        if string_date is None:
            pass
        else:
            string_date = string_date[0]
            string_date = str(string_date)
            twitchchat.chat(s, str(username) + ' your oldest follow/date you joined the stream is ' + string_date)
        conn.close()

    elif message.startswith(starting_val + 'myid'):
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        sql_UID = c.execute('SELECT UID FROM ViewerData WHERE User_Name = ?', (username,))
        string_UID = sql_UID.fetchone()
        try:
            string_UID = string_UID[0]
            twitchchat.chat(s, '.w ' + username + ' ' + str(string_UID) + ' is your UID, write this down and don\'t '
                                                                          'lose it! If you ever lose your account or '
                                                                          'change names, you can use this UID to '
                                                                          'retrieve your old data')
        except TypeError:
            twitchchat.chat(s, 'Sorry ' + username + 'you haven\'t been added to the database yet! Please wait a '
                                                     'minute then try again')
        conn.close()

    elif message.startswith(starting_val + 'hours'):
        game_list = ['LoL', 'SC2', 'League']
        count = 0

        if count == 0:
            conn1 = sqlite3.connect(hours_file())
            c1 = conn1.cursor()
            conn2 = sqlite3.connect(sql_file())
            c2 = conn2.cursor()

            sql_games = c1.execute('SELECT DISTINCT Game FROM Hours')
            string_games = sql_games.fetchall()
            for i in string_games:
                game_list.append(i[0])

            sql_uid = c2.execute('SELECT UID FROM ViewerData WHERE User_Name=?', (username,))
            string_uid = sql_uid.fetchone()

            hours_strip = message.replace(starting_val + 'hours ', '')
            if hours_strip.strip() in game_list:
                game = hours_strip.strip()
                hl = []
                if game == 'LoL' or game == 'League':
                    game = 'LeagueofLegends'
                elif game == 'SC2':
                    game = 'StarCraftII'

                sql_game = c1.execute('SELECT Hours FROM Hours WHERE Game=? AND UID=?', (game, string_uid[0]))
                string_game = sql_game.fetchall()
                for i in string_game:
                    hl.append(i[0])
                hl = round((sum(hl)/60)/60, 2)
                twitchchat.chat(s, username + ' your hours for ' + game + ' is ' + str(hl))
                count += 1

            else:
                try:
                    hours_list = []
                    sql_hours = c1.execute("SELECT Hours FROM Hours WHERE UID=? AND Game NOT IN ('Offline')",
                                           (string_uid[0],))
                    string_hours = sql_hours.fetchall()
                    for i in string_hours:
                        hours_list.append(i[0])
                    total_hours = round((sum(hours_list)/60)/60, 2)
                    twitchchat.chat(s, username + ' your total online hours are: ' + str(total_hours))
                    count += 1
                except TypeError:
                    twitchchat.chat(s, 'Please wait a minute' + username + ', we are still adding you to the database!')

            conn1.close()
            conn2.close()

    elif message.startswith(starting_val + 'chatlines'):
        conn1 = sqlite3.connect(hours_file())
        c1 = conn1.cursor()
        conn2 = sqlite3.connect(sql_file())
        c2 = conn2.cursor()

        sql_uid = c2.execute('SELECT UID FROM ViewerData WHERE User_Name=?', (username,))
        string_uid = sql_uid.fetchone()

        chat_list = []
        sql_chat_lines = c1.execute('SELECT Chat FROM Hours Where UID=?', (string_uid[0],))
        string_chat_lines = sql_chat_lines.fetchall()
        for i in string_chat_lines:
            if i[0] is None:
                i = 0
                chat_list.append(i)
            else:
                chat_list.append(i[0])
        total_chatlines = sum(chat_list)
        twitchchat.chat(s, username + ' your total chatlines are ' + str(total_chatlines))

        conn1.close()
        conn2.close()

    elif message.startswith(starting_val + 'appsignup'):
        twitchchat.chat(s, 'https://goo.gl/forms/Cmf7aVBrZNSbGbQX2')

    elif message.startswith(starting_val + "points"):
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        sql_user_points = c.execute("SELECT Points FROM ViewerData WHERE User_Name=?", (username,))
        string_user_points = sql_user_points.fetchone()
        string_user_points = string_user_points[0]
        string_user_points = round(string_user_points, 2)
        twitchchat.chat(s, username + " you have " + str(string_user_points) + " points!")

    elif message.startswith(starting_val + "compare"):
        #try:
        keyword = ((message.split(' ')[1]).strip()).capitalize()
        if keyword == "Points" or keyword == "Hours" or keyword == "Chatlines":
            sec_username = ((message.split(' ')[2]).strip()).lower()
            if "Points" in message or "points" in message:
                conn = sqlite3.connect(sql_file())
                c = conn.cursor()

                sql_points1 = c.execute("SELECT Points FROM ViewerData Where User_Name=?", (username,))
                string_points1 = sql_points1.fetchone()
                sql_points2 = c.execute("SELECT Points FROM ViewerData Where User_Name=?", (sec_username,))
                string_points2 = sql_points2.fetchone()

                difference = (abs(int(string_points1[0])) - int(string_points2[0]))
                twitchchat.chat(s, username + " has " + str(round(string_points1[0], 2)) + ", " + sec_username + " has "
                                + str(round(string_points2[0], 2)) + ", that's a difference of " + str(difference))

            else:
                conn1 = sqlite3.connect(hours_file())
                c1 = conn1.cursor()
                conn2 = sqlite3.connect(sql_file())
                c2 = conn2.cursor()

                sql_uid1 = c2.execute("SELECT UID FROM ViewerData WHERE User_Name=?", (username,))
                string_uid1 = sql_uid1.fetchone()
                string_uid1 = string_uid1[0]
                sql_uid2 = c2.execute("SELECT UID FROM ViewerData WHERE User_Name=?", (sec_username,))
                string_uid2 = sql_uid2.fetchone()
                if string_uid2 is None:
                    pass
                else:
                    if keyword.capitalize() == 'Chatlines':
                        keyword = 'Chat'
                    string_uid2 = string_uid2[0]

                    sql_keyword_grab1 = c1.execute("SELECT %s FROM Hours WHERE UID=? AND Game NOT IN ('Offline')"
                                                   % keyword,
                                                   (string_uid1,))
                    string_keyword_grab1 = sql_keyword_grab1.fetchall()
                    keyword_sum1 = []
                    for i in string_keyword_grab1:
                        keyword_sum1.append(i[0])
                    sum1_total = sum(keyword_sum1)

                    sql_keyword_grab2 = c1.execute("SELECT %s FROM Hours WHERE UID=? AND Game NOT IN ('Offline')"
                                                   % keyword,
                                                   (string_uid2,))
                    string_keyword_grab2 = sql_keyword_grab2.fetchall()
                    keyword_sum2 = []
                    for i in string_keyword_grab2:
                        keyword_sum2.append(i[0])
                    sum2_total = sum(keyword_sum2)

                    difference = (abs(int(sum1_total)) - int(sum2_total))

                    if keyword == 'Chat':
                        difference = abs(difference)
                        twitchchat.chat(s, username + " has " + str(sum1_total) + " chatlines, " + sec_username + " has " +
                                        str(sum2_total) + " chatlines, that's a difference of " + str(difference))
                    elif keyword == 'Hours':
                        difference = abs(round(difference/3600, 2))
                        sum1_total = round((sum1_total/3600), 2)
                        sum2_total = round((sum2_total/3600), 2)
                        twitchchat.chat(s, username + " has " + str(sum1_total) + ", " + sec_username + " has " +
                                        str(sum2_total) + ", that's a difference of " + str(difference) + '!')

                conn1.close()
                conn2.close()
        #except (TypeError, sqlite3.OperationalError, IndexError) as e:
        #    print(e, 237)

    elif message.startswith(starting_val + "top"):
        bots = sql_commands.get_bot_list()  # this is an sql command will be in its own file and referenced from there
        try:
            keyword = (message.split()[1])
            keyword = keyword.capitalize()
            keyword = keyword.strip()
            if keyword == "Hours" or keyword == "Points" or keyword == "Chatlines":

                conn1 = sqlite3.connect(hours_file())
                c1 = conn1.cursor()
                conn2 = sqlite3.connect(sql_file())
                c2 = conn2.cursor()

                sql_uid_list = c2.execute("SELECT UID FROM ViewerData")
                string_uid_list = sql_uid_list.fetchall()
                uid_dict = {}
                for i in string_uid_list:
                    if keyword == "Hours":
                        sql_hours_per_uid = c1.execute \
                            ("SELECT COALESCE (SUM(Hours), 0) FROM Hours WHERE UID=? AND Game NOT IN ('Offline')",
                             (i[0],))
                        string_hours_per_uid = sql_hours_per_uid.fetchone()
                        if i[0] in bots:
                            pass
                        else:
                            uid_dict[i[0]] = string_hours_per_uid
                    elif keyword == "Points":
                        sql_points_per_uid = c2.execute("SELECT Points FROM ViewerData WHERE UID=?", (i[0],))
                        string_points_per_uid = sql_points_per_uid.fetchone()
                        if i[0] in bots:
                            pass
                        else:
                            uid_dict[i[0]] = string_points_per_uid
                    else:
                        sql_keyword_per_uid = c1.execute(
                            "SELECT COALESCE (SUM(Chat), 0) FROM Hours WHERE UID=?", (i[0],))
                        string_keyword_per_uid = sql_keyword_per_uid.fetchone()
                        if i[0] in bots:
                            pass
                        else:
                            uid_dict[i[0]] = string_keyword_per_uid

                conn1.close()
                conn2.close()

                dict_vals = sorted(uid_dict.items(), key=lambda d: d[1][0], reverse=True)[:10]

                string_join = ""
                count = 1
                if keyword == "Chatlines":
                    string_join = "The top ten chatters are - "
                elif keyword == "Points":
                    string_join = "The top ten point holders are - "
                elif keyword == "Hours":
                    string_join = "The top ten watchers are - "

                conn = sqlite3.connect(sql_file())
                c = conn.cursor()
                for (i, (uid, (value,))) in enumerate(dict_vals):
                    sql_username = c.execute("SELECT User_Name FROM ViewerData WHERE UID=?", (uid,))
                    string_username = sql_username.fetchone()
                    string_username = string_username[0]
                    if keyword == "Hours":
                        value = int(value / 3600)
                    elif keyword == "Points":
                        value = round(float(value), 2)
                    string_join += ('(' + str(count) + ')' + str(string_username) + ': ' + str(value)) + ' '
                    count += 1
                conn.close()
                twitchchat.chat(s, string_join)
            else:
                pass
        except (ValueError, sqlite3.OperationalError, IndexError):
            pass

    elif message.startswith(starting_val + "testme"):
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        sql_mod_check = c.execute("SELECT User_Type FROM ViewerData WHERE User_Name = ?", (username,))
        string_mod_check = sql_mod_check.fetchone()
        if string_mod_check[0] == "Moderator" or string_mod_check[0] == "Streamer":
            sql_mod_points = c.execute("SELECT Points FROM ViewerData WHERE User_Name = ?", (username,))
            string_mod_points = sql_mod_points.fetchone()
            mod_points = int(string_mod_points[0]) - random.randrange(30, 500)
            c.execute("UPDATE ViewerData SET Points = ? WHERE User_Name = ?", (mod_points, username))
            twitchchat.chat(s, "Whoops, looks like you lost some points there " + username + "! You went from " +
                            str(round(string_mod_points[0], 2)) + " to " + str(round(mod_points, 2)))
            conn.commit()
        else:
            twitchchat.chat(s, "/timeout " + username + " " + str(random.randrange(30, 500)))
        conn.close()

    elif message.startswith(starting_val + "game") or message.startswith(starting_val + "Game"):
        twitchchat.chat(s, current_game.game_name())

    elif message.startswith(starting_val + "invite") \
        or message.startswith(starting_val + 'honor') \
            or message.startswith(starting_val + 'dishonor'):
        try:
            keyword = ((message.split()[1]).strip()).lower()
            conn = sqlite3.connect(sql_file())
            c = conn.cursor()
            sql_check = c.execute("SELECT Invited_By FROM ViewerData WHERE User_Name = ?", (username,))
            string_check = sql_check.fetchone()

            if string_check[0] is None:
                sql_all_names = c.execute("SELECT User_Name FROM ViewerData")
                string_all_names = sql_all_names.fetchall()
                all_names_list = []
                for i in string_all_names:
                    all_names_list.append(i[0])
                if keyword not in all_names_list:
                    twitchchat.chat(s, "It looks like you spelled your inviters name wrong! Please try again " +
                                    username)
                if message.startswith(starting_val + "invite"):
                    if keyword == username:
                        twitchchat.chat(s, "Nice try " + username)
                        twitchchat.chat(s, "/timeout " + username + " 10")
                    else:
                        general.viewer_objects[username].points += 50  # this prob doesnt work
                        keyword.points += 100
                        # the below should be removed and all updates should happen at once
                        """c.execute("UPDATE ViewerData SET Points = Points + 50 WHERE User_Name = ?", 
                                  (username.lower(),))
                        c.execute("UPDATE ViewerData SET Points = Points + 100 WHERE User_Name = ?", 
                                  (keyword.lower(),))
                        c.execute("UPDATE ViewerData Set Invited_By = ? WHERE User_Name = ?", 
                                  (keyword, username.lower(),))"""
                        viewerclass.invite_rank_movement(inviter_viewer=username, invited_viewer=keyword)
                        twitchchat.chat(s, "Points added to you " + username + " and " + keyword)
                elif message.startswith(starting_val + 'honor'):  # honor and dishonor don't work yet
                    keyword.rankpoints += 100
                    username.rankpoints += 25
                elif message.startswith(starting_val + 'dishonor'):
                    keyword.rankpoints -= 100
                    username.rankpoints += 25
            conn.commit()
            conn.close()
        except IndexError:
            pass

    elif message.startswith(starting_val + "reward"):
        rewardval = rewards(username=username)
        if rewardval is False:
            twitchchat.chat(s, "You don't have enough points for that")
        else:
            twitchchat.chat(s, ".w " + username + " Your code is " + rewardval)

    elif message.startswith(starting_val + 'guessnumber'):
        if general.randnum == -1:
            general.create_num()
        else:
            guess_regex = re.search(r"(guessnumber \d+)", message)
            try:
                guess = guess_regex.group(0).split(" ")[1]
                if int(guess) > int(general.our_val):
                    twitchchat.chat(s, 'Number is too high! Try guessing lower ' + username)

                elif int(guess) < int(general.our_val):
                    twitchchat.chat(s, 'Number is too low! Try guessing higher ' + username)

                elif int(guess) == int(general.our_val):
                    twitchchat.chat(s, "Nice guess! The answer was " + str(general.our_val))
                    general.create_num()
            except AttributeError:
                twitchchat.chat(s, 'You have to include a number ' + username)


def hello():
    return "hello"


def eight_ball():
    return ["No", "Yes", "Leave me alone", "I think we already know the answer to THAT",
            "I'm not sure",
            "My sources point to yes", "Could be yes, could be no, nobody knows!", "Maybe",
            "Are you kidding me?", "You may rely on it", 'Outlook not so good', 'Don\'t count on it',
            'Most likely', 'Without a doubt', 'As I see it, yes']


def bm(username):
    bm_list = ["Bronze 5 is too good for you " + username, "Hey " + username + " you're terrible at this",
               "Your mother is a bronze 5 and your father smells of elderberries " + username,
               "Crying yourself to sleep again tonight " + username + "? Good.",
               "Is your father still out at the store? Don't worry, he'll come back soon " + username,
               "If only someone cared " + username + "...",
               username + " you must be a glutton for punishment eh?", username + " I bet you main yasuo",
               username + " you degenerate weeb lover", "Hey " + username + ", you tried, now if only that mattered...",
               'Trying for first in the Darwin awards ' + username + '? Go you!', "Nobody loves you " + username +
               ", stop bothering me",
               username + " you have two parts of brain, 'left' and 'right'. In the left side, there's nothing right. "
               "In the right side, there's nothing left.",
               "It's better to let someone think you are an idiot than to open your mouth and prove it " + username,
               "Hey " + username + " you know how your parents always called you special? I just wanted to "
                                   "make sure you knew that wasn't a compliment", "Heyya " + username
               + ", just an FYI, you suck", "You know " + username +
               ", your parents have always said you were a happy accident, and yet I've never seen them happy after "
               "having you", "Hey " + username + " you’ll be good at something in life someday!"
                             " Or maybe barely mediocre, don’t want to get your hopes up too high now...",
               username + ", you light up my day like a lightbulb lights up a mine workers day, just barely "
                          "and only because there’s no other options",
               "I'm always happy at the beginning of the day, then I see you " + username +
               " and get inexplicably depressed again", "For every second of every day, I try to forget you a little "
                                                        "more " + username, "I just can't do this anymore, I'm sorry "
               + username + ", I slept with your significant other, except I'm really not that sorry, "
                            "and they told me I was better than you. It was great...", "So hows life treating you "
                                                                                       "lately " + username +
               "? Ah I'm sorry is that still a touchy subject for you?", username +
               " you are a great human being with a lot of potential! "
               "But only if great means terrible and potential means ugly"]
    return random.choice(bm_list)


def python_commands():
    return 'https://giphertius.wordpress.com/2018/02/20/giphertius-python-commands/'


def github():
    return 'https://github.com/ZERG3R/PythonBot'


def feel_good(username):
    feel_good_list = ["You're more fun than a ball pit filled with candy " + username +
                      " (And seriously, what could be more fun than that?)",
                      "That thing you don't like about yourself is what makes you so interesting " + username,
                      "If you were a box of crayons, you'd be the giant name-brand one with the built-in sharpener "
                      + username,
                      "The people you love are lucky to have you in their lives " + username,
                      "Our community is better because you're in it " + username,
                      username + ", you inspire me.",
                      username + " you have a gift for making people comfortable.",
                      username + " you are nothing less than special.",
                      username + " you always make people smile.",
                      username + " you have a heart of gold.",
                      username + " I like the way you are.",
                      username + " thanks for being there for me.",
                      username + " you inspired me to become a better person.",
                      username + " you smell good today.",
                      username + " I am honored to get to know you.",
                      "You are so talented " + username + "!",
                      "I will be here to support you on your decisions " + username,
                      "I believe in you " + username
                      ]
    return random.choice(feel_good_list)


def rewards(username):
    conn = sqlite3.connect(sql_file())
    c = conn.cursor()
    sql_user_points = c.execute("SELECT Points FROM ViewerData WHERE User_Name=?", (username,))
    string_user_points = sql_user_points.fetchone()
    string_user_points = string_user_points[0]
    string_user_points = round(string_user_points, 2)
    if int(string_user_points) > 10000:
        with open('MyFiles/rewards_file.txt', 'r') as f:
            all_lines = f.readlines()
        with open('MyFiles/rewards_file.txt', 'w') as f:
            with open('MyFiles/used_rewards.txt', 'a') as f1:
                removed_line = all_lines[0]
                all_lines.pop(0)
                for i in all_lines:
                    pass  # come back to this
                all_lines = str(all_lines)
                f1.write(removed_line + '\n')
                f.write(all_lines)
        c.execute('UPDATE ViewerData SET Points = Points - 10000 WHERE User_Name = ?', (username,))
        conn.commit()
        conn.close()
        return removed_line
    else:
        conn.commit()
        conn.close()
        return False
