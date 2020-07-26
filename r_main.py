import datetime
import re
import asyncio
import time

import get_streamers_game
import viewer_data
import encryption_key
import class_definition_and_manipulation
import sql_commands


def formatted_time() -> datetime.datetime:
    """
    returns a time object for current time, used in multiple functions
    """
    return datetime.datetime.now()


async def async_connect_socket(streamer_obj: class_definition_and_manipulation.StreamerObj) -> None:
    """
    set a reader and writer (async) per streamer and do the equivalent of socket.send to
    twitch.tv, store reader and writer to class object
    """
    reader, writer = await asyncio.open_connection(encryption_key.cfg_host,
                                                   int(encryption_key.cfg_port))

    writer.write(f'CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n'.encode('utf-8'))
    print(f"Connecting to socket for {streamer_obj.name}")

    writer.write("PASS {}\r\n".format(encryption_key.decrypted_pass).encode('utf-8'))  # password
    writer.write("NICK #zerg3rrbot\r\n".encode('utf-8'))  # bot name
    writer.write(f"JOIN #{streamer_obj.name}\r\n".encode('utf-8'))

    await writer.drain()
    streamer_obj.stream_socket_writer = writer
    streamer_obj.stream_socket_reader = reader


async def parse_whisper(response: str, username_regex) -> list:

        whisper_regex = re.search(r"(?<=WHISPER )(.*)", response).group(0)
        whisper = re.search(r"(?<= :)(.*)", whisper_regex).group(0)
        username = username_regex.search(response)

        print(f"WHISPER - ({formatted_time().hour}:{formatted_time().second}) {username} : "
              f"{whisper}")
        return [username, whisper]


async def parse_message(streamer_obj: class_definition_and_manipulation.StreamerObj,
                        response: str,
                        username_regex):
    message_list = []
    for i in response.split("@badges"):
        split_response = response.split("PRIVMSG")

        irc_tags = split_response[0]
        username_regexed = username_regex.search(irc_tags)
        if username_regexed is not None:
            username = username_regexed.group(1)

            message = re.search(r":(.*)", split_response[1]).group(1)
            saved_time = formatted_time()

            await viewer_data.create_one_viewerobject(streamer_obj=streamer_obj,
                                                      viewer_name=username.strip(),
                                                      timer=class_definition_and_manipulation.Timer,
                                                      curr_time=formatted_time())
            if streamer_obj.game_name not in streamer_obj.viewer_objects[username].chat:
                streamer_obj.viewer_objects[username].chat[streamer_obj.game_name] = []
            streamer_obj.viewer_objects[username].chat[streamer_obj.game_name].append([saved_time,
                                                                                       message])
            class_definition_and_manipulation.set_active_viewer(streamer_obj.viewer_objects[username])

            if "bits=" in irc_tags:
                bits_donation = re.search(r"(bits=)[0-9]+", irc_tags).group(0)
                print(75, "main.py", bits_donation)
                bits_number = int(bits_donation.split("=")[1])
                print(77, "main.py", bits_number)
                streamer_obj.viewer_objects[username].bits_donated += bits_number
            print(f"{streamer_obj.name.upper()}-{streamer_obj.game_name}-({saved_time.hour}:"
                  f"{saved_time.minute}:{saved_time.second}) {username}: {message}")

            message_list.append([username, saved_time, message])
    return message_list


