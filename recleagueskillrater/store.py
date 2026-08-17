import datetime


REFRESH_THRESHOLD = 24 * 60 * 60  # one day


class PlayerStore:
    class PlayerEntry:
        def __init__(self, player, refresh_threshold=REFRESH_THRESHOLD):
            self.player = player
            self.refreshed_at = datetime.datetime.now()
            self.refresh_threshold = refresh_threshold

        def data_is_expired(self):
            return self.refreshed_at.total_seconds() + self.refresh_threshold > datetime.datetime.now().total_seconds()

    def __init__(self):
        self.players = {}

    def set_player(self, player_id, player):
        self.players[player_id] = PlayerEntry(player)

    def get_player(self, player_id):
        player = self.players.get(player_id)
        if player_id is None or player.data_is_expired():
            return None
        return player.player
