import json
from os import walk
from os.path import join


class _json():
    def __init__(self, path) -> None:
        self.path = path

    def read(self) -> dict:
        """Zwraca zawartość danego pliku"""
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
            return data

    def write(self, data):
        with open(self.path, "w",  encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()

settings = _json('data/config.json').read()

def return_cogs():
    __cogs__ = []
    for (path, dirs, files) in walk(settings["path_to_cogs"]):
        for file in files:
            if file.endswith(".py"):
                path = join(path, file)
                table = path.maketrans("\\", ".")

                __cogs__.append(path.translate(table)[2:-3])
    print(__cogs__)
    return __cogs__


# podstawowe parametry bota
# TOKEN = settings['token']
normal_work = True
version = settings['version']
commands_prefix = settings['prefix']
description = settings['description']
status = settings['status']
owners_id = settings['owners_id']
__cogs__ = return_cogs()

default_channels = {
    "role": "role_channel_id",
    "zatwierdzanie-ról": "role_confirm_channel_id",
    "moderacja": "moderation_channel_id"
}

cache = {
    "messages": [],
}


class GuildParams:
    def __init__(self, id: int):
        self.id = id

        with open('data/config.json', 'r+', encoding="utf-8") as f:
            settings = json.load(f)
            f.close()

        if str(id) not in settings['guilds']:
            settings['guilds'][str(self.id)] = {}
        guild_config = settings['guilds'][str(id)]
        try:
            self.role_channel_id = guild_config['role_channel_id']
            self.role_confirm_channel_id = guild_config['role_confirm_channel_id']
            self.moderation_channel_id = guild_config['moderation_channel_id']
        except:
            pass
        #self.spectator_role_id = guild_config['spectator_role_id']

    def add_new(self, data):
        with open('data/config.json', 'r+', encoding="utf-8") as f:
            settings = json.load(f)
            settings['guilds'][str(self.id)] = {}
            for a, b in default_channels.items():
                settings['guilds'][str(self.id)][b] = data[a].id
            f.seek(0)
            f.truncate()
            json.dump(settings, f, indent=4, ensure_ascii=False)