async def parse_event(streamer_obj, response):
    """
    78 @ban-duration=600;room-id=41659699;target-user-id=23951758;tmi-sent-ts=1595555353843 :tmi.twitch.tv CLEARCHAT #zerg3rr :ogre2
    78 @room-id=41659699;target-user-id=32787655;tmi-sent-ts=1595556256023 :tmi.twitch.tv CLEARCHAT #zerg3rr :kitboga
    78 @room-id=41659699;target-user-id=32787655;tmi-sent-ts=1595556478293 :tmi.twitch.tv CLEARCHAT #zerg3rr :kitboga
    # only works in parent channel not receiving channel
    78 :tmi.twitch.tv HOSTTARGET #zerg3rr :inefficient_sloth 6
    78 @msg-id=host_on :tmi.twitch.tv NOTICE #zerg3rr :Now hosting inefficient_sloth.
    162 @badge-info=;badges=moderator/1,premium/1;bits=1;color=#00FF7F;display-name=Mr_Rontastic;emotes=;flags=;id=ed522866-6fab-4c5b-a371-687e16e6d65c;mod=1;room-id=41659699;subscriber=0;tmi-sent-ts=1595637999405;turbo=0;user-id=74578764;user-type=mod :mr_rontastic!mr_rontastic@mr_rontastic.tmi.twitch.tv PRIVMSG #zerg3rr :Cheer1 ok

    gifted subs
    162 @badge-info=subscriber/2;badges=subscriber/2,sub-gift-leader/2;color=#7DA6D6;display-name=Wolf_Spear;emotes=;flags=;id=41b5df10-41c7-47e6-95b4-aedb752638bb;login=wolf_spear;mod=0;msg-id=subgift;msg-param-gift-months=1;msg-param-months=1;msg-param-origin-id=da\s39\sa3\see\s5e\s6b\s4b\s0d\s32\s55\sbf\sef\s95\s60\s18\s90\saf\sd8\s07\s09;msg-param-recipient-display-name=Batmander;msg-param-recipient-id=36217715;msg-param-recipient-user-name=batmander;msg-param-sender-count=0;msg-param-sub-plan-name=Channel\sSubscription\s(booooooooooooooooooom);msg-param-sub-plan=1000;room-id=77894502;subscriber=1;system-msg=Wolf_Spear\sgifted\sa\sTier\s1\ssub\sto\sBatmander!;tmi-sent-ts=1595728475293;user-id=145516554;user-type= :tmi.twitch.tv USERNOTICE #booooooooooooooooooom
    162 @badge-info=subscriber/2;badges=subscriber/2,sub-gift-leader/2;color=#7DA6D6;display-name=Wolf_Spear;emotes=;flags=;id=f5ee1a6b-0d66-4d8c-bca8-3410c3cfd153;login=wolf_spear;mod=0;msg-id=subgift;msg-param-gift-months=1;msg-param-months=1;msg-param-origin-id=da\s39\sa3\see\s5e\s6b\s4b\s0d\s32\s55\sbf\sef\s95\s60\s18\s90\saf\sd8\s07\s09;msg-param-recipient-display-name=t00l_mau5;msg-param-recipient-id=540272674;msg-param-recipient-user-name=t00l_mau5;msg-param-sender-count=0;msg-param-sub-plan-name=Channel\sSubscription\s(booooooooooooooooooom);msg-param-sub-plan=1000;room-id=77894502;subscriber=1;system-msg=Wolf_Spear\sgifted\sa\sTier\s1\ssub\sto\st00l_mau5!;tmi-sent-ts=1595728475348;user-id=145516554;user-type= :tmi.twitch.tv USERNOTICE #booooooooooooooooooom
    162 @badge-info=subscriber/2;badges=subscriber/2,sub-gift-leader/2;color=#7DA6D6;display-name=Wolf_Spear;emotes=;flags=;id=86217c64-4509-40e1-aa5e-5e9102fd742a;login=wolf_spear;mod=0;msg-id=subgift;msg-param-gift-months=1;msg-param-months=2;msg-param-origin-id=da\s39\sa3\see\s5e\s6b\s4b\s0d\s32\s55\sbf\sef\s95\s60\s18\s90\saf\sd8\s07\s09;msg-param-recipient-display-name=snowfireclan;msg-param-recipient-id=433219082;msg-param-recipient-user-name=snowfireclan;msg-param-sender-count=0;msg-param-sub-plan-name=Channel\sSubscription\s(booooooooooooooooooom);msg-param-sub-plan=1000;room-id=77894502;subscriber=1;system-msg=Wolf_Spear\sgifted\sa\sTier\s1\ssub\sto\ssnowfireclan!;tmi-sent-ts=1595728475471;user-id=145516554;user-type= :tmi.twitch.tv USERNOTICE #booooooooooooooooooom


    https://dev.twitch.tv/docs/irc/tags#usernotice-twitch-tags
    @badge-info=<badge-info>;badges=<badges>;color=<color>;display-name=<display-name>;emotes=<emotes>;id=<id-of-msg>;login=<user>;mod=<mod>;msg-id=<msg-id>;room-id=<room-id>;subscriber=<subscriber>;system-msg=<system-msg>;tmi-sent-ts=<timestamp>;turbo=<turbo>;user-id=<user-id>;user-type=<user-type> :tmi.twitch.tv USERNOTICE #<channel> :<message>


    162 @badge-info=subscriber/2;badges=subscriber/2,glhf-pledge/1;color=#D2691E;display-name=CeeJVic;emotes=;flags=;id=503cba8e-20f2-4ee9-88fd-979a15102b72;login=ceejvic;mod=0;msg-id=resub;msg-param-cumulative-months=2;msg-param-months=0;msg-param-should-share-streak=0;msg-param-sub-plan-name=Channel\sSubscription\s(booooooooooooooooooom);msg-param-sub-plan=1000;room-id=77894502;subscriber=1;system-msg=CeeJVic\ssubscribed\sat\sTier\s1.\sThey've\ssubscribed\sfor\s2\smonths!;tmi-sent-ts=1595644575283;user-id=49693035;user-type= :tmi.twitch.tv USERNOTICE #booooooooooooooooooom :whoa, interesting aesthetic. I be lurkin in the chats this friyay, but have good strim, great weekend start, and some good good. <,< with the evil I guess
    162 @badge-info=subscriber/16;badges=subscriber/12,glhf-pledge/1;color=#19FF19;display-name=mr_gnarlton;emotes=300977152:37-44;flags=;id=1f04b5e6-8d06-44b0-ad4e-9d9e36488c9f;login=mr_gnarlton;mod=0;msg-id=resub;msg-param-cumulative-months=16;msg-param-months=0;msg-param-should-share-streak=1;msg-param-streak-months=13;msg-param-sub-plan-name=Channel\sSubscription\s(zerg3rr);msg-param-sub-plan=1000;room-id=41659699;subscriber=1;system-msg=mr_gnarlton\ssubscribed\sat\sTier\s1.\sThey've\ssubscribed\sfor\s16\smonths,\scurrently\son\sa\s13\smonth\sstreak!;tmi-sent-ts=1595645707571;user-id=92894695;user-type= :tmi.twitch.tv USERNOTICE #zerg3rr :This message technically cost me $65 bo8Derpy
    162 @badge-info=founder/33;badges=founder/0,bits/1000;color=#51E4AF;display-name=TurtleBlock;emotes=;flags=;id=18e56381-5934-452b-a21e-f628adeeb299;login=turtleblock;mod=0;msg-id=resub;msg-param-cumulative-months=33;msg-param-months=0;msg-param-should-share-streak=1;msg-param-streak-months=30;msg-param-sub-plan-name=Channel\sSubscription\s(zerg3rr);msg-param-sub-plan=1000;room-id=41659699;subscriber=1;system-msg=TurtleBlock\ssubscribed\sat\sTier\s1.\sThey've\ssubscribed\sfor\s33\smonths,\scurrently\son\sa\s30\smonth\sstreak!;tmi-sent-ts=1595645911044;user-id=78423560;user-type= :tmi.twitch.tv USERNOTICE #zerg3rr
    162 @badge-info=subscriber/13;badges=subscriber/12,premium/1;color=#0000FF;display-name=soundzx;emotes=555555589:28-29;flags=;id=4f46c210-2705-46b4-aae1-88a4b71df4b0;login=soundzx;mod=0;msg-id=resub;msg-param-cumulative-months=13;msg-param-months=0;msg-param-should-share-streak=0;msg-param-sub-plan-name=Channel\sSubscription\s(zerg3rr);msg-param-sub-plan=1000;room-id=41659699;subscriber=1;system-msg=soundzx\ssubscribed\sat\sTier\s1.\sThey've\ssubscribed\sfor\s13\smonths!;tmi-sent-ts=1595647387064;user-id=174361922;user-type= :tmi.twitch.tv USERNOTICE #zerg3rr :Good to see you back on pal ;)
    162 @badge-info=;badges=moderator/1,partner/1;color=#5B99FF;display-name=StreamElements;emotes=88:51-58;flags=;id=01fdda86-03da-429c-9de8-1aad94b33e47;mod=1;room-id=60375321;subscriber=0;tmi-sent-ts=1595713552565;turbo=0;user-id=100135110;user-type=mod :streamelements!streamelements@streamelements.tmi.twitch.tv PRIVMSG #thebuzzkill :AnAnonymousCheerer (Anonymous) just cheered 1 bits PogChamp


    mod=<mod>, 1 if mod, 0 if not mod
    clearchat for timeouts/bans
    usernotice for sub events, raid/host
    privmsg bits tag - DONE

    add a subtotal and bits total to viewer_data?

    Valid values: sub, resub, subgift, anonsubgift, submysterygift, giftpaidupgrade, rewardgift, anongiftpaidupgrade, raid, unraid, ritual, bitsbadgetier.
    msg-param-displayName = (Sent only on raid) The display name of the source user raiding this channel.
    """
    if "CLEARCHAT" in response:
        username = response.split(":")[2]
        await viewer_data.create_one_viewerobject(streamer_obj=streamer_obj,
                                                  viewer_name=username,
                                                  timer=class_definition_and_manipulation.Timer,
                                                  curr_time=formatted_time())
        if "@ban-duration=" in response:
            timeout_num = re.search("@ban-duration=(.*?);", response).group(1)
            streamer_obj.viewer_objects[username].honor -= int(timeout_num) * 0.5
        else:
            # user is banned
            streamer_obj.viewer_objects[username].honor -= 7200
    elif "USERNOTICE" in response:
        streamer_name = ""
        username = ""


