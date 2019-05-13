import sqlite3
import datetime
import requests
import re
from copy import deepcopy

from twitchbot import (encryption_key,
                       current_game,
                       twitchchat)

channel_name = encryption_key.decrypted_chan


def new_sql_file():
    sqlite_file = r'MyFiles\ViewerData2_' + encryption_key.decrypted_chan + '.sqlite'
    return sqlite_file


def create_viewer_tables():
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()

    table2 = 'ViewerData'
    column1 = 'UID'
    column2 = 'User_Name'
    column3 = 'User_Type'
    column4 = 'Honor'
    column5 = 'Points'
    column14 = 'Join_Message'
    column15 = 'Join_Date'
    column16 = 'Join_Date_Check'
    column17 = 'Last_Seen'
    column18 = 'Join_Game'
    column19 = 'Invited_By'
    str_type = 'STRING'
    int_type = 'INTEGER'

    c.execute(
        'CREATE TABLE {table2}( '
        '{nf1} {ft1} PRIMARY KEY,'
        '{nf2} {ft2} UNIQUE,'
        '{nf3} {ft3},'
        '{nf4} {ft4},'
        '{nf5} {ft5},'

        '{nf14} {ft14},'
        '{nf15} {ft15},'
        '{nf16} {ft16},'
        '{nf17} {ft17},'
        '{nf18} {ft18},'
        '{nf19} {ft19})'
        .format(table2=table2,
                nf1=column1, ft1=int_type,
                nf2=column2, ft2=str_type,
                nf3=column3, ft3=str_type,
                nf4=column4, ft4=str_type,
                nf5=column5, ft5=int_type,

                nf14=column14, ft14=str_type,
                nf15=column15, ft15=str_type,
                nf16=column16, ft16=str_type,
                nf17=column17, ft17=str_type,
                nf18=column18, ft18=str_type,
                nf19=column19, ft19=str_type))

    """c.execute("CREATE TABLE Daily_Stats (Entry_Number INTEGER PRIMARY KEY, UID INTEGER, Game STRING, Date STRING, "
              "Seconds INTEGER, Chat INTEGER)")

    c.execute("CREATE TABLE viewer_chat (MessageNum INTEGER PRIMARY KEY, UID INTEGER, Date STRING, "
              "Time STRING, Message STRING, Game STRING)")"""

    c.execute('INSERT INTO ViewerData(UID, User_Name, User_Type, Honor, Points, Join_Date) '
              'VALUES(12358132, "zerg3rr", "Creator", "0", "0", "2014-06-01")')
    conn.commit()
    conn.close()


def insert_user(User_Name, User_Type, Join_Date, game):
    try:
        conn = sqlite3.connect(new_sql_file())
        c = conn.cursor()
        if type(User_Name) is list or User_Name is None:
            pass
        elif str(User_Name).isdigit():
            if User_Name[0] == 0:
                pass
        else:
            c.execute('INSERT INTO ViewerData(UID, "User_Name", User_Type, Join_Date, Points, Join_Game) Values'
                      '(?, LOWER(?), ?, ?, ?, ?)', (UID_generator(), str(User_Name), User_Type, Join_Date, 0, game))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError as e:
        #print(92, e)
        pass  # this is not getting a new uid fast enough(?), dont know where its hung up


def get_table_columns():  # startup
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    sql_ViewerData_column_list = c.execute("PRAGMA table_info(ViewerData)")
    string_ViewerData_column_list = sql_ViewerData_column_list.fetchall()
    columns = []
    for i in string_ViewerData_column_list:
        columns.append(i[1])
    if "Points" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Points INTEGER")
    if "Last_Seen" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Last_Seen STRING")
    if "Invited_By" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Invited_By STRING")
    if "Join_Game" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Join_Game STRING")
    if "Updating_Name_Point_Deduction" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Updating_Name_Point_Deduction INTEGER")
    if "Trivia_Answers" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Trivia_Answers INTEGER")

    conn.commit()
    conn.close()


