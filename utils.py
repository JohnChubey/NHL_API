def stats_exist(player_stats_list):
    """
    Check if the player has valid stats.

    Args:
        player_stats_list: A list containing all stats objects for a particular player returned from the API.
    Returns:
        A boolean value based on whether the player has valid stats or not.        
    Raises:
        No errors raised.
    """
    if len(player_stats_list) > 0:
        splits = player_stats_list[0].get('splits', [])
        if len(splits) > 0:
            return True
    return False


def filter_player_data(custom_player_data):
    """
    Filters final player data to remove specific entries.

    This function should be used to remove undesired values in the data, such as a None value.
    Args:
        custom_player_data: A list of data for each player, including their stats and personal information.
    Returns:
        A filtered list based off the given function.
    Raises:
        No errors raised.
    """
    return list(filter(lambda player_stat : player_stat is not None, custom_player_data))
