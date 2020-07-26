import encryption_key
import requests


def create_stream_query_url(list_of_streamers) -> list:
    urls_list = []
    try:
        num1 = 0
        num2 = 90

        num_streamers = len(list_of_streamers)

        while num_streamers > 0:
            base_url = f'https://api.twitch.tv/helix/streams?user_login='
            streamers_string_url = "&user_login=".join(list_of_streamers[num1:num2])
            query_url = base_url + streamers_string_url

            num1 = num2
            num2 += 90
            num_streamers -= 90
            urls_list.append(query_url)

        return urls_list
    except Exception as e:
        print(25, "get_streamers_game", e)
        print(26, "get_streamers_game", urls_list)


def twitch_down_check(all_json_data) -> None:
    for i in all_json_data:
        if "error" in i:
            print(77, "get_streamers_game", i)


def get_streamers_online(list_of_streamers, auth_token) -> list:
    all_json_data = []
    try:
        for big_url in create_stream_query_url(list_of_streamers):
            headers = {"CLIENT-ID": encryption_key.client_id,
                       "Authorization": f"Bearer {auth_token}"}
            stream_info = requests.get(big_url, headers=headers)
            all_json_data.append(stream_info.json())
        twitch_down_check(all_json_data)
        return all_json_data

    # lost internet connection OR couldn't connect to twitch api (too many requests?)
    except (ConnectionError, requests.exceptions.ConnectionError) as e:
        print(f"48, get_streamers_game: \n {e}")
        return all_json_data


def create_game_query_url(live_streamers) -> list:
    urls_list = []
    num1 = 0
    num2 = 90
    game_ids_list = []

    for streamer in live_streamers:
        if live_streamers[streamer.lower()].game_id not in game_ids_list:
            game_ids_list.append(str(live_streamers[streamer].game_id))
            """
            wrapped this in str to attempt to fix this error
              File "E:/Programming/projects/Python/twitchbot_refactor/main.py", line 316, in main
                auth_token=auth_class_object.app_access_token)
              File "E:/Programming/projects/Python/twitchbot_refactor/main.py", line 270, in assign_game_to_user
                live_streamers=live_streamers_dict)
              File "E:\Programming\projects\Python\twitchbot_refactor\get_streamers_game.py", line 75, in get_game_ids
                for big_url in create_game_query_url(live_streamers):
              File "E:\Programming\projects\Python\twitchbot_refactor\get_streamers_game.py", line 62, in 
              create_game_query_url
                game_string_url = "&id=".join(game_ids_list[num1:num2])
            TypeError: sequence item 2: expected str instance, int found
            """

    num_game_ids = len(game_ids_list)

    while num_game_ids > 0:
        base_url = f'https://api.twitch.tv/helix/games?id='
        game_string_url = "&id=".join(game_ids_list[num1:num2])
        query_url = base_url + game_string_url
        num1 = num2
        num2 += 90
        num_game_ids -= 90
        urls_list.append(query_url)
    return urls_list


def get_game_ids(auth_token, live_streamers) -> dict:
    all_json_data = []

    try:
        for big_url in create_game_query_url(live_streamers):

            headers = {"CLIENT-ID": encryption_key.client_id,
                       "Authorization": f"Bearer {auth_token}"}

            game_info = requests.get(big_url, headers=headers)
            all_json_data.append(game_info.json())
        game_data_dict = {}

        for sublist in all_json_data:
            for game_data in sublist['data']:
                game_id = game_data["id"]
                game_name = game_data["name"].replace(' ', '')
                game_data_dict[game_id] = game_name
        return game_data_dict
    except (requests.exceptions.ConnectionError, ConnectionError) as e:
        print(108, "get_streamers_game", e)
        return {}

