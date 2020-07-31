from functools import partial

from flask import Flask, jsonify
import requests
import itertools
from multiprocessing import Pool

app = Flask(__name__)

BASE_URL = 'https://statsapi.web.nhl.com'
CURRENT_SEASON_URL = 'https://statsapi.web.nhl.com/api/v1/seasons/current'
TEAMS_URL = 'https://statsapi.web.nhl.com/api/v1/teams?expand=team.roster'


def get_players_from_teams(team):
    roster = team.get('roster', dict()).get('roster', [])
    return roster


def get_custom_player_data(team, season='20182019'):
    return []


def get_season(season=None):
    if season is None:
        current_season_response = requests.get(CURRENT_SEASON_URL)
        if current_season_response.status_code == 200:
            return current_season_response.json().get('seasons')[0].get('seasonid', '20192020')
        else:
            return '20182019'


@app.route("/players")
def get_player_stats():
    current_season = get_season()
    teams_response = requests.get(TEAMS_URL)
    if teams_response.status_code == 200:
        teams = teams_response.json()
        worker_pool = Pool(5)
        all_players = list(itertools.chain.from_iterable(worker_pool.map(get_players_from_teams, teams.get('teams', []))))
        custom_player_data_function = partial(get_custom_player_data, season=current_season)
        custom_player_data = list(itertools.chain.from_iterable(worker_pool.map(custom_player_data_function, all_players)))
        return jsonify(all_players)
    else:
        return []

