"""
Create new database with ViewerData, Hours, and viewer_chat tables

In ViewerData table we need to have these columns
UID, User_Name, User_Type, Honor, Join_Message, Join_Date_Check, Points, Last_Seen, Invited_By, Join_Game,
Updating_Name_Point_Deduction, Trivia_Answers

In Hours we need to have these columns
UID, Game, Day, Hours, Chat


In viewer_chat we need to have these columns
MessageNum, UID, Date, Time, Message, Game

"""

import sqlite3

from twitchbot import encryption_key


def new_sql_file():
    sqlite_file = r'MyFiles\ViewerData2_' + encryption_key.decrypted_chan + '.sqlite'
    return sqlite_file


def sql_file():
    sqlite_file = r'MyFiles\ViewerData_' + encryption_key.decrypted_chan + '.sqlite'
    return sqlite_file


def hours_file():
    hrs_file = r'MyFiles\hours_' + encryption_key.decrypted_chan + '.sqlite'
    return hrs_file


def copy_viewerdata():
    conn1 = sqlite3.connect(new_sql_file())
    conn2 = sqlite3.connect(sql_file())
    c1 = conn1.cursor()
    c2 = conn2.cursor()
    sql_uids = c2.execute("SELECT UID FROM ViewerData")
    str_uids = sql_uids.fetchall()
    for uid in str_uids:
        sql_username = c2.execute("SELECT User_Name FROM ViewerData WHERE UID=?", (uid[0],))
        str_username = sql_username.fetchone()[0]

        sql_usertype = c2.execute("SELECT User_Type FROM ViewerData WHERE UID=?", (uid[0],))
        str_usertype = sql_usertype.fetchone()[0]

        sql_honor = c2.execute("SELECT Level FROM ViewerData WHERE UID=?", (uid[0],))
        str_honor = sql_honor.fetchone()
        if str_honor[0] is None or str_honor is None:
            str_honor = 0
        else:
            str_honor = str_honor[0]

        sql_join_message = c2.execute("SELECT Join_Message FROM ViewerData WHERE UID=?", (uid[0],))
        str_join_message = sql_join_message.fetchone()
        if str_join_message[0] is None or str_join_message is None:
            str_join_message = None
        else:
            str_join_message = str_join_message[0]

        sql_join_date = c2.execute("SELECT Join_Date FROM ViewerData WHERE UID=?", (uid[0],))
        str_join_date = sql_join_date.fetchone()[0]

        sql_join_date_check = c2.execute("SELECT Join_Date_Check FROM ViewerData WHERE UID=?", (uid[0],))
        str_join_date_check = sql_join_date_check.fetchone()
        if str_join_date_check[0] is None or str_join_date_check is None:
            str_join_date_check = None
        else:
            str_join_date_check = str_join_date_check[0]

        sql_points = c2.execute("SELECT Points FROM ViewerData WHERE UID=?", (uid[0],))
        str_points = sql_points.fetchone()[0]

        sql_last_seen = c2.execute("SELECT Last_Seen FROM ViewerData WHERE UID=?", (uid[0],))
        str_last_seen = sql_last_seen.fetchone()
        if str_last_seen[0] is None or str_last_seen is None:
            str_last_seen = None
        else:
            str_last_seen = str_last_seen[0]

        sql_invited_by = c2.execute("SELECT Invited_By FROM ViewerData WHERE UID=?", (uid[0],))
        str_invited_by = sql_invited_by.fetchone()
        if str_invited_by[0] is None or str_invited_by is None:
            str_invited_by = None
        else:
            str_invited_by = str_invited_by[0]

        sql_join_game = c2.execute("SELECT Join_Game FROM ViewerData WHERE UID=?", (uid[0],))
        str_join_game = sql_join_game.fetchone()
        if str_join_game[0] is None or str_join_game is None:
            str_join_game = None
        else:
            str_join_game = str_join_game[0]

        #sql_user_check = c1.execute("SELECT User_Name FROM ViewerData WHERE UID=?", (uid[0],))
        #str_user_check = sql_user_check.fetchone()
        if str(uid[0]) == '12358132':
            c1.execute('UPDATE ViewerData '
                       'SET Honor=?, Join_Message=?, Points=?, Last_Seen=?, Invited_By=?, Join_Game=?'
                       'WHERE UID=?', (str_honor,
                                       str_join_message,
                                       str_points,
                                       str_last_seen,
                                       str_invited_by,
                                       str_join_game,
                                       uid[0]))
        else:
            c1.execute('INSERT INTO ViewerData(UID, User_Name, User_Type, Honor, Join_Message, Join_Date, '
                       'Join_Date_Check, Points, Last_Seen, Invited_By, Join_Game) '
                       'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (uid[0],
                                                                   str_username,
                                                                   str_usertype,
                                                                   str_honor,
                                                                   str_join_message,
                                                                   str_join_date,
                                                                   str_join_date_check,
                                                                   str_points,
                                                                   str_last_seen,
                                                                   str_invited_by,
                                                                   str_join_game))
    conn1.commit()
    conn1.close()
    conn2.close()


def copy_hoursdata():
    conn1 = sqlite3.connect(new_sql_file())
    c1 = conn1.cursor()
    conn2 = sqlite3.connect(hours_file())
    c2 = conn2.cursor()
    sql_all_hours_data = c2.execute("SELECT * FROM Hours")
    str_all_hours_data = sql_all_hours_data.fetchall()
    for item in str_all_hours_data:
        #print(229, item)
        uid = item[0]
        game = item[1]
        date = item[2]
        seconds = item[3]
        chat = item[4]
        if chat is None:
            chat = 0
        sql_entry_number = c1.execute("SELECT MAX(Entry_Number) FROM Daily_Stats")
        str_entry_number = sql_entry_number.fetchone()
        if str_entry_number[0] is None:
            str_entry_number = 1
        else:
            str_entry_number = str_entry_number[0] + 1
        c1.execute("INSERT INTO Daily_Stats (Entry_Number, UID, Game, Date, Seconds, Chat) "
                   "VALUES(?, ?, ?, ?, ?, ?)", (str_entry_number, uid, game, date, seconds, chat))

    sql_all_viewer_chat_data = c2.execute("SELECT * FROM viewer_chat")
    str_all_viewer_chat_data = sql_all_viewer_chat_data.fetchall()
    for item in str_all_viewer_chat_data:
        #print(249, item)
        MessageNum = item[0]
        UID = item[1]
        Date = item[2]
        Time = item[3]
        Message = item[4]
        Game = item[5]
        c1.execute("INSERT INTO viewer_chat (MessageNum, UID, Date, Time, Message, Game) "
                   "VALUES(?, ?, ?, ?, ?, ?)", (MessageNum, UID, Date, Time, Message, Game))

    conn1.commit()
    conn1.close()
    conn2.close()
