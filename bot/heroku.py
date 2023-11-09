import psycopg2

from typing import cast, List
from bot.userdata import CCT

class Tweet:
    def __init__(self, id, text, actioned):
        self.id = id
        self.text = text
        self.actioned = actioned


def database_connect(context: CCT) -> psycopg2.extensions.connection:
    """Connects to the database.

    Args:
        context: The callback context as provided by the application.
    """
    conn = psycopg2.connect(
        user=context.application.bot_data["DB_USER"],
        password=context.application.bot_data["DB_PASSWORD"],
        host=context.application.bot_data["DB_HOST"],
        port="5432",
        database=context.application.bot_data["DB_NAME"],
    )
    return conn


def create_table(context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    create_table_query = """CREATE TABLE AccessCodes (
        access_code TEXT PRIMARY KEY,
        generated_by_user TEXT,
        user_id TEXT DEFAULT NULL,
        date TEXT,
        used BOOLEAN
    );"""

    cursor.execute(create_table_query)

    connection.commit()
    cursor.close()

def retrieve_access_tokens(context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM AccessCodes")

    result = cursor.fetchall()
    cursor.close()
    return result

def use_access_code(access_code: str, context: CCT) -> bool:
    connection = database_connect(context)
    cursor = connection.cursor()

    # Check if access_code exists and was not used
    cursor.execute("SELECT * FROM AccessCodes WHERE access_code = %s AND used is FALSE", (access_code,))
    result = cursor.fetchone()

    # Mark access_code as used if it was found and not used yet
    if result is not None:
        cursor.execute("UPDATE AccessCodes SET used = TRUE WHERE access_code = %s", (access_code,))
        connection.commit()
        return True

    cursor.close()
    return False


def add_access_tokens(access_code: str, generated_by_user: str, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO AccessCodes (access_code, generated_by_user, date, used) VALUES (%s, %s, NOW(), FALSE)",
       (access_code, generated_by_user)
    )

    connection.commit()
    cursor.close()



def insert_tweets(tweet_id, twitter_id, tg_id, tweet, likes, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    update_user_query = """UPDATE users SET twitter_id = %s WHERE id = %s"""
    cursor.execute(update_user_query, (twitter_id, tg_id))

    insert_tweet_query = """INSERT INTO tweets (ID, TWITTER_ID, TWEET, LIKES) VALUES (%s, %s, %s, %s) ON CONFLICT (ID) DO NOTHING"""
    data_tuple = (tweet_id, twitter_id, tweet, likes)
    cursor.execute(insert_tweet_query, data_tuple)

    connection.commit()
    cursor.close()


def set_num_tweets(context: CCT, user_id: int, num_tweets: int):
    connection = database_connect(context)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET NUM_TWEETS = %s WHERE id = %s;", (num_tweets, user_id)
    )

    connection.commit()
    cursor.close()


def get_num_tweets(context: CCT, user_id: int):
    connection = database_connect(context)
    cursor = connection.cursor()

    cursor.execute("SELECT NUM_TWEETS FROM users WHERE id = %s;", (user_id,))
    row = cursor.fetchone()

    connection.commit()
    cursor.close()

    if row:
        return row[0]
    return None


def update_table(context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    alter_table_query = """ALTER TABLE users
                          ADD COLUMN IF NOT EXISTS JWT TEXT NULL;"""
    cursor.execute(alter_table_query)

    connection.commit()
    cursor.close()


def delete_data(user_id, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    delete_tweets_query = f"""DELETE FROM tweets WHERE ID = {user_id}"""
    cursor.execute(delete_tweets_query)

    delete_user_query = f"""DELETE FROM users WHERE ID = {user_id}"""
    cursor.execute(delete_user_query)

    connection.commit()
    cursor.close()


def insert_data(user_id, username, access_token, access_secret, num_tokens, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    # stripe_id, subscription = stripe_api(user_id, username)
    subscription = "none"

    insert_query = """
    INSERT INTO users (id, username, access_token, access_secret, subscription, num_tokens)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (id)
    DO UPDATE SET username = EXCLUDED.username, access_token = EXCLUDED.access_token, access_secret = EXCLUDED.access_secret, subscription = EXCLUDED.subscription, num_tokens = EXCLUDED.num_tokens;
    """
    cursor.execute(insert_query, (user_id, username, access_token, access_secret, subscription, num_tokens))

    connection.commit()
    cursor.close()


def insert_friendtech_data(user_id, jwt, address, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    query = "UPDATE users SET jwt = %s, address = %s WHERE id = %s"
    params = (jwt, address, user_id)
    cursor.execute(query, params)

    connection.commit()

    cursor.close()


def insert_basic_data(user_id, username, access_token, access_secret, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    insert_query = f"""INSERT INTO users (ID, USERNAME, ACCESS_TOKEN, ACCESS_SECRET, SUBSCRIPTION, ) VALUES ({user_id}, '{username}', '{access_token}', '{access_secret}', '{subscription}', '{stripe_id}')"""
    cursor.execute(insert_query)

    connection.commit()
    cursor.close()


def get_data(user_id, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    select_query = f"""SELECT USERNAME, ACCESS_TOKEN, ACCESS_SECRET, NUM_TOKENS, JWT, ADDRESS FROM users WHERE ID = {user_id}"""
    cursor.execute(select_query)

    records = cursor.fetchall()
    if not records:
        return None
    cursor.close()

    return records


def get_all_data(context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    select_query = f"""SELECT * FROM users"""
    cursor.execute(select_query)

    column_names = [desc[0] for desc in cursor.description]
    records = cursor.fetchall()
    cursor.close()

    return [dict(zip(column_names, record)) for record in records]


def delete_all_data(context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    delete_user_query = f"""DELETE FROM users"""
    cursor.execute(delete_user_query)

    connection.commit()
    cursor.close()

def get_twitter_data(user_id, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    select_query = (
        f"""SELECT ACCESS_TOKEN, ACCESS_SECRET FROM users WHERE ID = {user_id}"""
    )
    cursor.execute(select_query)

    records = cursor.fetchall()
    cursor.close()

    return records



def fetch_user_tweets(twitter_id, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    # select_query = """SELECT twitter_id FROM users WHERE id = %s"""
    # cursor.execute(select_query, (tg_id,))

    # record = cursor.fetchone()[0]

    select_query = """SELECT tweet, likes FROM tweets WHERE twitter_id = %s"""
    cursor.execute(select_query, (twitter_id,))

    tweets = cursor.fetchall()
    cursor.close()

    return tweets


def remove_one_time_payment(tg_id, one_time_payment, context):
    connection = database_connect(context)
    cursor = connection.cursor()

    if tg_id != "1574952849":
        update_query = "UPDATE users SET ONE_TIME_PAYMENT=%s WHERE ID=%s;"
        cursor.execute(update_query, (one_time_payment, tg_id))

    connection.commit()
    cursor.close()


def fetch_all_twitter_ids(context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    select_query = "SELECT twitter_id FROM users"
    cursor.execute(select_query)

    records = cursor.fetchall()
    cursor.close()

    twitter_ids = [id_tuple[0] for id_tuple in records]
    return twitter_ids


def fetch_user_twitter_id(tg_id, context: CCT):
    connection = database_connect(context)
    cursor = connection.cursor()

    select_query = """SELECT twitter_id FROM users WHERE id = %s"""
    cursor.execute(select_query, (tg_id,))

    record = cursor.fetchone()[0]
    cursor.close()

    return record


def pull_and_action_tweets(context: CCT):
    conn = database_connect(context)
    cur = conn.cursor()

    # Fetch unactioned tweets
    cur.execute("SELECT * FROM tweets WHERE actioned=false LIMIT 5")
    rows = cur.fetchall()

    # Built query to update fetched rows
    ids = [str(x[0]) for x in rows]
    if ids:
        cur.execute(f"UPDATE tweets SET actioned=true WHERE id IN ({','.join(ids)})")

    conn.commit()

    cur.close()
    conn.close()

    return [Tweet(id, text, actioned) for id, text, actioned in rows]
