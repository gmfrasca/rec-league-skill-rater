from .player import Player
import datetime
import logging
import pickle


REFRESH_THRESHOLD = 24 * 60 * 60  # one day


class PlayerEntry(object):
    def __init__(self, player, refresh_threshold=REFRESH_THRESHOLD):
        self.player = player
        self.refreshed_at = datetime.datetime.now()
        self.refresh_threshold = datetime.timedelta(seconds=refresh_threshold)

    def data_is_expired(self):
        ref_by = self.refreshed_at + self.refresh_threshold
        return ref_by < datetime.datetime.now()


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
                self._logger.info(f"Player {player_id} already in store.")
                player = player_entry.player
            else:
                self._logger.info(f"Player {player_id} found but data is stale")
                player = Player(session, player_id, company)
                self.set_player(player_id, player)
        else:
            self._logger.info(f"No player {player_id} in PlayerStore")
            player = Player(session, player_id, company)
            self.set_player(player_id, player)
        return player

    def to_pickle(self, dest_file):
        with open(dest_file, "wb") as file:
            pickle.dump(self.players, file)

    def from_pickle(self, src_file):
        with open(src_file, "rb") as file:
            self.players = pickle.load(file)


# Singletons
player_store = PlayerStore()