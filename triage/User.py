import datetime

class User:
    def __init__(self, name="", username="", sourced_from="manual input", bio="", followers=None, following=None, is_verified=True, date_created=None, total_dms_sent=0, last_dm_sent=None, is_scraped=False):
        self.name = name
        self.username = username
        self.bio = bio
        self.followers = followers
        self.following = following
        self.is_verified = is_verified
        self.sourced_from = sourced_from
        self.date_created = date_created if date_created else datetime.date.today()
        self.total_dms_sent = total_dms_sent  # Corrected from 'total_dms_send' to 'total_dms_sent'
        self.last_dm_sent = last_dm_sent if last_dm_sent else None
        self.is_scraped = is_scraped

    def __str__(self):
        return (
            f"Name: {self.name} "
            f"Username: @{self.username} "
            f"Bio: {self.bio or 'N/A'} "
            f"Followers: {self.followers if self.followers is not None else 'N/A'} "
            f"Following: {self.following if self.following is not None else 'N/A'} "
            f"Verified: {'Yes' if self.is_verified else 'No'} "
            f"Sourced From: {self.sourced_from} "
            f"Date Created: {self.date_created} "
            f"Total DMs Sent: {self.total_dms_sent} "
            f"Last DM Sent: {self.last_dm_sent if self.last_dm_sent else 'Never'} "
            f"Is Scraped: {'Yes' if self.is_scraped else 'No'}"
        )

    def check_for_keyword(self, keyword):
        return keyword in f"{self.name} {self.username} {self.bio}".lower()
