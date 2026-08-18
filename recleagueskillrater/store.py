from .player import Player
import datetime
import logging

REFRESH_THRESHOLD = 24 * 60 * 60  # one day


class PlayerEntry(object):
    def __init__(self, player, refresh_threshold=REFRESH_THRESHOLD):
        self.player = player
        self.refreshed_at = datetime.datetime.now()
        self.refresh_threshold = refresh_threshold

    def data_is_expired(self):
        return self.refreshed_at.total_seconds() + self.refresh_threshold > datetime.datetime.now().total_seconds()


class PlayerStore(object):
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.players = {}

    def set_player(self, player_id, player):
        self.players[player_id] = PlayerEntry(player)

    def get_player(self, session, player_id, company):
        player_entry = self.players.get(player_id)
        if player_entry is not None:
            if not player_entry.data_is_expired():
                self._logger.debug(f"Player {player_id} already in store.")
                player = player_entry.player
            else:
                self._logger.debug(f"Player {player_id} found but data is stale")
                player = Player(session, player_id, company)
                self.set_player(player_id, player)
        else:
            self._logger.debug(f"No player {player_id} in PlayerStore")
            player = Player(session, player_id, company)
            self.set_player(player_id, player)
        return player

# Singletons
player_store = PlayerStore()