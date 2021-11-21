from os import walk
from os.path import join
import discord
from config.core import _json, CONFIG_FILE_PATH, COGS_DIR_PATH
from discord import activity

def return_cogs():
    __cogs__ = []
    for (path, dirs, files) in walk(COGS_DIR_PATH):
        for file in files:
            if file.endswith(".py"):
                path_to_file = join(path, file[:-3])
                table = path_to_file.maketrans("\\", ".") # for Windows
                path_to_file = path_to_file.translate(table)
                table = path_to_file.maketrans("/", ".") # for Linux
                __cogs__.append(path_to_file.translate(table))
    print(__cogs__)
    return __cogs__


# parametry bota
settings = _json(CONFIG_FILE_PATH).read()
normal_work = True
version = settings['version']
commands_prefix = settings['prefix']
description = settings['description']
owners_id = settings['owners_id']
__cogs__ = return_cogs()

default_channels = { #to_display, in_file
    "role": "role_channel_id",
    "zatwierdzanie-ról": "role_confirm_channel_id",
    "moderacja": "moderation_channel_id"
}

cache = {
    "messages": {},
}

status = _json(CONFIG_FILE_PATH).read()['status']
activities = []

for stat in status:
    activities.append(
        activity.Activity(
            name=stat,
            type=discord.ActivityType.listening,
            state="W trakcie załamania", 
        )
    )

