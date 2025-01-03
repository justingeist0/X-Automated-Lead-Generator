import csv
import datetime
import sqlite3
from datetime import date

from config import Config, get_executable_dir
from triage.User import User


class Repository:

    def __init__(self, config: Config):
        self.messages_sent_today = 0
        self.db_path = get_executable_dir() / "prospects.db"
        self.create_user_table()
        self.config = config
        self.export_users_with_dms_sent_one()

    def create_user_table(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # SQL command to create the table with username as the primary key
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT NOT NULL,
            username TEXT PRIMARY KEY,
            bio TEXT,
            followers INTEGER,
            following INTEGER,
            is_verified BOOLEAN DEFAULT 1,
            sourced_from TEXT NOT NULL,
            date_created DATE NOT NULL,
            total_dms_sent INTEGER DEFAULT 0,
            last_dm_sent DATE,
            is_scraped BOOLEAN DEFAULT 0
        )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
        conn.commit()
        conn.close()

    def export_users_with_dms_sent_one(self, output_csv_path=get_executable_dir() / "list.csv"):
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Query to fetch all rows where total_dms_sent = 1
        c.execute('SELECT * FROM users WHERE total_dms_sent = 1')
        rows = c.fetchall()
        print(rows)

        # Fetch the column names from the table
        column_names = [description[0] for description in c.description]

        # Write the result to a CSV file
        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)

            # Write the header (column names)
            writer.writerow(column_names)

            # Write the data rows
            writer.writerows(rows)

        # Close the database connection
        conn.close()

        print(f"Exported all users with total_dms_sent = 1 to {output_csv_path}")

    def get_user(self, username):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Query to fetch user by username
        c.execute('''
        SELECT name, username, bio, followers, following, is_verified, 
               sourced_from, date_created, total_dms_sent, last_dm_sent, is_scraped
        FROM users 
        WHERE username = ?
        ''', (username,))

        # Fetch one user record
        user_data = c.fetchone()

        if user_data:
            # If user found, create and return User object
            user = User(
                name=user_data[0],
                username=user_data[1],
                bio=user_data[2],
                followers=user_data[3],
                following=user_data[4],
                is_verified=user_data[5],
                sourced_from=user_data[6],
                date_created=user_data[7],
                total_dms_sent=user_data[8],
                last_dm_sent=user_data[9],
                is_scraped=user_data[10]
            )
            conn.close()
            return user
        else:
            # If no user found, return None or handle accordingly
            conn.close()
            return None

    def update_user(self, user):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Try to update an existing user
        c.execute('''
        UPDATE users 
        SET name = ?, 
            bio = ?, 
            followers = ?, 
            following = ?, 
            is_verified = ?, 
            sourced_from = ?, 
            date_created = ?, 
            total_dms_sent = ?, 
            last_dm_sent = ?,
            is_scraped = ?
        WHERE username = ?
        ''', (
            user.name,
            user.bio,
            user.followers,
            user.following,
            user.is_verified,
            user.sourced_from,
            user.date_created,
            user.total_dms_sent,
            user.last_dm_sent,
            user.is_scraped,
            user.username
        ))

        # If no rows were affected by the update (i.e., user didn't exist), insert a new user
        if c.rowcount == 0:
            c.execute('''
            INSERT INTO users (name, username, bio, followers, following, is_verified, 
                               sourced_from, date_created, total_dms_sent, last_dm_sent, is_scraped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.name,
                user.username,
                user.bio,
                user.followers,
                user.following,
                user.is_verified,
                user.sourced_from,
                user.date_created,
                user.total_dms_sent,
                user.last_dm_sent,
                user.is_scraped
            ))
            print(f"User {user.username} added to the database.")
        else:
            print(f"User {user.username} updated in the database.")
        conn.commit()
        conn.close()

    def get_next_user_to_scrape(self):
        if len(self.config.manual_queue) > 0:
            return self.config.manual_queue.pop()
        return self.find_next_user_to_scrape()

    def should_dm_user(self, user: User):
        # See if user is in database already based on username.
        existing_user = self.get_user(user.username)
        if existing_user is not None:
            user = existing_user
        else:
            self.update_user(user)

        # See if has been DMed before
        if user.last_dm_sent is not None:
            print("DM Sent already or can't sent DM", user)
            return False

        if len(self.config.keywords) == 0:
            return True

        # Check bio, username, and display name for keywords.
        for keyword in self.config.keywords:
            if user.check_for_keyword(keyword):
                return True
        return False

    def on_user_dm_result(self, can_message, user):
        if can_message:
            self.messages_sent_today += 1
            user.last_dm_sent = date.today()
        else:
            user.last_dm_sent = -1
        self.update_user(user)

    def find_next_user_to_scrape(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Build the SQL WHERE clause for keywords dynamically
        keyword_conditions = " OR ".join(
            ["LOWER(bio) LIKE ? OR LOWER(username) LIKE ?" for _ in self.config.keywords]
        )
        params = []
        for keyword in self.config.keywords:
            params.append(f"%{keyword}%")  # For bio
            params.append(f"%{keyword}%")  # For username

        query = f'''
        SELECT *
        FROM users
        WHERE is_scraped = 0 AND ({keyword_conditions})
        LIMIT 1
        '''

        c.execute(query, params)
        user = c.fetchone()

        conn.close()

        if user is None:
            print("All out of users to scrape. Please manually add some new ones. ")
            return "AlexHormozi"

        print("user", user[1])
        return user[1]
        # Returns a tuple of user details or None if no match found

    def set_scraped(self, next_user_to_scrape):
        user = self.get_user(next_user_to_scrape)
        if user is None:
            user = User(username=next_user_to_scrape)
        user.is_scraped = True
        self.update_user(user)

    def get_user_data_for_date(self, date):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
        SELECT username, name, bio, followers, following, is_verified, sourced_from, date_created, total_dms_sent, last_dm_sent, is_scraped
        FROM users
        WHERE last_dm_sent = ?
        ''', (date,))
        users = c.fetchall()
        conn.close()
        return users

    def get_analytics_data(self, start_date, end_date):
        # Mock data for testing
        # Returns dates between start_date and end_date with dummy data
        mock_data = []
        current_date = start_date
        while current_date <= end_date:
            users_from_date = self.get_user_data_for_date(current_date)
            mock_data.append((current_date.strftime("%b %d"), len(users_from_date)))
            current_date += datetime.timedelta(days=1)
        return mock_data[::-1]
