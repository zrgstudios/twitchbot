import re

print('Importing commands')


def get_commands(general):
    with open("MyFiles/bot_commands.txt") as f:
        x = f.readlines()

    general.str_command_dict = {}  # this does not yet exist in bot.py
    general.list_command_dict = {}

    for line in x:
        if line is None or line == "\n":
            pass
        else:
            command_and_random = re.findall("(-.*?) ", line)
            command = command_and_random[0]

            command_output = re.search("(?<=\[)(.*)(?=\])", line)
            if len(command_output.group(0).split(';')) > 1:
                general.list_command_dict[command] = []
                for i in command_output.group(0).split(';'):
                    general.list_command_dict[command].append(i)
            else:
                general.str_command_dict[command] = command_output.group(0)
            # command_and_random[1], this means we have a random keyword
