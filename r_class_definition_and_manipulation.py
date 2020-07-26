import encryption_key
import requests
import json
import time


class Viewer:
    def __init__(self, name: str, twitch_id: int):
        self.name = name.lower()  # login name, ascii text name only
        self.twitch_id = twitch_id
        self.join_time = None
        self.active_viewer = None
        self.display_name = str
        self.honor = 0  # .02 honor per second = 1.2 hour per minute = 72 per hour = 7200 per 100 hours
        self.trivia_answered = int
        self.followed_date = False  # date, false (if not checked yet), or None if not followed, otherwise date
        self.follow_check = False

        """
        save game seconds in timer obj
        """
        self.active_seconds_per_game = {}  # key = game, values = seconds, Timer object from main
        self.inactive_seconds_per_game = {}  # key = game, values = seconds, Timer object from main
        self.chat = {}  # key = game, values = [formatted_time(), message]
        self.bits_donated = 0

        """
        There are two separate timers here because we want to consistently keep adding time to dicts which the timer_obj
        allows us to do, however this forces us to reset the timer due to the intricacies of how saving time to the 
        dicts works, as a result we need a second timer object simply for keeping track of time passed while the other 
        can save the data
        """
        self.timer_obj = None  # this exists to actually add our times together
        self.time_passed_obj = None  # this exists to keep track of our timers
        self.last_message_time = None

    def __str__(self) -> str:
        return self.name.lower()


def set_active_viewer(viewer_obj) -> None:
    viewer_obj.timer_obj.set_start_time()
    viewer_obj.active_viewer = True
    viewer_obj.time_passed_obj.set_start_time()


def set_inactive_viewer(viewer_obj) -> None:
    viewer_obj.timer_obj.total_time_diff = 0
    viewer_obj.active_viewer = False
    viewer_obj.time_passed_obj.total_time_diff = 0


class StreamerObj(Viewer):
    """
    basic class for streamer
    """
    def __init__(self, name, twitch_id, game_id):
        super(StreamerObj, self).__init__(name, twitch_id)
        self.game_id = game_id
        self.game_name = str

        self.viewer_objects = {}
        self.old_viewer_info = {}

        # self.async_task = None

        self.stream_socket_writer = None  # keeps a socket connection object for writing and reading
        self.stream_socket_reader = None
        self.timer_obj = Timer()  # this is needed to see how long since the last ping/message from twitch


async def close_connection(streamer_obj):
    """
    close socket connection for streamer
    """
    streamer_obj.stream_socket_writer.close()
    await streamer_obj.stream_socket_writer.wait_closed()
    streamer_obj.stream_socket_writer = None
    streamer_obj.stream_socket_reader = None


class Timer:
    def __init__(self):
        self.start_time = None
        self.total_time_diff = 0

    def stop_and_add_times(self, end_time) -> None:
        # end time is time.time()
        full_time = int((end_time - self.start_time))
        self.total_time_diff += full_time
        self.set_start_time()

    def set_start_time(self) -> None:
        self.start_time = time.time()


class TwitchData:
    def __init__(self):
        self.app_access_token = [str]
        self.refresh_timer = None
        self.refresh_token = None
        self.app_access_token_json_data = str
        self.current_time = None

    def get_access_token(self):
        """
        put this on a timer, 1 hour? so that time doesn't run out
        """
        get_app_access_token = requests.post(f"https://id.twitch.tv/oauth2/token?client_id="
                                             f"{encryption_key.client_id}&client_secret="
                                             f"{encryption_key.client_secret}&"
                                             f"grant_type=client_credentials")
        self.app_access_token_json_data = json.loads(get_app_access_token.text)

        self.app_access_token = self.app_access_token_json_data["access_token"]
        self.refresh_timer = self.app_access_token_json_data["expires_in"]
        self.current_time = time.time()

        """ there is no refreshing for APP ACCESS TOKEN 
        https://discuss.dev.twitch.tv/t/response-not-contains-refresh-token/21978
        # self.refresh_token = int(app_access_token_json_data["refresh_token"])

    def refresh_access_token(self, refresh):
        if self.refresh_token < 100 or refresh is True:
            requests.post(f"https://id.twitch.tv/oauth2/token--data-urlencode"
                          f"?grant_type=refresh_token"
                          f"&refresh_token={self.refresh_token}"
                          f"&client_id={encryption_key.client_id}"
                          f"&client_secret={encryption_key.client_secret}")
                          """

    def check_access_token(self) -> None:
        print(32, self.app_access_token_json_data)
        print(33, self.app_access_token)
        print(34, self.refresh_timer)
