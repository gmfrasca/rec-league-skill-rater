SKILL_LEVEL_MAPPING = {
    "D League": 1,
    "Lower C": 2,
    "Intermediate C": 3,
    "Upper C": 4,
    "Lower B": 5,
    "Upper B": 6,
    "A League": 7
}

class SeasonStats(object):

    def __init__(self, team_name, level, goals=0, assists=0, pim=0, goals_against=0, shots_against=0, saves=0, games_played=0):
        self.team_name = team_name
        self.level = level
        self.goals = goals
        self.assists = assists
        self.pim = pim
        self.goals_against = goals_against
        self.shots_against = shots_against
        self.saves = saves
        self.games_played = games_played

    def __repr__(self):
        return f"{self.team_name:<15} ({self.level_rating} - {self.level:<15}): {self.goals:>3} G, {self.assists:>3} A, {self.pim:>3} PIM, {self.goals_against:>3} GA, {self.shots_against:>3} SA, {self.saves:>3} SV, {self.games_played:>3} GP"

    @property
    def level_rating(self):
        default_mapping = 3
        return SKILL_LEVEL_MAPPING.get(self.level, default_mapping)
