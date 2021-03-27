"""
Author: John Chubey

Creates an NHL API that retrieves and handles player stats from the unofficial NHL API.

This module is responsible for initializing a running a Flask API, which is used to retrieve NHL stats from the
unofficial NHL API, and handle the data quickly and efficiently. Because of the way the unofficial NHL API is
programmed, this API had to be created to handle player stat retrieval. Results are cached to make subsequent
API calls faster. Also, multiprocessing is used to reduce the time required to retrieve player stats due to many
required API calls.
"""

from functools import partial

from flask import Flask, jsonify
import requests
import itertools
from multiprocessing import Pool

from flask_cors import CORS
from flask_caching import Cache

from utils import stats_exist, filter_player_data

cache = Cache(config={'CACHE_TYPE': 'simple'})

app = Flask(__name__)
cache.init_app(app)
CORS(app)

BASE_URL = 'https://statsapi.web.nhl.com'
CURRENT_SEASON_URL = 'https://statsapi.web.nhl.com/api/v1/seasons/current'
TEAMS_URL = 'https://statsapi.web.nhl.com/api/v1/teams?expand=team.roster'


def get_players_from_teams(team):
    """
    Get team roster and from a specific 'team' dictionary.

    Args:
        team: A dictionary containing all information for a specific team.
    Returns:
        A list of player objects that play for the specific team.
    Raises:
        No errors raised.
    """
    roster = team.get('roster', dict()).get('roster', [])
    return roster


def get_player_stats_object(player_stats_list):
    """
    Retrieve the player stat data from a specific player list.

    Player stat data is returned from the unofficial NHL API as a list. This function parses through the list and
    retrieves the actual stat object. Basically it navigates through the JSON object returned by the unofficial NHL
    API to retrieve the actual stats.

    Args:
        player_stats_list: A JSON object returned from the unofficial NHL API containing the player stats.
    Returns:
        A dictionary containing the stats of the player if the stats exist, otherwise returns a dictionary with an error
        key and value.
    Raises:
        No errors raised.
    """
    if player_stats_list:
        stats_object = player_stats_list[0].get('splits', None)
        if stats_object:
            return stats_object[0].get('stat', dict())
        else:
            return {'error': 'Stats failed to be retrieved'}
    else:
        return {'error': 'Stats failed to be retrieved'}


def get_custom_player_data(player, season='20182019'):
    """
    Retrieve and combine all player information for a specific player from a specific season.

    This function makes an API call to the unofficial NHL API, and combines all the data related to a specific player
    into a single python dictionary.

    Args:
        player: A dictionary with player information, excluding stats.
        season: The particular season the stats are being retrieved for.
    Returns:
        A dictionary representing a player's stats and other extra information. If the API response is bad, returns a
        dictionary with an error key or value.
    Raises:
        No errors raised.
    """
    person = player.get('person', {'error': 'Person not found'})
    id = player.get('person', dict()).get('id', 0000000)
    player_stats_response = requests.get(BASE_URL + '/api/v1/people/' + str(id) + '/stats' + '?stats=statsSingleSeason&season=' + season)
    if player_stats_response.status_code == 200:
        player_stats_list = player_stats_response.json().get('stats', None)
        if not stats_exist(player_stats_list):
            return
        if person.get('fullName') == 'Johnny Boychuk': #################################### REMOVE THIS IF STATEMENT
            print(id)
        player_stats = get_player_stats_object(player_stats_list)
        return {
            'player': person,
            'stats': player_stats,
            'position': player.get('position', dict()),
        }
    else:
        return {'error': 'Problem retrieving player stats '}

def get_season(season=None):
    """
    Gets an NHL season.

    Gets a designated NHL season. If a season isn't provided, the current season is retrieved.

    Args:
        season: A string representing a specific season.
    Returns:
        A string representing an NHL season.
    Raises:
        No errors raised.
    """
    if season is None:
        current_season_response = requests.get(CURRENT_SEASON_URL)
        if current_season_response.status_code == 200:
            return current_season_response.json().get('seasons')[0].get('seasonId', '20192020')
        else:
            return '20182019'
    elif len(season) == 8 and season.isdigit():
        return season
    else:
        return '20182019'


@app.route("/players")
@cache.cached(timeout=600)
def get_player_stats():
    """
    An API endpoint that pulls and handles NHL player stat data.

    This endpoint pulls the rosters from all teams. Then for each player, all stats are gathered and combined into a
    single object. These objects are combined into a list which is returned to the frontend. This endpoint data is
    cached to increase the speed of subsequent requests. Also, multiprocessing is used to make concurrent API requests
    to gather all the player stats quickly.

    Args:
        No arguments
    Returns:
        A python list converted to JSON data representing all the stats and extra info of every NHL player.
    Raises:
        No errors raised.
    """
    current_season = get_season()
    teams_response = requests.get(TEAMS_URL)
    if teams_response.status_code == 200:
        teams = teams_response.json()
        worker_pool = Pool(60)
        all_players = list(itertools.chain.from_iterable(worker_pool.map(get_players_from_teams, teams.get('teams', []))))
        custom_player_data_function = partial(get_custom_player_data, season=current_season)
        custom_player_data = list(worker_pool.map(custom_player_data_function, all_players))
        return jsonify(filter_player_data(custom_player_data))
    else:
        return jsonify([])
