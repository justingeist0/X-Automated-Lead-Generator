
from kivy.app import App
from kivy.clock import mainthread
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
import datetime
import threading
from config import Config
from triage.Repository import Repository
from triage.SeleniumUtil import XActions


def filter_bmp(text):
    # Keep characters with Unicode values up to U+FFFF (BMP)
    return ''.join(char for char in text if ord(char) <= 0xFFFF)


class LeadGeneratorApp(App):

    def build(self):
        self.config = Config()
        self.actions = XActions(self.config)
        self.repo = Repository(self.config)
        self.stop_event = False
        self.title = "Laplead.com - X Automated Lead Generator"

        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=12)
        # Header
        header_label = Label(
            text="X Automated Lead Generator",
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.1),
        )
        main_layout.add_widget(header_label)

        # Status Label
        self.status_label = Label(
            text="Status: Off",
            font_size='14sp',
            size_hint=(1, 0.1)
        )
        main_layout.add_widget(self.status_label)

        # Power Button
        self.login_button = Button(
            text="Power On",
            size_hint=(1, 0.1),
            on_press=self.toggle_on
        )
        main_layout.add_widget(self.login_button)


        analytics_label = Label(
            text="Total Daily DMs Sent:",
            font_size='14sp',
            size_hint=(1, 0.05)
        )
        main_layout.add_widget(analytics_label)
        # Scrollable GridLayout
        scroll_view = ScrollView(size_hint=(1, 0.5), do_scroll_x=False, do_scroll_y=True)
        self.grid_layout = GridLayout(cols=2, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        # Add the GridLayout to ScrollView
        scroll_view.add_widget(self.grid_layout)
        main_layout.add_widget(scroll_view)

        # DM Template
        dm_template_label = Label(
            text="DM Message Template (Use {name} to personalize):",
            size_hint=(1, 0.05),
            halign='left',
            text_size=(None, None), # Allow the label to expand horizontally
            padding=(20, 0, 0, 0)  # Increase top margin by 20 pixels
        )
        main_layout.add_widget(dm_template_label)

        self.dm_template_input = TextInput(
            multiline=True,
            size_hint=(1, 0.4),
            text=self.config.dm_template
        )
        self.dm_template_input.bind(text=self.on_dm_input_change)
        main_layout.add_widget(self.dm_template_input)

        self.save_dm_button = Button(
            text="Save Template",
            size_hint=(1, 0.1),
            on_press=self.save_dm_template,
            disabled = True
        )
        main_layout.add_widget(self.save_dm_button)

        # Keywords
        keyword_label = Label(
            text="Enter Keywords (comma-separated):",
            font_size='14sp',
            size_hint=(1, 0.05)
        )
        main_layout.add_widget(keyword_label)

        self.keyword_input = TextInput(
            size_hint=(1, 0.1),
            text = self.config.keywords_str()
        )
        self.keyword_input.bind(text=self.on_keyword_input_change)
        main_layout.add_widget(self.keyword_input)

        self.save_keywords_button = Button(
            text="Save Keywords",
            size_hint=(1, 0.1),
            on_press=self.save_keywords,
            disabled = True
        )
        main_layout.add_widget(self.save_keywords_button)

        # Usernames
        username_label = Label(
            text="Enter Usernames (comma-separated):",
            font_size='14sp',
            size_hint=(1, 0.05),
        )
        main_layout.add_widget(username_label)

        self.username_input = TextInput(
            size_hint=(1, 0.1),
            text=self.config.manual_queue_str()
        )
        self.username_input.bind(text=self.on_username_keyword_input_change)
        main_layout.add_widget(self.username_input)

        self.save_usernames_button = Button(
            text="Update Usernames in Queue",
            size_hint=(1, 0.1),
            on_press=self.save_usernames,
            disabled = True
        )
        main_layout.add_widget(self.save_usernames_button)


        self.populate_analytics_table()

        return main_layout

    @mainthread
    def populate_analytics_table(self):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=10)
        data = self.repo.get_analytics_data(start_date, today)
        self.grid_layout.clear_widgets()
        # Add Header Row
        self.grid_layout.add_widget(Label(text='Date', bold=True, size_hint_y=None, height=30))
        self.grid_layout.add_widget(Label(text='Total', bold=True, size_hint_y=None, height=30))
        for row in data:
            date, dms_sent = row[0], row[1]
            self.grid_layout.add_widget(Label(text=str(date), size_hint_y=None, height=30))
            self.grid_layout.add_widget(Label(text=str(dms_sent), size_hint_y=None, height=30))

    def update_status(self, new_status, disable=False):
        self.status_label.text = f"Status: {new_status}"
        self.login_button.disabled=disable

    def toggle_on(self, *kwargs):
        if self.login_button.text == "Power Off":
            self.login_button.text = "Power On"
            self.stop_event = True
            if "Visiting" in self.status_label.text:
                self.update_status("Finishing DM and then quitting...", disable=True)
            else:
                self.actions.off()
                self.update_status("Turning off...", disable=True)
            return
        self.stop_event = False
        task_thread = threading.Thread(target=self.background_task, daemon=True)
        task_thread.start()
        self.login_button.text = "Power Off"
        self.update_status("Please log in. Waiting up to 60 to get started.")

    def background_task(self):
        try:
            if not self.actions.login():
                self.actions.off()
                self.update_status("Logged out, please log in within 60 seconds.")
                return
        except Exception as e:
            if not self.stop_event:
                self.update_status("Unknown error please take screenshot of this error, send it to me, and restart application." + str(e))

        self.login_button.disabled = False
        while self.repo.messages_sent_today < 450 and not self.stop_event:
            next_user_to_scrape = self.repo.get_next_user_to_scrape()
            self.update_status(f"Scraping user {next_user_to_scrape}")

            try:
                users_to_dm = self.actions.scrape_user_name(next_user_to_scrape)
                self.repo.set_scraped(next_user_to_scrape)
            except Exception as e:
                if not self.stop_event:
                    self.update_status("Unknown error please take screenshot of this error, send it to me, and restart application." + str(e))
                users_to_dm = []

            for user in users_to_dm:
                if self.stop_event:
                    break

                self.update_status(f"Visiting {user.username} profile")
                if self.repo.should_dm_user(user):
                    can_message = self.actions.dm_user(user)
                    self.repo.on_user_dm_result(can_message, user)
                    self.update_status(f"Sent {self.repo.messages_sent_today} DMs Today")
                    if can_message:
                        self.populate_analytics_table()

        self.actions.off()
        self.update_status("Off")

    def on_keyword_input_change(self, *kwargs):
        keywords = self.keyword_input.text
        self.save_keywords_button.disabled = keywords == self.config.keywords_str()

    def on_username_keyword_input_change(self, *kwargs):
        username = self.username_input.text
        self.save_usernames_button.disabled = username == self.config.manual_queue_str()

    def on_dm_input_change(self, *kwargs):
        text = self.dm_template_input.text
        self.save_dm_button.disabled = text == self.config.dm_template

    def save_keywords(self, *kwargs):
        keywords = self.keyword_input.text
        self.config.save_keywords(keywords)
        self.save_keywords_button.disabled = True

        popup = Popup(title='Keywords Saved',
                      content=Label(text=f"Keywords saved:\n{keywords}"),
                      size_hint=(0.6, 0.4))
        popup.open()

    def save_usernames(self, *kwargs):
        usernames = self.username_input.text
        self.config.save_manual_queue(usernames)
        self.save_usernames_button.disabled = True

        popup = Popup(title='Usernames Saved',
                      content=Label(text=f"Usernames saved:\n{self.config.manual_queue}"),
                      size_hint=(0.6, 0.4))
        popup.open()

    def save_dm_template(self, *kwargs):
        dm_template = self.dm_template_input.text.strip()
        dm_template = filter_bmp(dm_template)
        self.config.save_dm_template(dm_template)
        self.save_dm_button.disabled = True

        popup = Popup(title='Template Saved',
                      content=Label(text=f"DM Template saved:\n{dm_template}"),
                      size_hint=(0.6, 0.4))
        popup.open()

    # def populate_messages_table(self):
    #     # Get today's date
    #     today = datetime.date.today()
    #     # Calculate the date 100 days ago
    #     start_date = today - datetime.timedelta(days=100)
    #
    #     # Query the repository for analytics data
    #     # Assuming the repository provides a method `get_analytics_data(start_date, end_date)`
    #     data = self.repo.get_analytics_data(start_date, today)
    #
    #     # Expected format of `data`: list of tuples [("Date", dms_sent, responded, interested, not_interested, sales)]
    #
    #     # Clear any existing rows in the analytics_tree
    #     for row in self.messages_tree.get_children():
    #         self.messages_tree.delete(row)
    #
    #     for row in data:
    #         self.messages_tree.insert("", tk.END, values=("Dec 27", "@fantasmadev", "htttps://x.com/messages"))
    #         self.messages_tree.pack(expand=True, fill='both')



if __name__ == '__main__':
    LeadGeneratorApp().run()
