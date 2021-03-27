def stats_exist(player_stats_list):
    if len(player_stats_list) > 0:
        splits = player_stats_list[0].get('splits', [])
        if len(splits) > 0:
            return True
    return False


def filter_player_data(custom_player_data):
    return list(filter(lambda player_stat : player_stat is not None, custom_player_data))
