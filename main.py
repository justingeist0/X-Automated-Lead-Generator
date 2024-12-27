from triage.Repository import Repository
from triage.SeleniumUtil import XActions

keywords = ['coach', 'smma', 'entrepreneur', 'founder', 'consultant', 'help', 'video', 'fitness', 'mentor', 'certified', 'ghost', 'email', 'ads', 'growth', 'brand', 'sale', 'build', 'built', 'eth', 'btc', 'bitcoin']
starting_profiles = []
# starting_profiles = []

repo = Repository(starting_profiles, keywords)
actions = XActions()

actions.login()
# actions.dm_user(User(name="moo", sourced_from="fu", username="beardfistmcfist"))
while repo.messages_sent_today < 450:
    next_user_to_scrape = repo.get_next_user_to_scrape()
    users_to_dm = actions.scrape_user_name(next_user_to_scrape)
    repo.set_scraped(next_user_to_scrape)
    for user in users_to_dm:
        if repo.should_dm_user(user):
            # we try to dm user, we also update user object with their followers/followering as well.
            can_message = actions.dm_user(user)
            repo.on_user_dm_result(can_message, user)
    print("Sent ", repo.messages_sent_today, "dms so far!")



# # Messages table
# messages_frame = ttk.LabelFrame(main_frame, text="Recent Messages")
# messages_frame.grid(row=3, column=0, pady=10, sticky=tk.W+tk.E)
#
# columns = ("Username", "Status", "Inbox Link")
#
# # Create the Treeview with yscrollcommand set
# messages_tree = ttk.Treeview(messages_frame, columns=columns, show='headings', yscrollcommand=tk.Scrollbar.set)
#
# # Configure columns
# for col in columns:
#     messages_tree.heading(col, text=col)
#     messages_tree.column(col, width=100)
#
# # Create a scrollbar on the right side
# scrollbar = ttk.Scrollbar(messages_frame, orient=tk.VERTICAL, command=messages_tree.yview)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#
# # Pack the Treeview
# messages_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#
# # Link scrollbar to Treeview
# messages_tree.configure(yscrollcommand=scrollbar.set)
#
# # Example data insertion
# messages_tree.insert("", tk.END, values=("@fantasmadev", "1st DM Sent", 'https://x.com'))
# messages_tree.pack(expand=True, fill='both')
#
# # Analytics table
# analytics_frame = ttk.LabelFrame(main_frame, text="Analytics")
# analytics_frame.grid(row=4, column=0, pady=10, sticky=tk.W+tk.E)
#
# analytics_columns = ("Date", "DMs Sent", "Responded", "Interested", "Sales")
# analytics_tree = ttk.Treeview(analytics_frame, columns=analytics_columns, show='headings')
# for col in analytics_columns:
#     analytics_tree.heading(col, text=col)
#     analytics_tree.column(col, width=100)
#
# # Example data insertion
# analytics_tree.insert("", tk.END, values=("Dec 22", 100, 50, 20, 5))
# analytics_tree.pack(expand=True, fill='both')