async def handle_response(response: str,
                          streamer_obj: class_definition_and_manipulation.StreamerObj,
                          sock_write: asyncio.StreamWriter) -> bool:
    """
    If False we break out of the function and close the socket
    If True we simply pass because we need to skip that input as it has no chat
    Otherwise it's none because there IS a message that needs to be processed by other lines of if statement
    """
    if len(response) == 0:
        print(f"LENGTH OF RESPONSE WAS 0 FROM {streamer_obj.name}")
        await class_definition_and_manipulation.close_connection(streamer_obj)
        return False

    # if PING in response we need to reply pong to keep connection open
    elif "PING :tmi.twitch.tv\r\n" in response:
        print(f"PING FROM {streamer_obj.name} SENDING PONG")
        sock_write.write("PONG :tmi.twitch.tv\r\n".encode('utf-8', 'ignore'))
        await sock_write.drain()
        await asyncio.sleep(1 / (20 / 30))
        return True


async def check_connection(live_streamers_dict, streamer_name, event_loop):
    live_streamers_dict[streamer_name].timer_obj.stop_and_add_times(time.time())
    if live_streamers_dict[streamer_name].timer_obj.total_time_diff > 480:
        print(147, "main.py", live_streamers_dict[streamer_name].timer_obj.total_time_diff, streamer_name)
        live_streamers_dict[streamer_name].timer_obj.total_time_diff = 0
        await class_definition_and_manipulation.close_connection(live_streamers_dict[streamer_name])
        await async_connect_socket(live_streamers_dict[streamer_name])
        asyncio.ensure_future(handle_chat_message(streamer_obj=live_streamers_dict[streamer_name]),
                              loop=event_loop)


