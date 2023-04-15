import json
import os

import tweepy


def create_credentials_file():
    credentials = {
        'CONSUMER_KEY': input('Enter your Consumer Key: '),
        'CONSUMER_SECRET': input('Enter your Consumer Secret: '),
        'ACCESS_KEY': input('Enter your Access Key: '),
        'ACCESS_SECRET': input('Enter your Access Secret: ')
    }

    with open('twitter_credentials.json', 'w') as cred_data:
        json.dump(credentials, cred_data)

    return credentials


def authenticate_twitter(credentials):
    auth = tweepy.OAuthHandler(credentials['CONSUMER_KEY'], credentials['CONSUMER_SECRET'])
    auth.set_access_token(credentials['ACCESS_KEY'], credentials['ACCESS_SECRET'])
    return tweepy.API(auth)


def main():
    # Check for the existence of the credentials file
    if not os.path.exists('twitter_credentials.json'):
        print('twitter_credentials.json not found. Follow the instructions to create it:')
        print('1. Go to https://developer.twitter.com and create an App.')
        print('2. Obtain the Consumer Key, Consumer Secret, Access Key, and Access Secret.')
        print('3. Enter the credentials when prompted.\n')
        credentials = create_credentials_file()
    else:
        with open('twitter_credentials.json') as cred_data:
            credentials = json.load(cred_data)

    api = authenticate_twitter(credentials)

    while True:
        print('\nChoose an option:')
        print('1 - Get stats')
        print('2 - Backup')
        print('3 - Backup and Delete')
        print('q - Quit')

        choice = input('Enter your choice: ')

        if choice == '1':
            # Implement the 'Get stats' function
            pass
        elif choice == '2':
            # Implement the 'Backup' function
            pass
        elif choice == '3':
            # Implement the 'Backup and Delete' function
            pass
        elif choice.lower() == 'q':
            break
        else:
            print('Invalid choice. Please try again.')


if __name__ == '__main__':
    main()
