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
                config = json.load(file)
                return config.get("dm_template", "")
        return ""

    # Load DM template from file
    def load_keywords(self) -> [str]:
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r", encoding="utf-16") as file:
                config = json.load(file)
                return config.get("keywords", "")
        return []

    def save_dm_template(self, dm_template):
        self.dm_template = dm_template
        with open(self.CONFIG_FILE, "w", encoding="utf-16") as file:
            json.dump({
                "dm_template": dm_template,
                "keywords": self.keywords
            }, file)

    def save_keywords(self, keywords):
        self.keywords = keywords.split(",")
        for i in range(0, len(self.keywords)):
            self.keywords[i] = self.keywords[i].strip()
        with open(self.CONFIG_FILE, "w", encoding="utf-16") as file:
            json.dump({
                "dm_template": self.dm_template,
                "keywords": self.keywords
            }, file)

    def keywords_str(self):
        saved_keywords = ""
        for i in range(0, len(self.keywords)):
            saved_keywords += self.keywords[i]
            if i != len(self.keywords) - 1:
                saved_keywords += ", "
        return saved_keywords
