from flask import url_for

from shared.database import sqlescape

from decksite.data import card
from decksite.view import View

# pylint: disable=no-self-use
class Person(View):
    def __init__(self, person):
        self.person = person
        self.decks = person.decks
        self.hide_person = True
        self.cards = card.played_cards('d.person_id = {person_id}'.format(person_id=sqlescape(person.id)))
        self.only_played_cards = card.only_played_by(person.id)
        self.has_only_played_cards = len(self.only_played_cards) > 0
        for record in person.head_to_head:
            record.show_record = True
            record.opp_url = url_for('person', person_id=record.opp_mtgo_username)
        self.show_head_to_head = len(person.head_to_head) > 0

    def __getattr__(self, attr):
        return getattr(self.person, attr)

    def subtitle(self):
        return self.person.name
