import inflect
from flask import url_for

from magic import tournaments
from shared import rules

from decksite.view import View

# pylint: disable=no-self-use
class Tournaments(View):
    def __init__(self):

        info = tournaments.next_tournament_info()
        self.next_tournament_name = info['next_tournament_name']
        self.next_tournament_time = info['next_tournament_time']
        self.leaderboards_url = url_for('tournament_leaderboards')

        self.tournaments = tournaments.all_series_info()
        p = inflect.engine()
        self.num_tournaments = p.number_to_words(len(self.tournaments))

        self.bugs_rules = rules.bugs(fmt=rules.HTML)

    def subtitle(self):
        return 'Tournaments'
