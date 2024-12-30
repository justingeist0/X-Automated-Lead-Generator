import json
import os


class Config:

    def __init__(self):
        self.CONFIG_FILE = "config.json"
        self.keywords = self.load_keywords()
        self.dm_template = self.load_dm_template()
        self.manual_queue = []

    # Load DM template from file
    def load_dm_template(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r", encoding="utf-16") as file:
                try:
                    config = json.load(file)
                except Exception as e:
                    return ""
                return config.get("dm_template", "")
        return ""

    # Load DM template from file
    def load_keywords(self) -> [str]:
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r", encoding="utf-16") as file:
                try:
                    config = json.load(file)
                except Exception as e:
                    return []
                return config.get("keywords", [])
        return []

    def load_manual_queue(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r", encoding="utf-16") as file:
                try:
                    config = json.load(file)
                except Exception as e:
                    return []
                return config.get("manual_queue", [])
        return []

    def save_dm_template(self, dm_template):
        self.dm_template = dm_template
        with open(self.CONFIG_FILE, "w", encoding="utf-16") as file:
            json.dump({
                "dm_template": dm_template,
                "keywords": self.keywords,
                "manual_queue": self.manual_queue
            }, file)

    def save_keywords(self, keywords):
        self.keywords = keywords.split(",")
        for i in range(0, len(self.keywords)):
            self.keywords[i] = self.keywords[i].strip()
        with open(self.CONFIG_FILE, "w", encoding="utf-16") as file:
            json.dump({
                "dm_template": self.dm_template,
                "keywords": self.keywords,
                "manual_queue": self.manual_queue
            }, file)

    def save_manual_queue(self, manual_queue):
        self.manual_queue = manual_queue.split(",")
        for i in range(0, len(self.manual_queue)):
            self.manual_queue[i] = self.manual_queue[i].strip()
        with open(self.CONFIG_FILE, "w", encoding="utf-16") as file:
            json.dump({
                "dm_template": self.dm_template,
                "keywords": self.keywords,
                "manual_queue": self.manual_queue
            }, file)

    def keywords_str(self):
        saved_keywords = ""
        for i in range(0, len(self.keywords)):
            saved_keywords += self.keywords[i]
            if i != len(self.keywords) - 1:
                saved_keywords += ", "
        return saved_keywords

    def manual_queue_str(self):
        saved_queue = ""
        for i in range(0, len(self.manual_queue)):
            saved_queue += self.manual_queue[i]
            if i != len(self.manual_queue) - 1:
                saved_queue += ", "
        return saved_queue
