import datetime
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from config import Config, get_executable_dir
from triage.Repository import Repository
from triage.SeleniumUtil import XActions


def filter_bmp(text):
    # Keep characters with Unicode values up to U+FFFF (BMP)
    return ''.join(char for char in text if ord(char) <= 0xFFFF)


class GUI:

    def __init__(self):
        self.config = Config()
        self.actions = XActions(self.config)
        self.repo = Repository(self.config)

        self.start_dming = False

        # Main window
        self.root = tk.Tk()
        self.root.title("Fantasma.dev - X Automated Lead Generator") # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.label = tk.Label(self.main_frame, text="X Automated Lead Generator", font=("Arial Bold", 18), foreground='black',
                              background="light blue")
        self.label.grid(row=0, column=0, columnspan=2, pady=5)

        # Status text
        self.status_label = ttk.Label(self.main_frame, text="Status: Off")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Login button
        self.login_button = ttk.Button(self.main_frame, text="Start DMing", command=self.toggle_on)
        self.login_button.grid(row=2, column=0, pady=5, columnspan=2)

        # DM Template Label
        self.message_label = ttk.Label(self.main_frame, text="DM Message Template, Use \"{name}\" to Personalize:")
        self.message_label.grid(row=3, column=0, pady=(20, 10), sticky=tk.W)

        # DM Template Save Button
        self.save_dm_button = ttk.Button(self.main_frame, text="Save Template", command=self.save_dm_template, state=tk.DISABLED)
        self.save_dm_button.grid(row=3, column=1, pady=(20, 10), sticky="e")

        # DM Template Text Box
        self.dm_template_input = tk.Text(self.main_frame, height=6, width=50, wrap="word", font=("Arial", 12))
        self.dm_template_input.grid(row=4, column=0, pady=(0, 5), columnspan=2, sticky=(tk.W, tk.E))
        self.dm_template_input.insert("1.0", self.config.dm_template)
        self.dm_template_input.edit_modified(False)
        self.dm_template_input.bind("<<Modified>>", self.on_dm_change)

        # Keyword input label
        self.keyword_label = ttk.Label(self.main_frame, text="Enter Keywords, Separated by Commas:")
        self.keyword_label.grid(row=5, column=0, pady=(20, 0), sticky=tk.W)

        # Keyword save
        self.save_keywords_button = ttk.Button(self.main_frame, text="Save Keywords", command=self.save_keywords, state=tk.DISABLED)
        self.save_keywords_button.grid(row=5, column=1, pady=(20, 0), sticky="e")

        # Keyword variable and trace
        self.keyword_var = tk.StringVar(value=self.config.keywords_str())
        self.keyword_var.trace_add("write", self.on_keyword_change)
        self.keyword_entry = ttk.Entry(self.main_frame, textvariable=self.keyword_var, width=40)
        self.keyword_entry.grid(row=6, column=0, pady=5, columnspan=2, sticky=(tk.W, tk.E))

        # Username input label
        self.username_label = ttk.Label(self.main_frame, text="(optional) Add Usernames to Scrape, Separated by Commas:")
        self.username_label.grid(row=7, column=0, pady=(20, 0), sticky=tk.W)

        # Username save
        self.save_username_button = ttk.Button(self.main_frame, text="Add Usernames to Queue", command=self.save_usernames, state=tk.DISABLED)
        self.save_username_button.grid(row=7, column=1, pady=(20, 0), sticky="e")

        # Username variable and trace
        self.username_var = tk.StringVar(value=self.config.manual_queue_str())
        self.username_var.trace_add("write", self.on_username_keyword_change)
        self.username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var, width=40)
        self.username_entry.grid(row=8, column=0, pady=5, columnspan=2, sticky=(tk.W, tk.E))

        # Analytics table
        self.analytics_frame = ttk.LabelFrame(self.main_frame, text="Total Daily DMs Sent")
        self.analytics_frame.grid(row=9, column=0, pady=10, sticky=tk.W+tk.E, columnspan=2)

        analytics_columns = ("Date", "DMs Sent")
        self.analytics_tree = ttk.Treeview(self.analytics_frame, columns=analytics_columns, show='headings', height=3)
        for col in analytics_columns:
            self.analytics_tree.heading(col, text=col)
            self.analytics_tree.column(col, width=100)
        self.populate_analytics_table()

        # Configure grid to make everything stretch with the window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Ensure the window renders correctly on macOS
        self.root.after(100, self.ensure_visibility)
        task_thread = threading.Thread(target=self.background_task, daemon=True)
        task_thread.start()
        self.root.mainloop()

    def ensure_visibility(self):
        # macOS sometimes needs a slight delay before widgets are displayed
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))

    def on_closing(self):
        self.root.destroy()
        self.actions.off()

    def populate_analytics_table(self):
        # Get today's date
        today = datetime.date.today()
        # Calculate the date 100 days ago
        start_date = today - datetime.timedelta(days=100)

        # Query the repository for analytics data
        # Assuming the repository provides a method `get_analytics_data(start_date, end_date)`
        data = self.repo.get_analytics_data(start_date, today)

        # Expected format of `data`: list of tuples [("Date", dms_sent, responded, interested, not_interested, sales)]
        # Clear any existing rows in the analytics_tree
        for row in self.analytics_tree.get_children():
            self.analytics_tree.delete(row)

        # Populate the table with data
        for row in data:
            self.analytics_tree.insert("", tk.END, values=row)
            self.analytics_tree.pack(expand=True, fill='both')

    def update_status(self, new_status, disable=False):
        self.status_label.config(text=f"Status: {new_status}")
        self.login_button.config(state=tk.DISABLED if disable else tk.NORMAL)
        self.login_button.update_idletasks()
        self.status_label.update_idletasks()

    def toggle_on(self):
        self.start_dming = not self.start_dming
        self.login_button.config(text="Stop DMing" if self.start_dming else "Start DMing")
        self.update_status("Finishing up last DMs" if not self.start_dming else "Starting DMing")
        if self.save_keywords_button["state"] == tk.NORMAL or self.save_username_button["state"] == tk.NORMAL:
            messagebox.showwarning("Unsaved Changes", "You have unsaved changes.")

    def background_task(self):
        while True:
            while self.repo.messages_sent_today < 450 and self.start_dming:
                time.sleep(1)
                try:
                    if self.actions.is_browser_closed():
                        self.update_status("Opening web browser. Could take a minute. Please log in if you haven't already.")
                        self.actions.login()
                        self.actions.save_cookies_until_auth_token()
                    next_user_to_scrape = self.repo.get_next_user_to_scrape()
                    self.update_status(f"Scraping user {next_user_to_scrape}")

                    users_to_dm = self.actions.scrape_user_name(next_user_to_scrape)
                    print(users_to_dm)
                    self.repo.set_scraped(next_user_to_scrape)

                    for user in users_to_dm:
                        if not self.start_dming:
                            break

                        self.update_status(f"Visiting {user.username} profile")

                        if self.repo.should_dm_user(user):
                            can_message = self.actions.dm_user(user)
                            self.repo.on_user_dm_result(can_message, user)
                            if can_message:
                                self.populate_analytics_table()

                except Exception as e:
                    self.update_status("Reopening browser.")
                    self.actions.off()
                    time.sleep(1)
            self.update_status("Off")
            time.sleep(1)

    def on_keyword_change(self, text1, text2, text3):
        keywords = self.keyword_var.get()
        self.save_keywords_button.config(state=tk.NORMAL if keywords != self.config.keywords_str() else tk.DISABLED)

    def on_username_keyword_change(self, text1, text2, text3):
        username = self.username_var.get()
        self.save_username_button.config(state=tk.NORMAL if username != self.config.manual_queue_str() else tk.DISABLED)

    def save_keywords(self):
        keywords = self.keyword_var.get()
        self.config.save_keywords(str(keywords.lower()))
        messagebox.showinfo("Success", "Saved keywords. " + str(self.config.keywords))
        self.save_keywords_button.config(state=tk.DISABLED)

    def save_usernames(self):
        username = self.username_var.get()
        self.config.save_manual_queue(username)
        messagebox.showinfo("Success", "Saved usernames to queue. " + str(self.config.manual_queue))
        self.save_username_button.config(state=tk.DISABLED)

    def on_dm_change(self, event=None):
        """
        Handles text changes in the message box.
        This function is triggered by the <<Modified>> event.
        """
        # Ensure the event is responding to real changes
        if self.dm_template_input.edit_modified():
            # Get current text from the text box
            dm_template = self.dm_template_input.get("1.0", tk.END).strip()

            # Enable or disable the "Save Template" button based on changes
            self.save_dm_button.config(state=tk.NORMAL if dm_template != self.config.dm_template else tk.DISABLED)

            # Reset the "modified" flag
            self.dm_template_input.edit_modified(False)

    def save_dm_template(self):
        dm_template = self.dm_template_input.get("1.0", tk.END).strip()
        dm_template = filter_bmp(dm_template)
        self.config.save_dm_template(dm_template)
        messagebox.showinfo("Success", "New DM Template saved. " + self.config.dm_template)
        self.save_dm_button.config(state=tk.DISABLED)

    def populate_messages_table(self):
        # Get today's date
        today = datetime.date.today()
        # Calculate the date 100 days ago
        start_date = today - datetime.timedelta(days=100)

        # Query the repository for analytics data
        # Assuming the repository provides a method `get_analytics_data(start_date, end_date)`
        data = self.repo.get_analytics_data(start_date, today)

        # Expected format of `data`: list of tuples [("Date", dms_sent, responded, interested, not_interested, sales)]

        # Clear any existing rows in the analytics_tree
        for row in self.messages_tree.get_children():
            self.messages_tree.delete(row)

        for row in data:
            self.messages_tree.insert("", tk.END, values=("Dec 27", "@fantasmadev", "htttps://x.com/messages"))
            self.messages_tree.pack(expand=True, fill='both')

    def on_message_sort_change(self):
        sort_by = self.message_sort_var.get()
        self.populate_messages_table()

GUI()