def check_table_names():  # startup
    table_list = []

    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    sql_table_names = c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    string_table_names = sql_table_names.fetchall()
    for i in string_table_names:
        table_list.append(i[0])

    if "ViewerData" not in table_list:
        create_viewer_tables()

    if "viewer_chat" not in table_list:
        c.execute("CREATE TABLE viewer_chat (MessageNum INTEGER PRIMARY KEY, UID INTEGER, Date STRING, "
                  "Time STRING, Message STRING, Game STRING)")
    if "Daily_Stats" not in table_list:
        c.execute("CREATE TABLE Daily_Stats (Entry_Number INTEGER PRIMARY KEY, UID INTEGER, Game STRING, Date STRING, "
                  "Seconds INTEGER, Chat INTEGER)")
    if "Error_Log" not in table_list:
        c.execute("CREATE TABLE Error_Log (Entry_Number INTEGER PRIMARY KEY, Date STRING, "
                  "Time STRING, Error STRING, Sent STRING, Patch_Number STRING)")
    conn.commit()
    conn.close()


def error_log_writing(general):
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    sql_entry_number = c.execute("SELECT MAX(Entry_Number) FROM Error_Log")
    str_entry_number = sql_entry_number.fetchone()
    if str_entry_number[0] is None or str_entry_number is None:
        str_entry_number = 1
    else:
        str_entry_number = str_entry_number[0] + 1

    if general.errors is not None:
        for i in general.errors:
            err_date = str(i[0])
            err_time = str(i[1])
            err_error = str(i[2])
            version_number = general.version_number
            c.execute("INSERT INTO Error_Log (Entry_Number, Date, Time, Error, Patch_Number) VALUES(?, ?, ?, ?, ?)",
                      (str_entry_number, err_date, err_time, err_error, version_number))
            general.errors.remove(i)

    conn.commit()
    conn.close()


def error_log_reading():
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    sql_all_errors = c.execute("SELECT * FROM Error_Log WHERE Sent IS NULL")
    str_all_errors = sql_all_errors.fetchall()
    conn.close()
    return str_all_errors


def error_sent(general):
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    for i in general.sent_errors:
        c.execute("UPDATE Error_Log SET Sent=? WHERE Entry_Number=?", ("x", i,))
    conn.commit()
    conn.close()


def get_last_uid():
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    last_uid = c.execute('SELECT MAX(UID) FROM ViewerData')
    largest_uid = last_uid.fetchone()
    largest_uid = largest_uid[0]
    conn.close()
    return largest_uid


def base_UID():
    base_first = 1
    base_second = base_first + base_first
    base_third = base_first + base_second
    base_fourth = base_second + base_third
    base_fifth = base_third + base_fourth
    base_sixth = base_fourth + base_fifth
    base_seventh = base_fifth + base_sixth
    fullalgorithm = str(base_first) + str(base_second) + str(base_third) + str(base_fourth) + str(base_fifth) + \
                    str(base_sixth) + str(base_seventh)
    algorithm = fullalgorithm[0:8]
    return algorithm


def UID_generator():  # this needs to read the last uid from the database and use the algorithm on
    # it to get the next number then add the next number to the file when a new user is entered
    algorithm = str(get_last_uid())
    base_algo = 0
    # convert the above to a string so it can be iterated over
    secondtolast_char = str(algorithm[-2:-1:]).strip()  # take second to last character of algorithm
    # add our algorithm number plus the second to last character together to get our new number
    secondtolast_char = int(secondtolast_char)
    if int(secondtolast_char) != 0:
        base_algo = int(algorithm) + int(secondtolast_char)
    elif int(secondtolast_char) == 0:
        secondtolast_char = int(secondtolast_char) + 1
        base_algo = int(algorithm) + int(secondtolast_char)
    # overwrite the algorithm number with the base number to prepare for the next loop
    return base_algo


