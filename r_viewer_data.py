import requests
import time

from urllib3 import Retry
from requests.adapters import HTTPAdapter

import encryption_key
import class_definition_and_manipulation
import sql_commands


def get_viewers(streamer_obj) -> list:
    """
    handles getting all viewers currently in the channel, should only be called once every 10.5
    minutes, calling earlier than that will lead to inaccurate results, due to not being a
    standard api point, sometimes goes down or is otherwise inaccurate
    """
    session = requests.Session()
    retry = Retry(connect=500, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        channel_json = session.get(url=(f"https://tmi.twitch.tv/group/user/"
                                        f"{streamer_obj}/chatters")).json()
        broadcaster = channel_json["chatters"]["broadcaster"]
        viewers = channel_json["chatters"]["viewers"]
        moderators = (channel_json['chatters']['moderators'])
        staff = (channel_json['chatters']['staff'])
        vips = (channel_json['chatters']['vips'])
        global_mods = (channel_json['chatters']['global_mods'])
        admins = (channel_json['chatters']['admins'])
        viewers_list = viewers + staff + vips + global_mods + admins
        viewers_and_mods = [viewers_list, moderators, broadcaster]
        return viewers_and_mods
    except TypeError as e:
        print(47, "viewer_data", e)
        return []


def create_viewers_query_url(streamer_obj) -> list:
    get_viewers_func_list = get_viewers(streamer_obj)

    if not get_viewers_func_list:
        return []
    else:
        urls_list = []
        viewers_list = get_viewers_func_list[0] + get_viewers_func_list[1] + get_viewers_func_list[2]
        num1 = 0
        num2 = 90
        num_viewers = len(viewers_list)

        for viewer in streamer_obj.viewer_objects:
            if streamer_obj.viewer_objects[viewer].twitch_id == 0:
                num_viewers += 1
                viewers_list.append(streamer_obj.viewer_objects[viewer].name)

        while num_viewers > 0:
            base_url = f"https://api.twitch.tv/helix/users?login="
            viewer_url_piece = "&login=".join(viewers_list[num1:num2])
            query_url = base_url + viewer_url_piece
            num1 = num2
            num2 += 90
            num_viewers -= 90
            urls_list.append(query_url)
        return urls_list


def get_viewer_info(streamer_obj, auth_token) -> dict:
    all_json_data = []
    all_viewer_data = {}

    for big_url in create_viewers_query_url(streamer_obj):
        headers = {"CLIENT-ID": encryption_key.client_id,
                   "Authorization": f"Bearer {auth_token}"}
        viewer_info = requests.get(big_url, headers=headers)
        all_json_data.append(viewer_info.json())
    for sublist in all_json_data:
        if 'data' not in sublist:
            print(all_json_data)
            print(81, "viewer_data", sublist)
        else:
            for viewer_data in sublist['data']:
                login_name = viewer_data["login"]
                display_name = viewer_data["display_name"]
                viewer_id = viewer_data["id"]
                all_viewer_data[login_name] = [display_name, viewer_id]
    if len(all_viewer_data) == 0:
        all_viewer_data = streamer_obj.old_viewer_info
        if len(all_viewer_data) == 0:
            return {}
    else:
        # dict key = login_name, values = [display_name, viewer_id]
        streamer_obj.old_viewer_data = all_viewer_data
        return all_viewer_data


def create_timer_objects(streamer_obj, viewer_name, timer, curr_time) -> None:
    """
    sends viewer object into streamer_obj[viewer_obj] dict as well setting up timers
    """

    viewer_object = streamer_obj.viewer_objects[viewer_name]
    viewer_object.join_time = curr_time
    viewer_object.timer_obj = timer()

    viewer_object.time_passed_obj = timer()

    class_definition_and_manipulation.set_active_viewer(viewer_object)


async def create_multiple_viewerobjects(viewer_info, streamer_obj, timer, curr_time) -> None:
    if viewer_info is not False:
        for viewer_name in viewer_info:
            if viewer_name not in streamer_obj.viewer_objects:
                create_viewer = class_definition_and_manipulation.Viewer(name=viewer_name.lower(),
                                                                         twitch_id=viewer_info[viewer_name][1])
                create_viewer.display_name = viewer_info[viewer_name][0]
                streamer_obj.viewer_objects[viewer_name] = create_viewer

                create_timer_objects(streamer_obj, viewer_name, timer, curr_time)


async def create_one_viewerobject(viewer_name, streamer_obj, timer, curr_time) -> None:
    if viewer_name not in streamer_obj.viewer_objects:
        create_viewer = class_definition_and_manipulation.Viewer(name=viewer_name, twitch_id=0)
        streamer_obj.viewer_objects[viewer_name] = create_viewer
        create_timer_objects(streamer_obj, viewer_name, timer, curr_time)


async def check_active_viewers(streamer_obj, viewer_info) -> None:
    """
    first look at the time that they have joined the stream
    next look at their last chat message
        go into each game and check last chat message for all games
    if they have not sent a message within 10 minutes of either of these events
        begin inactive time in stream dict AFTER adding those 10 minutes as active stream time
    else
        keep adding time to inactive time stream dict

    need to check if game id == -1, if it does then we stop saving data and write whatever is left
    """

    if streamer_obj.game_id != -1:

        def if_game_in_seconds_dict(viewer_obj_dict_name):
            if streamer_obj.game_name not in viewer_obj_dict_name:
                viewer_obj_dict_name[streamer_obj.game_name] = viewer_obj.timer_obj.total_time_diff
                save_honor(seconds=viewer_obj.timer_obj.total_time_diff,
                           seconds_type=viewer_obj_dict_name,
                           viewer_obj=viewer_obj)
            else:
                viewer_obj_dict_name[streamer_obj.game_name] += viewer_obj.timer_obj.total_time_diff
                save_honor(seconds=viewer_obj.timer_obj.total_time_diff,
                           seconds_type=viewer_obj_dict_name,
                           viewer_obj=viewer_obj)
            viewer_obj.timer_obj.total_time_diff = 0

        for viewer in streamer_obj.viewer_objects:
            most_recent_message_time = None
            viewer_obj = streamer_obj.viewer_objects[viewer]

            for game in viewer_obj.chat:
                for sublist in range(len(viewer_obj.chat[game])):
                    """
                    if we haven't started our list set message to last message of first game in list
                    bug here
                    """
                    if most_recent_message_time is None or most_recent_message_time < viewer_obj.chat[game][sublist][0]:
                        most_recent_message_time = viewer_obj.chat[game][sublist][0]

            """
            if they have not sent a message (meaning it's none) and the active timer toggle is true 
            then add their time to active and turn off active viewer since they have not sent any messages
            """
            if most_recent_message_time is None:
                viewer_obj.timer_obj.stop_and_add_times(end_time=time.time())
                viewer_obj.time_passed_obj.stop_and_add_times(end_time=time.time())
                if viewer_obj.active_viewer:
                    if_game_in_seconds_dict(viewer_obj.active_seconds_per_game)

                    if viewer_obj.time_passed_obj.total_time_diff > 150:
                        class_definition_and_manipulation.set_inactive_viewer(viewer_obj)

                elif viewer_obj.active_viewer is False:
                    if_game_in_seconds_dict(viewer_obj.inactive_seconds_per_game)

            else:
                """
                look at time of last message, and get difference from current time, add those last 10 minutes to active 
                viewer dict then switch toggle off until they leave (toggle None) or send another message (toggle true)
                -
                will need to reset timer again in handle chat messages when they begin talking again
                -
                If they send another message, get time between last two messages and add that time to active dict for 
                most recent game. 
                This means that now if they stop messaging it will instead grab that time once 10 min has elapsed
                
                timestamp() converts from datetime object to epoch seconds float
                """

                viewer_obj.timer_obj.stop_and_add_times(end_time=time.time())
                viewer_obj.time_passed_obj.stop_and_add_times(end_time=time.time())

                if (int(most_recent_message_time.timestamp()) + viewer_obj.time_passed_obj.total_time_diff) > \
                        (most_recent_message_time.timestamp() + 300):
                        class_definition_and_manipulation.set_inactive_viewer(viewer_obj)

                elif viewer_obj.active_viewer:
                    if_game_in_seconds_dict(viewer_obj.active_seconds_per_game)

                elif viewer_obj.active_viewer is False:
                    if_game_in_seconds_dict(viewer_obj.inactive_seconds_per_game)

            if viewer not in streamer_obj.old_viewer_info and viewer not in viewer_info:
                viewer_obj.timer_obj.stop_and_add_times(end_time=time.time())
                if viewer_obj.active_viewer is True:
                    if_game_in_seconds_dict(viewer_obj.active_seconds_per_game)
                else:
                    if_game_in_seconds_dict(viewer_obj.inactive_seconds_per_game)
                viewer_obj.active_viewer = None


def no_data_check(streamer_obj, streamer_id):
    for viewer in streamer_obj.viewer_objects:

        """
        chat is reset in sql_commands to - viewer_obj.chat[game] = []
        shouldn't update anymore once game is set to = "" in main.destroy_streamer_obj
        stops collecting messages in main.handle_chat_message once game is set to = ""
        """
        for game in streamer_obj.viewer_objects[viewer].chat:
            if len(streamer_obj.viewer_objects[viewer].chat[game]) != 0:
                print(f"223, viewer_data, streamer_name={streamer_obj.name}, "
                      f"streamer_id={streamer_obj.twitch_id}, "
                      f"viewer_name={streamer_obj.viewer_objects[viewer].name}, "
                      f"viewer_id={streamer_obj.viewer_objects[viewer].twitch_id}")
                print(227, "viewer_data", streamer_obj.viewer_objects[viewer].chat)
                print(228, "viewer_data", streamer_obj.viewer_objects[viewer].chat[game])
                return True

        """
        viewer_data.check_active_viewers will stop saving time if game is set to = ""
        """
        for game in streamer_obj.viewer_objects[viewer].active_seconds_per_game:
            if streamer_obj.viewer_objects[viewer].active_seconds_per_game[game] != 0:
                print(f"236, viewer_data, streamer_name={streamer_obj.name}, "
                      f"streamer_id={streamer_obj.twitch_id}, "
                      f"viewer_name={streamer_obj.viewer_objects[viewer].name}, "
                      f"viewer_id={streamer_obj.viewer_objects[viewer].twitch_id}")
                print(240, "viewer_data", streamer_obj.viewer_objects[viewer].active_seconds_per_game)
                print(241, "viewer_data", streamer_obj.viewer_objects[viewer].active_seconds_per_game[game])
                return True

        for game in streamer_obj.viewer_objects[viewer].inactive_seconds_per_game:
            if streamer_obj.viewer_objects[viewer].inactive_seconds_per_game[game] != 0:
                print(f"246, viewer_data, streamer_name={streamer_obj.name}, "
                      f"streamer_id={streamer_obj.twitch_id}, "
                      f"viewer_name={streamer_obj.viewer_objects[viewer].name}, "
                      f"viewer_id={streamer_obj.viewer_objects[viewer].twitch_id}")
                print(250, "viewer_data", streamer_obj.viewer_objects[viewer].inactive_seconds_per_game)
                print(251, "viewer_data", streamer_obj.viewer_objects[viewer].inactive_seconds_per_game[game])
                return True

        """
        need this in case a user joined between the 30 second period between stream going offline and check for new 
        users, so we hold onto this until we are sure that every id is accounted for
        """
        viewer_ids = sql_commands.get_viewer_ids_per_streamer(streamer_id)
        temp_list = []
        for i in viewer_ids:
            temp_list.append(int(i[0]))
        if int(streamer_obj.viewer_objects[viewer].twitch_id.strip()) not in temp_list:
            print(f"263, viewer_data, streamer_name={streamer_obj.name}, "
                  f"streamer_id={streamer_obj.twitch_id}, "
                  f"viewer_name={streamer_obj.viewer_objects[viewer].name}, "
                  f"viewer_id={streamer_obj.viewer_objects[viewer].twitch_id}")
            print(267, "viewer_data", viewer_ids)
            print(268, "viewer_data", streamer_obj.viewer_objects[viewer].twitch_id)
            return True

    return False


def get_follow_date(viewer_id, streamer_id, auth_token):
    headers = {"CLIENT-ID": encryption_key.client_id,
               "Authorization": f"Bearer {auth_token}"}
    url = f"https://api.twitch.tv/helix/users/follows?from_id={viewer_id}&to_id={streamer_id}"
    follow_date = requests.get(url, headers=headers).json()
    # example output is -
    # {'total': 1, 'data':
    # [{'from_id': '441100979', 'from_name': 'SPACEAMBULANCE', 'to_id': '77894502',
    #   'to_name': 'booooooooooooooooooOm', 'followed_at': '2020-07-21T07:12:30Z'}], 'pagination': {}}
    if follow_date['total'] == 1:
        return follow_date['data'][0]['followed_at'].split("T")[0]
    else:
        return None


def create_query_follow_url(streamer_obj):
    urls_list = []
    viewer_ids_list = []
    num1 = 0
    num2 = 90
    num_viewers = len(viewer_ids_list)

    for viewer in streamer_obj.viewer_objects:
        if streamer_obj.viewer_objects[viewer].follow_check is False:
            num_viewers += 1
            viewer_id = streamer_obj.viewer_objects[viewer].twitch_id
            viewer_ids_list.append(viewer_id)
            streamer_obj.viewer_objects[viewer].follow_check = True

    while num_viewers > 0:

        base_url = f"https://api.twitch.tv/helix/users?follows="
        temp_url_string = ""
        count = 0
        for i in range(num1, num2):
            if i >= num_viewers-1:
                break
            else:
                viewer_id_num = viewer_ids_list[i]
                if count == 0:
                    temp_url_string += f"from_id={viewer_id_num}&to_id={streamer_obj.twitch_id}"
                else:
                    temp_url_string += f"&from_id={viewer_id_num}&to_id={streamer_obj.twitch_id}"
            count += 1
        query_url = base_url + temp_url_string
        num1 = num2
        num2 += 90
        num_viewers -= 90
        print(333, "viewer_data", query_url)
        urls_list.append(query_url)
    return urls_list


def get_follow_info(streamer_obj, auth_token):
    all_json_data = []

    for big_url in create_query_follow_url(streamer_obj):
        headers = {"CLIENT-ID": encryption_key.client_id,
                   "Authorization": f"Bearer {auth_token}"}
        follow_info = requests.get(big_url, headers=headers)
        print(345, "viewer_data", follow_info)
        if follow_info is None:
            pass
        else:
            all_json_data.append(follow_info.json())
    for sublist in all_json_data:
        for follow_data in sublist['data']:
            follow_date = follow_data[0]['followed_at'].split("T")[0]
            viewer_name = follow_data[0]['from_name'.lower()]
            # follow date check is done when they are initially added to the big link
            streamer_obj.viewer_objects[viewer_name].follow_date = follow_date


def save_honor(seconds, seconds_type, viewer_obj):
    if seconds_type == viewer_obj.active_seconds_per_game:
        multiplier = .03
    else:
        multiplier = .01
    if seconds != 0:
        viewer_obj.honor += round((seconds * multiplier), 3)
        # print(362, f"{viewer_obj.name}: {viewer_obj.honor}")
