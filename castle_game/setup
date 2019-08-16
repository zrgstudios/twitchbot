"""def startup():
    Viewer.username = name  # this will be handled when receiving the whisper
    castle_name = input('What would you like your castle name to be? \n')
    Castle.castle_name = castle_name
    print(castle_name)
    print(str(Viewer.username) + ' your castles name is ' + str(castle_name))
    return_list = [name, castle_name]
    print(return_list)
    return return_list"""


"""
def view_inp():
    startup_list = startup()
    name = startup_list[0]
    Viewer.username = name
    Viewer.username = Castle(
        castle_name='',
        points=5,
        walls=0,
        moat=0,
        bridge=0,
        archers=0
    )
    points = Viewer.username.points

    print('You can spend ' + str(points) + ' points on one of the listed items')
    print(attributes_list)

    spend_points = input('How would you like to spend your points? You have ' + str(points) +
                         ' points (type "choice #") \n')

    if Viewer.username.points > 0:
        spend_points_list = spend_points.split()
        while spend_points_list[0] not in attributes_list:
            print('Please enter a valid input')
            spend_points = input('How would you like to spend your points? You have ' + str(points) +
                                 ' points (type "choice #") \n')

        while not spend_points_list[1].isdigit():
            print('Please enter a number in your second portion (separated by a space)')

        spend_points_list = spend_points.split()
        new_value = ''
        if 'walls' in spend_points_list[0]:
            Viewer.username.walls = Viewer.username.walls + int(spend_points_list[1])
            new_value = Viewer.username.walls
        if 'moat' in spend_points_list[0]:
            Viewer.username.moat = Viewer.username.moat + int(spend_points_list[1])
            new_value = Viewer.username.moat
        if 'bridge' in spend_points_list[0]:
            Viewer.username.bridge = Viewer.username.bridge + int(spend_points_list[1])
            new_value = Viewer.username.bridge
        if 'archers' in spend_points_list[0]:
            Viewer.username.archers = Viewer.username.archers + int(spend_points_list[1])
            new_value = Viewer.username.archers
        Viewer.username.points = Viewer.username.points - int(spend_points_list[1])

        for i in attributes_list:
            if i in spend_points:
                print('You have upgraded your %s to value ' % (spend_points_list[0],) + str(new_value))
                print('Your remaining points are ' + str(Viewer.username.points))

    our_list = [str(startup_list[0]), str(startup_list[1]), str(Viewer.username.points),
                str(Viewer.username.walls), str(Viewer.username.moat), str(Viewer.username.bridge),
                str(Viewer.username.archers)]
    print(our_list)
    return our_list
"""

import sqlite3
import os
# from twitchbot import MyFiles

sqlite_file = r"C:\Programming\PycharmProjects\twitchbot\MyFiles\testfile.sqlite"


def create_table():
    table1 = 'castle_data'
    column1 = 'UID'
    column2 = 'Castle_Name'
    column3 = 'Points'
    column4 = 'Walls'
    column5 = 'Moat'
    column6 = 'Bridge'
    column7 = 'Archers'
    str_type = 'STRING'
    int_type = 'INTEGER'

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('CREATE TABLE {tn}( '
              '{nf1} {ft1} PRIMARY KEY, '
              '{nf2} {ft2}, '
              '{nf3} {ft3}, '
              '{nf4} {ft4}, '
              '{nf5} {ft5}, '
              '{nf6} {ft6}, '
              '{nf7} {ft7})'.format(tn=table1,
                                    nf1=column1, ft1=int_type,
                                    nf2=column2, ft2=str_type,
                                    nf3=column3, ft3=int_type,
                                    nf4=column4, ft4=int_type,
                                    nf5=column5, ft5=int_type,
                                    nf6=column6, ft6=int_type,
                                    nf7=column7, ft7=int_type))

    conn = sqlite3.connect(sqlite_file)
    conn.execute('INSERT INTO castle_data({nf1}, {nf2}, {nf3}, {nf4}, {nf5}, {nf6}, {nf7})'
                 'VALUES(?, ?, ?, ?, ?, ?, ?)'.format(nf1=column1, nf2=column2, nf3=column3, nf4=column4,
                                                      nf5=column5, nf6=column6, nf7=column7),
                 ('1000001', 'Hello_World', '5', '5', '5', '5', '5'))
    conn.commit()
    conn.close()


def get_table_names():
    table_name = 'castle_data'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('PRAGMA TABLE_INFO({})'.format(table_name))
    names = [tup[1] for tup in c.fetchall()]
    print(names)
    conn.close()


"""
def insert_user():
    #castle_list = view_inp()
    conn = sqlite3.connect(sqlite_file)

    last_id = conn.execute('SELECT MAX(UID) FROM castle_data')  # this should get the users ID from main file
    largest_id = last_id.fetchone()
    plus_one = largest_id[0] + 1

    conn.execute('INSERT INTO castle_data(UID, User_Name, Castle_Name, Points, Walls, Moat, Bridge, Archers)'
                 'VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                 (str(plus_one), castle_list[0], castle_list[1], castle_list[2], castle_list[3], castle_list[4],
                  castle_list[5], castle_list[6]))

    conn.commit()
    conn.close()
    """


def main():

    def check_if_file_exists():
        if not os.path.exists(sqlite_file):
            create_table()

    """def check_if_user_exists():
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()

        row = c.execute('SELECT User_Name FROM castle_data')
        data = row.fetchall()
        data = list(data)

        name = view_inp()[0]

        for i in data:
            if i[0] == name:
                print('\nUser ' + i[0] + ' exists!\n')
                break
            if i[0] not in data:
                insert_user()

        conn.close()"""

    def update_user():
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        c.execute("UPDATE castle_data SET Archers=('1000') WHERE User_Name = 'Gotdott'")
        conn.commit()
        conn.close()

    #update_user()

    check_if_file_exists()
    #check_if_user_exists()


main()

# next up is to create database file, and populate it with entered data,
# then grab that data to upgrade values again
"""
column1 = 'UID'
column2 = 'User_Name'
column3 = 'User_Type'
column4 = 'Level'
column5 = 'Points'
column6 = 'Online_Total_Hours'
column7 = 'Online_Monthly_Hours'
column8 = 'Online_Weekly_Hours'
column9 = 'Offline_Total_Hours'
column10 = 'Online_Total_Chat_Lines'
column11 = 'Online_Monthly_Chat_Lines'
column12 = 'Online_Weekly_Chat_Lines'
column13 = 'Offline_Total_Chat_Lines'
column14 = 'Join_Message'
column15 = 'Join_Date'
"""