async def join_part(response, streamer_obj, username_regex):
    if ".tmi.twitch.tv PART" in response or ".tmi.twitch.tv JOIN" in response:
        """JOIN AND PART ARE VERY INACCURATE"""
        try:
            username = username_regex.search(response).group(1)
            if "JOIN" in response:
                print(f"{streamer_obj.name.upper()}-({formatted_time().hour}:"
                      f"{formatted_time().minute})"
                      f" {username} JOINED {streamer_obj.name}'s channel!")
            if "PART" in response:
                print(f"{streamer_obj.name.upper()}-({formatted_time().hour}:"
                      f"{formatted_time().minute})"
                      f" {username} LEFT {streamer_obj.name}'s channel!")
        except AttributeError as e:  # rare error, no username, somehow?
            print(114, "main.py", e)  # nonetype object has no attribute group


async def handle_chat_message(streamer_obj: class_definition_and_manipulation.StreamerObj) -> None:
    # streamers socket
    sock_read = streamer_obj.stream_socket_reader
    sock_write = streamer_obj.stream_socket_writer

    # regex to parse through final message if not whisper/ ping & pong
    username_regex = re.compile(r"!(.*)@")

    # this while true is here because it cannot be in handle response since we return the
    # message/streamer/viewer from that function
    while True:
        # decode the received message through utf-8, ignore non-utf-8 characters
        # print(136, streamer_obj.game_name)
        if streamer_obj.game_name != "":
            response = (await sock_read.read(1024)).decode('utf-8', 'ignore')
            streamer_obj.timer_obj.total_time_diff = 0
            streamer_obj.timer_obj.set_start_time()
            # print(162, "main.py", response)
            if "PRIVMSG" not in response:
                response_check = await handle_response(response, streamer_obj, sock_write)
                if response_check is False:  # if true we just pass
                    break
                await join_part(response, streamer_obj, username_regex)
                await parse_event(streamer_obj, response)
            else:
                if ".tmi.twitch.tv WHISPER" in response:
                    await parse_whisper(response, username_regex)

                else:
                    await parse_message(streamer_obj, response, username_regex)

        else:
            print(f"179, main.py, {streamer_obj.name} game = ''")
            break


