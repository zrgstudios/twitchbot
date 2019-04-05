from twitchbot import encryption_key
import requests
import re


class OldGameName:
    oldgamename = "GameNotFound"


Game = OldGameName()


def json_info():
    stream_info = requests.get(encryption_key.decrypted_api)
    json_data = stream_info.json()
    json_data = str(json_data)
    return json_data


def game_name():
    try:
        gameregex1 = re.search(r"('game':(.*?),)", json_info())
        gameregex1 = gameregex1.group(0)
        gameregex2 = re.search(r"(:(.*?)(.*)')", gameregex1)
        game = str(gameregex2.group(0))
        game = game.replace(": '", "")
        game = game.replace("'", "")
        game = game.replace(' ', '')
        Game.oldgamename = game
        if game != "GameNotFound":
            return game
    except AttributeError:
        return 'Offline'
    except ValueError:
        return Game
