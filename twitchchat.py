#!/usr/bin/env python3

from twitchbot import encryption_key

fkey = encryption_key.fkey


def chat(sock, msg):
    """
   send a chat message to the server
   Keyboard arguments:
   sock -- the socket over which to send the message
   msg -- the message to be sent
   """
    full_msg = "PRIVMSG {} :{}\n".format('#' + encryption_key.decrypted_chan, msg)
    msg_encoded = full_msg.encode("utf-8")
    print(msg_encoded)
    sock.send(msg_encoded)


def whisper(sock, msg):
    whisper_msg = "PRIVMSG {} :{}\n".format('#' + encryption_key.decrypted_chan, msg)
    whisper_encode = whisper_msg.encode("utf-8")
    print(whisper_encode)
    sock.send(whisper_encode)