def update_all_users_seconds(general, todaydate):
    conn1 = sqlite3.connect(new_sql_file())
    c1 = conn1.cursor()
    copy_of_viewerobjects = deepcopy(general.viewer_objects)
    for viewer in copy_of_viewerobjects:
        uid = general.viewer_objects[viewer].uid
        if uid is None or uid == 'None':
            pass
        else:
            for game in copy_of_viewerobjects[viewer].seconds:

                # game = 0 day = 1 seconds = 2
                seconds = copy_of_viewerobjects[viewer].seconds.get(game)

                sql_gameuid = c1.execute("SELECT UID FROM Daily_Stats WHERE UID=? AND Game=? AND Date=?", (uid,
                                                                                                           game,
                                                                                                           todaydate))
                string_gameuid = sql_gameuid.fetchone()
                if string_gameuid is None:
                    sql_entry_number = c1.execute("SELECT MAX(Entry_Number) FROM Daily_Stats")
                    str_entry_number = sql_entry_number.fetchone()
                    if str_entry_number[0] is None:
                        str_entry_number = 1
                    else:
                        str_entry_number = str_entry_number[0] + 1
                    c1.execute('INSERT INTO Daily_Stats(Entry_Number, UID, Game, Date, Seconds) Values(?, ?, ?, ?, ?)',
                               (str_entry_number, uid, game, todaydate, seconds))
                else:

                    sql_oldtime = c1.execute("SELECT Seconds FROM Daily_Stats WHERE UID=? AND Game=? AND Date=?",
                                             (uid,
                                              game,
                                              todaydate))
                    string_oldtime = sql_oldtime.fetchone()

                    c1.execute("UPDATE Daily_Stats SET Seconds=?+? WHERE UID=? AND Game=? AND Date=?",
                               (string_oldtime[0],
                                seconds,
                                uid,
                                game,
                                todaydate))
                    for game_original in general.viewer_objects[viewer].seconds:
                        if game == game_original:
                            general.viewer_objects[viewer].seconds[game] = 0
    conn1.commit()
    conn1.close()


def update_invited_by(general):
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    copy_of_viewerobjects = deepcopy(general.viewer_objects)
    for viewer in copy_of_viewerobjects:
        if copy_of_viewerobjects[viewer].invited_by is not None:
            c.execute('UPDATE ViewerData SET Invited_By=? WHERE User_Name=?', (general.viewer_objects[viewer].
                                                                               invited_by, viewer))
    conn.commit()
    conn.close()


# will need to save everything in a class nested dict viewer_name{game:chat number}
def update_user_chat_lines(date, general):  # this should grab an item from viewerclass and add that to game for day
    conn1 = sqlite3.connect(new_sql_file())
    c1 = conn1.cursor()
    # can use this same concept for trivia questions answered correctly

    copy_of_viewerobjects = deepcopy(general.viewer_objects)

    for viewer in copy_of_viewerobjects:
        uid = copy_of_viewerobjects[viewer].uid
        for game in copy_of_viewerobjects[viewer].chat_line_dict:

            sql_old_chatlines = c1.execute("SELECT Chat FROM Daily_Stats WHERE UID=? AND Game=? AND Date=?",
                                           (uid, game, date))
            string_old_chatlines = sql_old_chatlines.fetchone()
            if string_old_chatlines is None or string_old_chatlines[0] is None:
                old_chatlines = 0
            else:
                old_chatlines = string_old_chatlines[0]
            chat_line_total = old_chatlines + copy_of_viewerobjects[viewer].chat_line_dict.get(game)
            c1.execute("UPDATE Daily_Stats SET Chat=? WHERE UID=? AND Game=? AND Date=?", (chat_line_total, uid, game,
                                                                                           date))
            general.viewer_objects[viewer].chat_line_dict[game] = 0
    conn1.commit()
    conn1.close()


