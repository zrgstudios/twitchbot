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

    if message.startswith(starting_val + 'joinmessage'):  # if joinmessage is empty pass
        try:
            conn = sqlite3.connect(sql_file())
            c = conn.cursor()
            sql_points = c.execute('SELECT Points FROM ViewerData WHERE User_Name=?', (username,))
            str_points = sql_points.fetchone()[0]
            if str_points + general.viewer_objects[username].points < 1000:
                twitchchat.chat(s, 'Sorry you need 1,000 points to get a joinmessage!')

            else:
                general.viewer_objects[username].points -= 1000

                message_regex = re.search(r"(" + starting_val + "joinmessage .+)", message)
                join_message = message_regex.group(0).split(" ", 1)[1].strip() + ' - ' + username
                general.viewer_objects[username].join_message_check = join_message
                twitchchat.chat(s, username + ', your message has been saved at the cost of 1000 points!')
                if username in general.no_joinmessage:
                    general.no_joinmessage.remove(username)
        except AttributeError:
            pass

    elif message.startswith(starting_val + "remove_joinmessage"):  # make this worth nothing
        general.viewer_objects[username].join_message_check = "remove_joinmessage"
        twitchchat.chat(s, 'Your joinmessage has been removed, you do not get refunded your 1000 points')

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

                sql_game = c1.execute('SELECT Hours FROM Hours WHERE Game=? AND UID=?', (game.capitalize(), string_uid[0]))
                string_game = sql_game.fetchall()
                for i in string_game:
                    hl.append(i[0])

                current_seconds = general.viewer_objects[username].seconds.get(game)
                if current_seconds is None:
                    current_seconds = 0

                hl = round((sum(hl) / 60) / 60 + (current_seconds / 60) / 60, 2)

                twitchchat.chat(s, username + ' your hours for ' + game + ' is ' + str(hl))
                count += 1

            else:
                try:
                    hours_list = []
                    sql_hours = c1.execute("SELECT Hours FROM Hours WHERE UID=? AND Game NOT IN ('Offline')",
                                           (string_uid[0],))
                    string_hours = sql_hours.fetchall()

                    total_seconds = 0
                    for game in general.viewer_objects[username].seconds:
                        total_seconds += general.viewer_objects[username].seconds.get(game)

                    for i in string_hours:
                        hours_list.append(i[0])
                    total_hours = round((sum(hours_list)/60)/60 + (total_seconds / 60) / 60, 2)
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
        all_chatlines = 0
        for game in general.viewer_objects[username].chat_line_dict:
            all_chatlines += general.viewer_objects[username].chat_line_dict[game]
        twitchchat.chat(s, username + ' your total chatlines are ' + str(total_chatlines + all_chatlines))
        # stopped here

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
        twitchchat.chat(s, username + " you have " + str(string_user_points +
                                                         general.viewer_objects[username].points) +
                        " points!")

    elif message.startswith(starting_val + "compare"):
        #try:
        keyword = ((message.split(' ')[1]).strip()).capitalize()
        if keyword == "Points" or keyword == "Hours" or keyword == "Chatlines" or keyword == "Level":
            sec_username = ((message.split(' ')[2]).strip()).lower()
            if keyword == "Points":
                conn = sqlite3.connect(sql_file())
                c = conn.cursor()

                sql_points1 = c.execute("SELECT Points FROM ViewerData Where User_Name=?", (username,))
                string_points1 = sql_points1.fetchone()
                sql_points2 = c.execute("SELECT Points FROM ViewerData Where User_Name=?", (sec_username,))
                string_points2 = sql_points2.fetchone()

                if sec_username not in general.viewer_objects:
                    difference = (abs(int(string_points1[0]) + general.viewer_objects[username].points - int
                                  (string_points2[0])))
                else:
                    difference = (abs(int(string_points1[0]) + general.viewer_objects[username].points - int
                                  (string_points2[0]) + general.viewer_objects[sec_username].points))
                twitchchat.chat(s, username + " has " + str(round(string_points1[0], 2)) + ", " + sec_username + " has "
                                + str(round(string_points2[0], 2)) + ", that's a difference of " + str(difference))
                conn.close()

            elif keyword == "Level":
                conn = sqlite3.connect(sql_file())
                c = conn.cursor()
                sql_level1 = c.execute("SELECT Level FROM ViewerData Where User_Name=?", (username,))
                string_level1 = sql_level1.fetchone()
                sql_level2 = c.execute("SELECT Level FROM ViewerData Where User_Name=?", (sec_username,))
                string_level2 = sql_level2.fetchone()

                difference = (abs(int(string_level1[0]) + general.viewer_objects[username].points - int
                              (string_level2[0]) + general.viewer_objects[sec_username].points))
                twitchchat.chat(s, username + " has " + str(round(string_level1[0], 2)) + ", " + sec_username + " has "
                                + str(round(string_level2[0], 2)) + ", that's a difference of " + str(int(difference)))
                conn.close()

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
                    if keyword == 'Chatlines':
                        keyword = 'Chat'
                    string_uid2 = string_uid2[0]
                    sql_keyword_grab1 = c1.execute("SELECT %s FROM Hours WHERE UID=? AND Game NOT IN ('Offline')"
                                                   % keyword,
                                                   (string_uid1,))
                    string_keyword_grab1 = sql_keyword_grab1.fetchall()
                    keyword_sum1 = []
                    for i in string_keyword_grab1:
                        if i[0] is None:
                            num = 0
                        else:
                            num = i[0]
                        keyword_sum1.append(num)
                    sum1_total = sum(keyword_sum1)

                    sql_keyword_grab2 = c1.execute("SELECT %s FROM Hours WHERE UID=? AND Game NOT IN ('Offline')"
                                                   % keyword,
                                                   (string_uid2,))
                    string_keyword_grab2 = sql_keyword_grab2.fetchall()
                    keyword_sum2 = []
                    for i in string_keyword_grab2:
                        if i[0] is None:
                            num = 0
                        else:
                            num = i[0]
                        keyword_sum2.append(num)
                    sum2_total = sum(keyword_sum2)

                    difference = (abs(int(sum1_total)) - int(sum2_total))

                    if keyword == 'Chat':
                        difference = abs(difference)
                        twitchchat.chat(s, username + " has " + str(sum1_total) + " chatlines, " + sec_username +
                                        " has " +
                                        str(sum2_total) + " chatlines, that's a difference of " + str(difference))
                    elif keyword == 'Hours':
                        difference = abs(round(difference/3600, 2))
                        sum1_total = round((sum1_total/3600), 2)
                        sum2_total = round((sum2_total/3600), 2)
                        twitchchat.chat(s, username + " has " + str(sum1_total) + ", " + sec_username + " has " +
                                        str(sum2_total) + ", that's a difference of " + str(difference) + '!')

                conn1.close()
                conn2.close()
        # except (TypeError, sqlite3.OperationalError, IndexError) as e:
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
            general.viewer_objects[username].points -= 10
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
            sec_username = ((message.split()[1]).strip()).lower()
            conn = sqlite3.connect(sql_file())
            c = conn.cursor()
            if message.startswith(starting_val + "invite"):
                # need to check in database then check their
                sql_check = c.execute("SELECT Invited_By FROM ViewerData WHERE User_Name=?", (username,))
                string_check = sql_check.fetchone()

                if string_check[0] is None:  # if cell is empty
                    sql_all_names = c.execute("SELECT User_Name FROM ViewerData")
                    string_all_names = sql_all_names.fetchall()
                    all_names_list = []
                    for i in string_all_names:
                        all_names_list.append(i[0])
                    if sec_username not in all_names_list:
                        twitchchat.chat(s, "It looks like you spelled the persons name wrong! Please try again " +
                                        username)

                    elif sec_username == username:
                        twitchchat.chat(s, "Nice try " + username)
                        general.viewer_objects[username].points -= 10
                        twitchchat.chat(s, "/timeout " + username + " 10")

                    elif general.viewer_objects[username].invited_by is not None or string_check[0] is not None:
                        twitchchat.chat(s, 'You\'ve already been invited by someone')
                    else:
                        general.viewer_objects[username].invited_by = sec_username
                        # will throw error if username entered wrong
                        general.viewer_objects[username].points += 50
                        general.viewer_objects[sec_username].points += 100
                        viewerclass.invite_level_movement(general=general,
                                                          inviter_viewer=username)
                        twitchchat.chat(s, "Points added to you " + username + " and " + sec_username)

            elif message.startswith(starting_val + 'honor'):  # honor and dishonor don't work yet
                general.viewer_objects[sec_username].level += 100
                general.viewer_objects[username].level += 25
            elif message.startswith(starting_val + 'dishonor'):
                general.viewer_objects[sec_username].level -= 100
                general.viewer_objects[username].level += 25
            conn.commit()
            conn.close()
        except IndexError:
            twitchchat.chat(s, 'You must include a name when doing -invite')  # did not include a name with command

    elif message.startswith(starting_val + "reward"):
        rewardval = rewards(username=username)
        if rewardval is False:
            twitchchat.chat(s, "You don't have enough points for that")
        else:
            twitchchat.chat(s, ".w " + username + " Your code is " + rewardval)

    elif message.startswith(starting_val + 'gn'):
        guess_regex = re.search(f"({starting_val}gn \d+)", message)
        try:
            guess = guess_regex.group(0).split(" ")[1]
            if int(guess) > int(general.randnum):
                twitchchat.chat(s, 'Number is too high! Try guessing lower ' + username)

            elif int(guess) < int(general.randnum):
                twitchchat.chat(s, 'Number is too low! Try guessing higher ' + username)

            elif int(guess) == int(general.randnum):
                twitchchat.chat(s, "Nice guess! The answer was " + str(general.randnum))
                general.create_num()
        except AttributeError:
            twitchchat.chat(s, 'You have to include a number ' + username)

    elif message.startswith(starting_val + 'update_id'):
        try:
            keyword = ((message.split()[1]).strip())

            conn = sqlite3.connect(sql_file())
            c = conn.cursor()
            sql_uid_check = c.execute('SELECT UID FROM ViewerData WHERE UID=?', (keyword,))
            str_uid_check = sql_uid_check.fetchone()
            if str_uid_check is None:
                twitchchat.whisper(s, '.w ' + username + ' Sorry it looks like you typed in your UID incorrectly')
            else:
                twitchchat.whisper(s, '.w ' + username + ' This will combine your old UID (which you enter) with '
                                                         'your new UID. Are you sure you want to do this? Some of your '
                                                         'current data'
                                                         'Such as your join date, invited by, and join game will be '
                                                         'overwritten. Do -confirmed_transfer {your id here} '
                                                         '(no brackets) if you\'re sure. Each time you do this is costs'
                                                         ' double the last time starting at 200 points after the '
                                                         'first time, which will be free.')
        except sqlite3.DatabaseError:
            twitchchat.whisper(s, '.w ' + username + ' Sorry it looks like you typed in your UID incorrectly')
        except IndexError:
            twitchchat.whisper(s, '.w ' + username + ' You need to enter your UID as well so it will look like '
                                                     '-update_id {UID} (no brackets)')

    elif message.startswith(starting_val + 'confirmed_transfer'):
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()

        try:
            keyword = ((message.split()[1]).strip())
            old_sql_points = c.execute('SELECT Points FROM ViewerData WHERE UID=?', (keyword,))
            old_str_points = old_sql_points.fetchone()
            new_sql_points = c.execute('SELECT Points FROM ViewerData WHERE User_Name=?', (username,))
            new_str_points = new_sql_points.fetchone()

            # here is another example
            if old_str_points[0] is None:
                old_str_points = 0
            else:
                old_str_points = old_str_points[0]
            if new_str_points[0] is None:
                new_str_points = 0
            else:
                new_str_points = new_str_points[0]

            combined_points = old_str_points + new_str_points
            # here is one example
            sql_point_check = c.execute('SELECT Updating_Name_Point_Deduction FROM ViewerData WHERE UID=?', (keyword,))
            str_point_check = sql_point_check.fetchone()

            if str_point_check[0] is None:
                str_point_check = 0
            else:
                str_point_check = str_point_check[0]

            if general.viewer_objects[username].old_uid != 0:
                twitchchat.whisper(s, '.w ' + username + ' Sorry it looks like a transfer is already in process')

            if combined_points - str_point_check < 0:
                twitchchat.whisper(s, '.w ' + username + ' Sorry you don\'t have enough combined points to do a '
                                                         'transfer')
            else:
                general.viewer_objects[username].old_uid = keyword
                twitchchat.whisper(s, '.w ' + username + ' Data Transferring. Please be patient, it will take 10-20 '
                                                         'minutes for your data to merge')
        except sqlite3.DatabaseError:
            twitchchat.whisper(s, '.w ' + username + ' Sorry it looks like you typed in your UID incorrectly')

        conn.close()

    elif message.startswith(starting_val + 'level'):
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        sql_level = c.execute('SELECT Level FROM ViewerData WHERE User_Name=?', (username,))
        str_level = sql_level.fetchone()
        level_iter = "Larvae"
        combined_level = 0
        for curr_level in general.user_levels:
            combined_level = str_level[0] + general.viewer_objects[username].level
            if combined_level > general.user_levels[curr_level]:
                level_iter = curr_level
        twitchchat.chat(s, '%s Your level is %s, and the amount of level points you have is %d' %
                        (username, level_iter, combined_level))
        conn.close()

    for command in general.list_command_dict:
        if message.startswith(command.strip()):
            random_option = random.choice(general.list_command_dict[command])
            replaced_version = random_option
            if "username" in random_option:
                replaced_version = random_option.replace("username", username)
            twitchchat.chat(s, replaced_version)

    for command in general.str_command_dict:
        if message.startswith(command.strip()):
            replaced_version = general.str_command_dict[command]
            if "username" in replaced_version:
                replaced_version = replaced_version.replace("username", username)
            twitchchat.chat(s, replaced_version)


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
