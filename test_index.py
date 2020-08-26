"""
Tests out functionality of main index.py file.

This module contains a series of various unit tests which test out the functionality of the player stats API. Included
in this module are unit tests that ensure the various helper functions required to retrieve and handle player stats
are functioning properly.
"""
from index import *


def test_get_season():
    """
    Tests to ensure the 'get_season' function returns a correct season string.

    Args:
        No arguments in this function.
    Returns:
        No return value, void.
    Raises:
        Assertion error raised if assertion is incorrect.
    """
    assert get_season() is not None
    assert get_season('20142015') is not None


def test_get_players_from_teams():
    """
    Tests to ensure the 'get_players_from_teams' function returns either a list full of players, or an empty list.

    Args:
        No arguments in this function.
    Returns:
        No return value, void.
    Raises:
        Assertion error raised if assertion is incorrect.
    """
    assert get_players_from_teams(dict()) == list()
    fake_team = {
        'roster': {'test': 'not a roster'}
    }
    assert get_players_from_teams(fake_team) == list()


def test_get_custom_player_data():
    """
    Tests to ensure the 'get_custom_player_data' function returns a dictionary with either a dictionary with the
    combined stats and information of each player, or a dictionary with an error key and value.

    Args:
        No arguments in this function.
    Returns:
        No return value, void.
    Raises:
        Assertion error raised if assertion is incorrect.
    """
    assert get_custom_player_data(dict()) == {'error': 'Problem retrieving player stats '}
    real_player_object = {
        'person': {'id': 8474697}
    }
    player_object = get_custom_player_data(real_player_object)
    assert player_object.get('error', None) is None
    assert player_object.get('player', None) is not None
    assert player_object.get('stats', None) is not None
    assert player_object.get('position', None) is not None


def test_get_player_stats_object():
    """
    Tests to ensure the 'get_player_stats_object' function returns either a dictionary containing the stats of a player,
    or a dictionary containing an error key and value.

    Args:
        No arguments in this function.
    Returns:
        No return value, void.
    Raises:
        Assertion error raised if assertion is incorrect.
    """
    assert get_player_stats_object(None) == {'error': 'Stats failed to be retrieved'}
    test_list = [{
        'splits': [{
            'season': '20192020',
            'stat': {'goals': 10},
        }]
    }]
    assert get_player_stats_object(test_list) is not None

    test_bad_list = [{
        'bad_data': [{
            'season': '22423sdfsf',
        }]
    }]
    assert get_player_stats_object(test_bad_list) == {'error': 'Stats failed to be retrieved'}
