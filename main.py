import json
import os

import requests

user_info_url = "https://api.twitter.com/2/users/by"

def load_credentials_from_file():
    with open('twitter_credentials.json', 'r') as f:
        credentials = json.load(f)
    return credentials



def set_environment_variables(credentials):
    os.environ['API_KEY'] = credentials['API_KEY']
    os.environ['API_SECRET_KEY'] = credentials['API_SECRET_KEY']
    os.environ['ACCESS_TOKEN'] = credentials['ACCESS_TOKEN']
    os.environ['ACCESS_TOKEN_SECRET'] = credentials['ACCESS_TOKEN_SECRET']
    os.environ['BEARER_TOKEN'] = credentials['BEARER_TOKEN']

    # Logging statements to check if the environment variables are set correctly
    print("API_KEY:", os.environ['API_KEY'])
    print("API_SECRET_KEY:", os.environ['API_SECRET_KEY'])
    print("ACCESS_TOKEN:", os.environ['ACCESS_TOKEN'])
    print("ACCESS_TOKEN_SECRET:", os.environ['ACCESS_TOKEN_SECRET'])
    print("BEARER_TOKEN:", os.environ['BEARER_TOKEN'])


def create_credentials():
    print("Please provide the following keys and tokens from the Twitter Developer Portal:")
    credentials = {
        'API_KEY': input(
            'Enter your Consumer API Key (found under "Consumer Keys" > "API Key and Secret" > "API Key"): '),
        'API_SECRET_KEY': input(
            'Enter your Consumer API Secret Key (found under "Consumer Keys" > "API Key and Secret" > "API Secret"): '),
        'ACCESS_TOKEN': input(
            'Enter your Access Token (found under "Authentication Tokens" > "Access Token and Secret" > "Access Token"): '),
        'ACCESS_TOKEN_SECRET': input(
            'Enter your Access Token Secret (found under "Authentication Tokens" > "Access Token and Secret" > "Access Token Secret"): '),
        'BEARER_TOKEN': input('Enter your Bearer Token (found under "Authentication Tokens" > "Bearer Token"): ')
    }
    with open('twitter_credentials.json', 'w') as cred_data:
        json.dump(credentials, cred_data)
    set_environment_variables(credentials)
    return credentials


def bearer_oauth(r):
    bearer_token = os.environ.get("BEARER_TOKEN")
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def get_stats():
    twitter_handle = input("Please enter the Twitter handle (without @): ")
    query_params = {"usernames": twitter_handle, "user.fields": "public_metrics"}

    json_response = connect_to_endpoint(user_info_url, query_params)
    user = json_response['data'][0]
    print(f"Username: {user['username']}")
    print(f"Name: {user['name']}")
    print(f"Followers: {user['public_metrics']['followers_count']}")
    print(f"Following: {user['public_metrics']['following_count']}")
    print(f"Number of tweets: {user['public_metrics']['tweet_count']}")


def view_backup(file_name):
    if not os.path.exists(file_name):
        print(f"Backup file {file_name} not found.")
        return

    with open(file_name, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)

    print("User stats:")
    for key, value in backup_data['user_stats'].items():
        print(f"{key}: {value}")

    print("\nTweets:")
    for tweet in backup_data['tweets']:
        print(f"[{tweet['created_at']}] {tweet['id']}: {tweet['text']}")


def backup_tweets(oauth, file_name='tweets_backup.json'):
    all_tweets = []
    user_id = oauth.get("https://api.twitter.com/1.1/account/verify_credentials.json").json()["id"]

    response = oauth.get(f"https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={user_id}&count=200")
    statuses = response.json()

    for status in statuses:
        all_tweets.append({
            'id': status['id'],
            'created_at': status['created_at'],
            'text': status['text']
        })

    user = oauth.get("https://api.twitter.com/1.1/account/verify_credentials.json").json()
    backup_data = {
        'user_stats': {
            'username': user['screen_name'],
            'name': user['name'],
            'followers': user['followers_count'],
            'following': user['friends_count'],
            'number_of_tweets': user['statuses_count']
        },
        'tweets': all_tweets
    }

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2)

    print(f"Backup completed. Saved {len(all_tweets)} tweets to {file_name}")


def delete_tweets(oauth):
    deleted_tweets = 0
    user_id = oauth.get("https://api.twitter.com/1.1/account/verify_credentials.json").json()["id"]

    response = oauth.get(f"https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={user_id}&count=200")
    statuses = response.json()

    for status in statuses:
        try:
            oauth.delete(f"https://api.twitter.com/1.1/statuses/destroy/{status['id']}.json")
            deleted_tweets += 1
            print(f"Deleted tweet with ID {status['id']}")
        except Exception as e:
            print(f"Error deleting tweet with ID {status['id']}: {e}")
    print(f"Deleted {deleted_tweets} tweets")


def backup_and_delete_tweets():
    backup_tweets(file_name='tweets_backup_before_deletion.json')
    delete_tweets()


def main():
    print("Welcome to the Twitter Stats application!")
    print("Follow the instructions to set your credentials if you haven't already.\n")

    if not os.environ.get('BEARER_TOKEN'):
        if not os.path.exists('twitter_credentials.json'):
            print("Credentials not found in environment variables. Follow the instructions to set them:")
            print("1. Go to https://developer.twitter.com and create an App.")
            print("2. Obtain the API Key, API Secret Key, Access Token, Access Token Secret, and Bearer Token.")
            print("3. Enter the credentials when prompted.\n")
            credentials = create_credentials()
        else:
            credits = load_credentials_from_file()
            set_environment_variables(credits)

    else:
        credentials = {
            'API_KEY': os.environ['API_KEY'],
            'API_SECRET_KEY': os.environ['API_SECRET_KEY'],
            'ACCESS_TOKEN': os.environ['ACCESS_TOKEN'],
            'ACCESS_TOKEN_SECRET': os.environ['ACCESS_TOKEN_SECRET'],
            'BEARER_TOKEN': os.environ['BEARER_TOKEN']
        }

    while True:
        print('\nChoose an option:')
        print('0 - View backup')
        print('1 - Get stats')
        print('2 - Backup')
        print('3 - Backup and Delete')
        print('q - Quit')

        choice = input('Enter your choice: ')

        if choice == '0':
            file_name = input("Enter the backup file name (default: tweets_backup.json): ") or 'tweets_backup.json'
            view_backup(file_name)
        elif choice == '1':
            get_stats()
        elif choice == '2':
            backup_tweets()
        elif choice == '3':
            backup_and_delete_tweets()
        elif choice.lower() == 'q':
            break
        else:
            print('Invalid choice. Please try again.')


if __name__ == '__main__':
    main()