def update_user_points(general):
    #try:
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()

    c.execute("UPDATE ViewerData SET Points='0' WHERE Points IS NULL")

    copy_of_viewerobjects = deepcopy(general.viewer_objects)

    for viewer in copy_of_viewerobjects:
        if general.points_bool is True:
            for game in copy_of_viewerobjects[viewer].seconds:
                # game = 0, day = 1, time = 2, username = 3
                if game == "Offline":
                    points = 0.001 * general.viewer_objects[viewer].seconds.get(game)
                    general.viewer_objects[viewer].honor += general.viewer_objects[viewer].seconds.get(game) * .005
                else:
                    points = 0.016 * general.viewer_objects[viewer].seconds.get(game)
                    general.viewer_objects[viewer].honor += general.viewer_objects[viewer].seconds.get(game) * .05
                sql_oldpoints = c.execute("SELECT Points FROM ViewerData WHERE User_Name=?", (viewer,))
                string_oldpoints = sql_oldpoints.fetchone()[0]
                total_points = float(string_oldpoints) + float(points) + general.viewer_objects[viewer].points
                c.execute("UPDATE ViewerData SET Points=? WHERE User_Name=?",
                          (total_points, viewer))
                general.viewer_objects[viewer].points = 0

        # above is for points below is for honor

        if general.honor_bool is True:
            sql_old_honor = c.execute("SELECT Honor FROM ViewerData WHERE User_Name=?", (viewer,))
            str_old_honor = sql_old_honor.fetchone()
            if str_old_honor is None or str_old_honor[0] is None:
                str_old_honor = 0
            else:
                str_old_honor = str_old_honor[0]
            #print(str_old_honor, 328)
            combined_honor = str_old_honor + general.viewer_objects[viewer].honor
            c.execute("UPDATE ViewerData SET Honor=? WHERE User_Name=?", (combined_honor, viewer))
            general.viewer_objects[viewer].honor = 0
    conn.commit()
    conn.close()
    # except (TypeError, sqlite3.OperationalError) as e:
    # pass


def update_trivia_points(general):
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    for username in general.viewer_objects:
        trivia_points = general.viewer_objects[username].trivia_answers
        if trivia_points > 0:
            sql_trivia_points = c.execute("SELECT Trivia_Answers FROM ViewerData WHERE User_Name=?", (username,))
            str_trivia_points = sql_trivia_points.fetchone()
            if str_trivia_points is None or str_trivia_points[0] is None:
                str_trivia_points = 0
            else:
                str_trivia_points = str_trivia_points[0]
            c.execute("UPDATE ViewerData SET Trivia_Answers=? WHERE User_Name=?", (str_trivia_points, username,))
            general.viewer_objects[username].trivia_answers = 0
    conn.commit()
    conn.close()


def update_bots():  # time based
    conn1 = sqlite3.connect(new_sql_file())
    c1 = conn1.cursor()

    sql_bots = c1.execute("SELECT DISTINCT UID FROM Daily_stats WHERE Game NOT IN ('Offline') "
                          "GROUP BY UID HAVING COALESCE (SUM(Seconds), 0) > 180000 "
                          "AND COALESCE (SUM(Chat), 0) < 100")

    string_bots = sql_bots.fetchall()
    for i in string_bots:
        i = i[0]
        c1.execute("UPDATE ViewerData SET User_Type = 'Botter' WHERE UID = ?", (i,))
    other_bots = ["nightbot", "moobot", encryption_key.decrypted_nick, "zerg3rrbot", "giphertius"]
    for i in other_bots:
        c1.execute("UPDATE ViewerData Set User_Type = 'Botter' WHERE User_Name = ?", (i,))

    conn1.commit()
    conn1.close()


def get_bot_list():  # time based
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    sql_uid_list = c.execute("SELECT UID FROM ViewerData WHERE User_Type = 'Botter'")
    string_uid_list = sql_uid_list.fetchall()
    bot_list = []
    for i in string_uid_list:
        bot_list.append(i[0])

    bot_list.append(encryption_key.decrypted_chan.strip())

    conn.close()
    return bot_list


def update_last_seen(general):
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    for username in general.viewer_objects:
        last_seen = general.viewer_objects[username].last_seen_date
        if last_seen is not None:

            c.execute("UPDATE ViewerData SET Last_Seen = ? WHERE User_Name = ?",
                      (general.viewer_objects[username].last_seen_date, username,))
            general.viewer_objects[username].last_seen_date = None

    conn.commit()
    conn.close()


