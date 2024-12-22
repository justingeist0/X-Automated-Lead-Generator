from triage.Repository import Repository
from triage.SeleniumUtil import XActions

your_username = ""
your_password = ""
keywords = ['coach', 'smma', 'entrepreneur', 'founder', 'consultant', 'help', 'video', 'fitness', 'mentor', 'certified', 'ghost', 'email', 'ads', 'growth', 'brand', 'sale', 'build', 'built', 'eth', 'btc', 'bitcoin']
starting_profiles = []
# starting_profiles = []

repo = Repository(starting_profiles, keywords)
actions = XActions()

actions.login(your_username, your_password)

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
