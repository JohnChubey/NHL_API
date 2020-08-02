import time
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


def get_player_stats_object(response):
    player_stats_list = response.json().get('stats', None)
    if player_stats_list:
        stats_object = player_stats_list[0].get('splits', None)
        if stats_object:
            return stats_object[0].get('stat', dict())
        else:
            return {'error': 'Stats failed to be retrieved'}
    else:
        return {'error': 'Stats failed to be retrieved'}


def get_custom_player_data(player, season='20182019'):
    person = player.get('person', {'error': 'Person not found'})
    id = player.get('person', dict()).get('id', 0000000)
    player_stats_response = requests.get(BASE_URL + '/api/v1/people/' + str(id) +'/stats' + '?stats=statsSingleSeason&season=' + season)
    if player_stats_response.status_code == 200:
        player_stats = get_player_stats_object(player_stats_response)
        return {
            'player': person,
            'stats': player_stats,
            'position': player.get('position', dict()),
        }
    else:
        return {'error': 'Problem connecting to API'}


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
        worker_pool = Pool(60)
        all_players = list(itertools.chain.from_iterable(worker_pool.map(get_players_from_teams, teams.get('teams', []))))
        custom_player_data_function = partial(get_custom_player_data, season=current_season)
        print('Start searching...')
        start_time = time.time()
        custom_player_data = list(worker_pool.map(custom_player_data_function, all_players))
        print('Finished searching.')
        print('Total time:', time.time() - start_time)
        return jsonify(custom_player_data)
    else:
        return []