# chat sometimes saves without the uid if the user isn't in DB yet
# need to save both the username{game:chatcount}
def save_chat(general):  # chat based
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    # message=sublist[2], game=sublist[3], formatted_time=sublist[1], date=sublist[0]

    copy_of_viewerobjects = deepcopy(general.viewer_objects)

    for viewer in copy_of_viewerobjects:
        if copy_of_viewerobjects[viewer].chat is not None:
            uid = get_uid_from_username(viewer)
            for chat_item in copy_of_viewerobjects[viewer].chat:
                sql_currnum = c.execute('SELECT MAX(MessageNum) from viewer_chat')
                string_currnum = sql_currnum.fetchone()[0]
                if string_currnum is None:
                    int_currnum = 1
                else:
                    int_currnum = int(string_currnum) + 1
                c.execute('INSERT INTO viewer_chat(MessageNum, Date, Time, UID, Message, Game) Values(?,?,?,?,?,?)',
                          (int_currnum,
                           chat_item[0],
                           chat_item[1],
                           uid,
                           chat_item[2],
                           chat_item[3]))

                copy_of_viewerobjects[viewer].chat.remove(chat_item)
                if viewer in general.viewer_objects:  # probably a bug here
                    general.viewer_objects[viewer].chat.remove(chat_item)

    conn.commit()
    conn.close()


def welcome_viewers(s, general, getviewers, currtime):  # welcomes all new viewers with a joinmessage
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    for viewer in getviewers:
        if viewer not in general.viewer_objects:
            pass
        elif general.viewer_objects[viewer].join_message_check is None:
            sql_check_for_joinmessage = c.execute("SELECT Join_Message FROM ViewerData WHERE User_Name=?",
                                                  (viewer,))
            str_check_for_joinmessage = sql_check_for_joinmessage.fetchone()
            if str_check_for_joinmessage[0] is None or str_check_for_joinmessage[0] == 'None':
                general.viewer_objects[viewer].join_message_check = False

            elif general.viewer_objects[viewer].last_seen - \
                    general.viewer_objects[viewer].time_before_last_seen > 2400 or \
                    general.viewer_objects[viewer].last_seen == 0:

                        twitchchat.chat(s, str(str_check_for_joinmessage[0]))
                        general.viewer_objects[viewer].last_seen = currtime
                        general.viewer_objects[viewer].time_before_last_seen = \
                            general.viewer_objects[viewer].last_seen
            else:
                general.viewer_objects[viewer].join_message_check = False
    conn.close()


def write_welcome_viewers(general):
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    for viewer in general.viewer_objects:
        if general.viewer_objects[viewer].join_message_check is False or \
                general.viewer_objects[viewer].join_message_check is None:
            pass
        elif general.viewer_objects[viewer].join_message_check == 'remove_joinmessage':
            c.execute("UPDATE ViewerData Set Join_Message = ? WHERE User_Name = ?", (None, viewer,))

        else:
            c.execute("UPDATE ViewerData Set Join_Message = ? WHERE User_Name = ?", (general.viewer_objects[viewer]
                                                                                     .join_message_check, viewer))
            general.viewer_objects[viewer].join_message_check = None
    conn.commit()
    conn.close()


def check_if_user_exists(get_viewers):
        if get_viewers is not None:
            conn = sqlite3.connect(new_sql_file())
            c = conn.cursor()
            all_users = c.execute('SELECT User_Name FROM ViewerData')
            user_list = all_users.fetchall()
            user_list = list(user_list)

            untupled_user_list = []
            for j in user_list:
                untupled_user_list.append(str(j[0]).lower())

            for i in get_viewers:
                if i not in untupled_user_list:
                    year_month_day = datetime.datetime.now().strftime('%Y-%m-%d')
                    year_month_day = str(year_month_day)
                    insert_user(User_Name=i, User_Type='Viewer',
                                Join_Date=year_month_day, game=current_game.game_name())
                    # can change this ^^ to be saved in viewer object
            conn.close()