async def create_streamer_class_objects(list_of_streamers: list,
                                        live_streamers_dict: dict,
                                        event_loop,
                                        auth_token: [str]) -> None:
    """
    This function will check the master list of all streamers and determine if a new streamer has
    come online/ a currently live streamer has gone offline, those changes will be reflected in
    the newly returned list
    """

    """
    gather online streamers through twitch api
    """
    live_streamer_data = get_streamers_game.get_streamers_online(list_of_streamers, auth_token)
    """
    seperate data for each streamer
    """

    for sublist in live_streamer_data:
        if "data" in sublist:
            for streamer_data in sublist['data']:
                streamer_id = streamer_data['user_id']
                streamer_name = (streamer_data['user_name']).lower()
                streamer_game_id = streamer_data['game_id']
                if streamer_name in live_streamers_dict:
                    live_streamers_dict[streamer_name].game_id = streamer_game_id
                elif streamer_name not in live_streamers_dict:

                    # print(f"{streamer_name} - {streamer_id} playing this game ID -{streamer_game_id}")

                    """
                    create streamer objects, assign values, connect to socket and start handling chat 
                    messages
                    """

                    live_streamers_dict[streamer_name] = \
                        class_definition_and_manipulation.StreamerObj(name=streamer_name,
                                                                      twitch_id=streamer_id,
                                                                      game_id=streamer_game_id)
                    live_streamers_dict[streamer_name].timer_obj.set_start_time()

                    await async_connect_socket(streamer_obj=live_streamers_dict[streamer_name])
                    asyncio.ensure_future(handle_chat_message(streamer_obj=live_streamers_dict[
                                                                  streamer_name]),
                                          loop=event_loop)
                    # live_streamers_dict[streamer_name].async_task = task
                    # print(161, f"creating object for {streamer_name.lower()}")

                    await asyncio.sleep(0)

    # print(168, live_streamers_dict)


async def destroy_streamer_class_objects(live_streamers_dict: dict, auth_token: [str]) -> None:
    """
    online streamers returns who is still online, by checking this against live streamers we
    can remove duplicates and determine who has gone offline
    """
    online_streamers = get_streamers_game.get_streamers_online(list(live_streamers_dict.keys()), auth_token)
    # print(178, live_streamers_dict)

    for key in online_streamers:
        if key != "error":
            still_live_streamers = []
            for sublist in online_streamers:
                for streamer_data in sublist['data']:
                    streamer_name = streamer_data['user_name']
                    still_live_streamers.append(streamer_name.lower())

            # list of live streamers existed to ensure someone that we just made an object for we didnt
            # turn off half a second later, does this list need to exist?

            streamers_turned_off = list(set(list(live_streamers_dict.keys())) - set(still_live_streamers))
            for streamer in streamers_turned_off:
                live_streamers_dict[streamer].game_id = -1
                streamer_id = live_streamers_dict[streamer].viewer_objects[streamer].twitch_id
                if viewer_data.no_data_check(streamer_obj=live_streamers_dict[streamer],
                                             streamer_id=streamer_id) is False:

                    await class_definition_and_manipulation.close_connection(live_streamers_dict[streamer.lower()])
                    live_streamers_dict.pop(streamer.lower())
                    print(198, "main.py", f"Deleting object for {streamer.lower()}")
            # print(193, live_streamers_dict)


async def assign_game_to_user(live_streamers_dict: dict, auth_token: [str]) -> None:
    game_dict = get_streamers_game.get_game_ids(auth_token=auth_token,
                                                live_streamers=live_streamers_dict)
    print(313, "main.py", game_dict)
    for streamer in live_streamers_dict:
        for game_id in game_dict:
            if live_streamers_dict[streamer].game_id == game_id:
                live_streamers_dict[streamer].game_name = game_dict[game_id]


