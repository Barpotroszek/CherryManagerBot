import json_files as json
from os import makedirs
from os.path import isfile

class _json():
    def __init__(self, path) -> None:
        self.path = path

    def read(self) -> dict:
        """Zwraca zawartość danego pliku"""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                f.close()
                return data
        except (FileNotFoundError, FileExistsError):
            return {}

    def write(self, data):
        with open(self.path, "w",  encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()

# stałe zmienne dla bota
SECRETS_FILE_PATH = "./config/SECRETS.json"
CONFIG_FILE_PATH = "./config/config.json"
COGS_DIR_PATH = "cogs"
DATA_DIR_PATH = "data"
LOGS_DIR_PATH = f"{DATA_DIR_PATH}/logs"
SERVERS_SETTINGS_FILES = "data/servers_settings"
TOKEN_M = _json(SECRETS_FILE_PATH).read()["MAIN"]
TOKEN_T = _json(SECRETS_FILE_PATH).read()["TEST"]
default_channels = {
    "role": "role_channel_id",
    "zatwierdzanie-ról": "role_confirm_channel_id",
    "moderacja": "moderation_channel_id"
}


async def startup(bot):
    '''Uruchamianie "systemu", tworzenie potrzebnych folderów i plików'''
    makedirs(DATA_DIR_PATH, exist_ok=True)
    makedirs(LOGS_DIR_PATH, exist_ok=True)
    makedirs(SERVERS_SETTINGS_FILES, exist_ok=True)

    # creating file for each guild
    for guild in bot.guilds:
        path = f"{SERVERS_SETTINGS_FILES}/{guild.id}.json"  # creating path
        data={}

        # if there's a file, then continue
        if isfile(path):
            continue

        #if there's no file, then create it and make: 
        f = open(path, "a+", encoding="utf-8")
        print("Guild: ", guild.name)
        data["name"] = guild.name
        data['role_channel_id'] = None
        data['role_confirm_channel_id'] = None
        data['moderation_channel_id'] = None
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2, ensure_ascii=False)

class GuildParams:
    def __init__(self, id: int):
        self.id = id
        self.settings_filename=f'{SERVERS_SETTINGS_FILES}/{self.id}.json'
        print("File:", self.settings_filename)
        
        guild_config = _json(self.settings_filename).read()
        
        try:
            self.role_channel_id = guild_config['role_channel_id']
            self.role_confirm_channel_id = guild_config['role_confirm_channel_id']
            self.moderation_channel_id = guild_config['moderation_channel_id']
        except:
            pass
        #self.spectator_role_id = guild_config['spectator_role_id']

    def add_new(self, data):
        settings = _json(self.settings_filename).read()
        for a, b in default_channels.items():
            settings[b] = data[a].id
        _json(self.settings_filename).write(settings)