def check_users_joindate(get_viewers):  # time based
    def get_user_id(username, client_id):
        try:
            # Construct headers for HTTP request
            headers = {"Client-ID": client_id}

            # Need user id for request
            personal_user_info = requests.get("https://api.twitch.tv/helix/users?login={}".format(username),
                                              headers=headers).json()

            # extract user id
            user_id = personal_user_info['data'][0]['id']
            return user_id
        except KeyError as e:
            #print(e, 470)
            pass

    def initial_follow_date_for(username, client_id):

        # Construct headers for HTTP request
        headers = {"Client-ID": client_id}

        user_id = get_user_id(username, client_id)

        # Find follower data for user by id
        try:
            follow_data = requests.get("https://api.twitch.tv/helix/users/follows?from_id={}&to_id={}"
                                       .format(user_id, get_user_id(encryption_key.decrypted_chan,
                                                                    client_id)), headers=headers).json()['data'][0]

            # extract the follow date
            date = follow_data['followed_at'].split("T")[0]

            # return dict of format name: follow date in form year-month-day
            return [str(e) for e in date.split('-')]

        except (IndexError, KeyError) as e:
            #print(e, 492)
            return False

    try:
        conn = sqlite3.connect(new_sql_file())
        c = conn.cursor()
        if get_viewers is not None:
            viewer_list = get_viewers
            if viewer_list is not None:
                for i in viewer_list:
                    sql_jdc = c.execute('SELECT Join_Date_Check FROM ViewerData WHERE User_Name = ?', (i.strip(),))
                    string_jdc = sql_jdc.fetchone()
                    if string_jdc[0] != 'x':
                        web_date = initial_follow_date_for(i.strip(), client_id=str('j82z1o73ha4tauoxb8y462udh8t4i2'))
                        if web_date is False:
                            c.execute('UPDATE ViewerData SET Join_Date_Check = "x" '
                                      'WHERE User_Name = ?', (i,))
                            conn.commit()
                        if web_date:
                            year_month_day = ['']

                            sql_users_joindate = c.execute("SELECT Join_Date FROM ViewerData WHERE User_Name = ?", (i,))
                            users_joindate = sql_users_joindate.fetchone()
                            if users_joindate is not None:
                                users_joindate = users_joindate[0]
                                str_yearnow = str(users_joindate)[0:4]
                                str_monthnow = str(users_joindate)[5:7]
                                str_daynow = str(users_joindate)[8:]
                                full_strnow = str(str_yearnow + '-' + str_monthnow + '-' + str_daynow)
                                full_webdate = str(web_date[0]) + '-' + str(web_date[1]) + '-' + str(web_date[2])

                                if full_strnow == full_webdate:
                                    c.execute('UPDATE ViewerData SET Join_Date_Check = "x" '
                                              'WHERE User_Name = ?', (i,))

                                else:
                                    yearnow = int(str_yearnow)
                                    monthnow = int(str_monthnow)
                                    daynow = int(str_daynow)

                                    if int(web_date[0]) < yearnow:
                                        year_month_day[0] = str(web_date[0]) + '-' + str(web_date[1]) + '-' + \
                                                            str(web_date[2])

                                    elif int(web_date[0]) == yearnow:
                                        if int(web_date[1]) < monthnow:
                                            year_month_day[0] = str(web_date[0]) + '-' + str(web_date[1]) + '-' + \
                                                                str(web_date[2])

                                    elif int(web_date[0]) == yearnow:
                                        if (web_date[1]) == monthnow:
                                            if int(web_date[2]) < daynow:
                                                year_month_day[0] = str(web_date[0]) + '-' + str(web_date[1]) \
                                                                    + '-' + str(web_date[2])

                                    else:
                                        year_month_day[0] = users_joindate

                                if users_joindate != year_month_day[0]:
                                    if year_month_day[0] != '':
                                        c.execute('UPDATE ViewerData SET Join_Date = ? WHERE User_Name = ?'
                                                  , (year_month_day[0], i))
                                        c.execute('UPDATE ViewerData SET Join_Date_Check = "x" '
                                                  'WHERE User_Name = ?', (i,))

                                elif users_joindate == year_month_day[0]:
                                    c.execute('UPDATE ViewerData SET Join_Date_Check = "x" WHERE User_Name=?', (i,))

                                elif web_date is None:
                                    c.execute('UPDATE ViewerData SET Join_Date_Check = "x" '
                                              'WHERE User_Name = ?', (i,))
        conn.commit()
        conn.close()
    except (sqlite3.OperationalError, TypeError) as e:
        pass
        #print(e, 566)