async def close_streams() -> None:
    inp = input()
    while inp != "close":
        inp = input()


async def refresh_token(auth_class_object: class_definition_and_manipulation.TwitchData) -> None:
    if int(auth_class_object.current_time) + auth_class_object.refresh_timer >= int(time.time()):
        auth_class_object.get_access_token()


async def main(event_loop) -> None:
    auth_class_object = class_definition_and_manipulation.TwitchData()
    auth_class_object.get_access_token()
    # auth_class_object.check_access_token()

    list_of_streamers = ["zerg3rr", "theasianmagikarp", "int_surgency", "inefficient_sloth", "ayashi_na",
                         "raveydemon", "booooooooooooooooooom", "popbob0", "giphertius", "rxbots", "minafofina",
                         "soundzx", "arbitraryarzon", "ltzx", "dr__umshiz", "purealchemy", "garfield379",
                         "mr_rontastic", "spookynatetv", "tsdninjaking129", "paddy4",
                                                         "tsquared", "cbennett1212", "ridgure", "yebichai",
                                                         "thebuzzkill", "faultlessking", "neverlamb", "itipturtles"]

    count = 0
    sql_count = 0

    live_streamers_dict = {}
    # await close_streams()

    while True:
        if count != 0:
            await asyncio.sleep(30)
        count += 1

        await create_streamer_class_objects(list_of_streamers=list_of_streamers,
                                            live_streamers_dict=live_streamers_dict,
                                            event_loop=event_loop,
                                            auth_token=auth_class_object.app_access_token)
        await assign_game_to_user(live_streamers_dict=live_streamers_dict,
                                  auth_token=auth_class_object.app_access_token)

        for streamer in live_streamers_dict:
            await check_connection(live_streamers_dict, streamer, event_loop)
            viewer_info = viewer_data.get_viewer_info(streamer_obj=live_streamers_dict[streamer],
                                                      auth_token=auth_class_object.app_access_token)
            await viewer_data.create_multiple_viewerobjects(viewer_info=viewer_info,
                                                            streamer_obj=live_streamers_dict[streamer],
                                                            timer=class_definition_and_manipulation.Timer,
                                                            curr_time=formatted_time())
            await viewer_data.check_active_viewers(streamer_obj=live_streamers_dict[streamer], viewer_info=viewer_info)

            """
            for all the viewers in dict, if they have no twitch id, then we set their display name and twitch id from 
            the requested api data
            """
            for viewer in live_streamers_dict[streamer].viewer_objects:
                if live_streamers_dict[streamer].viewer_objects[viewer].twitch_id == 0:
                    live_streamers_dict[streamer].viewer_objects[viewer].display_name = viewer_info[viewer][0]
                    live_streamers_dict[streamer].viewer_objects[viewer].twitch_id = viewer_info[viewer][1]

            # print("\n")
            # print(f"325, {streamer}: {live_streamers_dict[streamer].viewer_objects.keys()}")
            """for viewer in live_streamers_dict[streamer].viewer_objects:
                ac_sec = live_streamers_dict[streamer].viewer_objects[viewer].active_seconds_per_game
                inac_sec = live_streamers_dict[streamer].viewer_objects[viewer].inactive_seconds_per_game
                for i in ac_sec:
                    if ac_sec[i] != 0:
                        print(f"329, {viewer}'s active seconds per game: "
                              f"{live_streamers_dict[streamer].viewer_objects[viewer].active_seconds_per_game}")
                for j in inac_sec:
                    if inac_sec[j] != 0:
                        print(f"335, {viewer}'s inactive seconds per game: "
                              f"{live_streamers_dict[streamer].viewer_objects[viewer].inactive_seconds_per_game}")"""

        await destroy_streamer_class_objects(live_streamers_dict=live_streamers_dict,
                                             auth_token=auth_class_object.app_access_token)

        await refresh_token(auth_class_object)

        if sql_count >= 10:  # every 5 minutes updates (30*10 = 300/60 = 5 minutes)
            await sql_commands.update_sql(live_streamers_dict, formatted_time(), auth_class_object.app_access_token)
            sql_count = 0
        sql_count += 1


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main(event_loop=loop))
