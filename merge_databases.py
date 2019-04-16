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
import encryption_key


def new_sql_file():
    sqlite_file = r'MyFiles\New_ViewerData_' + encryption_key.decrypted_chan + '.sqlite'
    return sqlite_file


def sql_file():
    sqlite_file = r'MyFiles\ViewerData_' + encryption_key.decrypted_chan + '.sqlite'
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

    """table = 'Daily_Stats'  # this gives error
    col10 = 'UID'
    col20 = 'Game'
    col30 = 'Day'
    col40 = 'Seconds'
    col50 = 'Chat'
    col60 = 'Number'
    str_type = 'STRING'
    int_type = 'INTEGER'
    c.execute("CREATE TABLE {table_name}("
              "{nf60} {ft60} PRIMARY KEY"
              "{nf10} {ft10},"
              "{nf20} {ft20},"
              "{nf30} {ft30},"
              "{nf40} {ft40},"
              "{nf50} {ft50})".format(table_name=table,
                                    nf60=col60, ft60=int_type,
                                    nf10=col10, ft10=int_type,
                                    nf20=col20, ft20=str_type,
                                    nf30=col30, ft30=str_type,
                                    nf40=col40, ft40=int_type,
                                    nf50=col50, ft50=int_type))"""

    c.execute("CREATE TABLE Daily_Stats (Number INTEGER PRIMARY KEY, UID INTEGER, Game STRING, Day STRING, "
              "Seconds INTEGER, Chat INTEGER)")

    c.execute("CREATE TABLE viewer_chat (MessageNum INTEGER PRIMARY KEY, UID INTEGER, Date STRING, "
              "Time STRING, Message STRING, Game STRING)")

    conn.commit()
    conn.close()


def get_table_columns():  # startup
    conn = sqlite3.connect(new_sql_file())
    c = conn.cursor()
    sql_column_list = c.execute("PRAGMA table_info(ViewerData)")
    string_column_list = sql_column_list.fetchall()
    columns = []
    for i in string_column_list:
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


def copy_data():
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


create_viewer_tables()
get_table_columns()
copy_data()