def check_mods(general):  # bots should be able to be mods
    #try:
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()

    sql_mod_list = c.execute("SELECT User_Name FROM ViewerData WHERE User_Type = 'Moderator'")
    fetchall_mod_list = sql_mod_list.fetchall()
    mod_list = []
    if fetchall_mod_list is None:
        if general.get_viewers_func[1]:
            mod_list.append(general.get_viewers_func[1])
    else:
        for i in fetchall_mod_list:
            mod_list.append(i[0])
        if general.get_viewers_func[1]:
            for i in general.get_viewers_func[1]:
                if i in mod_list:
                    pass
                else:
                    mod_list.append(i)
    for i in mod_list:
        sql_find_user = c.execute('SELECT User_Name FROM ViewerData WHERE User_Name = ?', (i,))
        user = sql_find_user.fetchall()
        if not user:
            pass
        else:
            if i == encryption_key.decrypted_chan.lower():
                c.execute("UPDATE ViewerData SET User_Type = 'Streamer' WHERE User_Name = ?", (i,))

            c.execute("UPDATE ViewerData SET User_Type = 'Moderator' WHERE User_Name = ?", (i,))

        if i not in general.get_viewers_func[1]:
            if i == "zerg3rr" or i == encryption_key.decrypted_chan:
                pass
            else:
                if i in general.get_viewers_func[0]:
                    c.execute("UPDATE ViewerData SET User_Type='Viewer' WHERE User_Name=?", (i,))

    conn.commit()
    conn.close()
    #except (TypeError, sqlite3.OperationalError) as e:
        #pass
        # print(e, 'Typerror or DB lock')


def get_uid_from_username(username):
    try:
        conn = sqlite3.connect(new_sql_file())
        c = conn.cursor()
        sql_uid = c.execute("SELECT UID FROM ViewerData WHERE User_Name=?", (username,))
        string_uid = sql_uid.fetchone()[0]
        #print(string_uid, username)
        conn.close()
        return string_uid
    except TypeError as e:
        #print(675, username, e)
        return False


def combine_db_data(general, username):
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()

    old_uid = general.viewer_objects[username].old_uid

    sql_new_uid = c.execute('SELECT UID FROM ViewerData WHERE User_Name=?', (username,))
    str_new_uid = sql_new_uid.fetchone()[0]

    sql_joindate = c.execute('SELECT Join_Date FROM ViewerData WHERE UID=?', (old_uid,))
    str_joindate = sql_joindate.fetchone()
    if str_joindate is not None:
        c.execute('UPDATE ViewerData SET Join_Date=? WHERE UID=?', (str_joindate[0], str_new_uid))

    sql_points = c.execute('SELECT Points FROM ViewerData WHERE UID=?', (old_uid,))
    str_points = sql_points.fetchone()
    c.execute('UPDATE ViewerData SET Points=Points+? WHERE UID=?', (str_points[0], str_new_uid))

    sql_invited_by = c.execute('SELECT Invited_By FROM ViewerData WHERE UID=?', (old_uid,))
    str_invited_by = sql_invited_by.fetchone()
    if str_invited_by is not None:
        c.execute('UPDATE ViewerData SET Invited_By=? WHERE UID=?', (str_invited_by[0], str_new_uid))

    sql_join_game = c.execute('SELECT Join_Game FROM ViewerData WHERE UID=?', (old_uid,))
    str_join_game = sql_join_game.fetchone()
    if str_join_game is not None:
        c.execute('UPDATE ViewerData SET Join_Game=? WHERE UID=?', (str_join_game[0], str_new_uid))

    sql_point_check = c.execute('SELECT Updating_Name_Point_Deduction FROM ViewerData WHERE UID=?', (old_uid,))
    str_join_game = sql_point_check.fetchone()
    if str_join_game is None:
        c.execute('UPDATE ViewerData SET Updating_Name_Point_Deduction=200 WHERE User_Name=?', (username,))
    else:
        c.execute('UPDATE ViewerData SET Updating_Name_Point_Deduction=Updating_Name_Point_Deduction*2 '
                  'WHERE User_Name=?', (username,))

    c.execute('DELETE FROM ViewerData WHERE UID=?', (old_uid,))

    c.execute('UPDATE Daily_Stats SET UID=? WHERE UID=?', (str_new_uid, old_uid))

    c.execute('UPDATE ViewerData SET Points=Points-Updating_Name_Point_Deduction WHERE UID=?', (str_new_uid,))

    general.viewer_objects[username].old_uid = 0

    conn.commit()
    conn.close()
