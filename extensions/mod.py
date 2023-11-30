import configparser as cp

import interactions as i

scope_ids = []


class ModCommand(i.Extension):
    def __init__(self, client) -> None:
        self.client = client
        self.refresh_config()

    def refresh_config(self):
        config = cp.ConfigParser()
        config.read("config.ini")
        global scope_ids
        scope_ids = config.get('General', 'servers').split(',')
