import re

from shared import configuration
from magic import fetcher, fetcher_internal

from decksite import translation
from decksite.data import deck, Deck
from decksite.scrapers import decklist

def scrape():
    fetch_decks('penny-dreadful')

def fetch_decks(hub: str):
    login()
    print("Logged in to TappedOut: {0}".format(is_authorised()))
    deckcycle = fetcher.fetch_json("http://tappedout.net/api/deck/latest/{0}/".format(hub))
    return [Deck(merge_deck(d)) for d in deckcycle]

def fetch_deck(slug: str):
    deckinfo = fetcher.fetch_json("http://tappedout.net/api/collection/collection:deck/{0}/".format(slug))
    deck_id = store_deck(deckinfo)
    return deck.load_deck(deck_id)

def merge_deck(blob):
    deck_id = store_deck(translation.translate(translation.TAPPEDOUT, blob))
    d = deck.load_deck(deck_id)
    if is_authorised():
        return fetch_deck(blob.get('slug'))
    return d

def store_deck(blob):
    keys = ['slug', 'name', 'tappedout_username', 'url', 'resource_uri', 'date_updated']
    d = {key: blob.get(key) for key in keys if key in blob.keys()}
    raw_decklist = fetcher.fetch('{base_url}?fmt=txt'.format(base_url=blob['url']))
    d['cards'] = decklist.parse(raw_decklist)
    d['source'] = 'Tapped Out'
    d['identifier'] = d['url']
    return deck.add_deck(d)

def is_authorised():
    return fetcher_internal.SESSION.cookies.get('tapped') is not None

def get_auth():
    cookie = fetcher_internal.SESSION.cookies.get('tapped')
    token = configuration.get("tapped_API_key")
    return fetcher.fetch("http://tappedout.net/api/v1/cookie/{0}/?access_token={1}".format(cookie, token))

def login(user=None, password=None):
    if user is None:
        user = configuration.get('to_username')
    if password is None:
        password = configuration.get('to_password')
    if user == '' or password == '':
        print('No TappedOut credentials provided')
        return
    url = "http://tappedout.net/accounts/login/"
    session = fetcher_internal.SESSION
    response = session.get(url)

    match = re.search(r"<input type='hidden' name='csrfmiddlewaretoken' value='(\w+)' />", response.text)
    if match is None:
        # Already logged in?
        return
    csrf = match.group(1)

    data = {
        'csrfmiddlewaretoken': csrf,
        'next': '/',
        'username': user,
        'password': password,
    }
    headers = {
        'referer': url,
    }
    print("Logging in to TappedOut as {0}".format(user))
    response = session.post(url, data=data, headers=headers)
    if response.status_code == 403:
        print("Failed to log in")
