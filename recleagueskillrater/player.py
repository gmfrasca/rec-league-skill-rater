from bs4 import BeautifulSoup
from .season_stats import SeasonStats
from .const import BASEURL


class Player(object):

    def __init__(self, session, player_id, company):
        self.session = session
        self.id = player_id
        self.company = company

        self.soup = self.fetch_stats_page()
        self.name = self.retrieve_name()
        self.seasons = self.retrieve_stats()

    def __repr__(self):
        return f"{self.name:<15}: Max Level {self.max_level}, Weighted Avg Level {self.weighted_avg_level:.3f}"

    def rate(self):
        print(self)

    def rate_seasons(self):
        print(f"=== {self.name} ===")
        for s in self.seasons:
            print(s)
    
    def retrieve_name(self):
        return self.soup.find("h4").text 

    def fetch_stats_page(self):
        stats_url = f"{BASEURL}/dash/index.php?Action=Stats/index&customerID={self.id}&company={self.company}"
        stats_text = self.session.get(stats_url).text
        return BeautifulSoup(stats_text, 'html.parser')

    def parse_season_level(self, season_level_str):
        split = season_level_str.split(" - ")
        return split[0].strip(), split[1].strip()

    def retrieve_stats(self):
        seasons = []

        tables = self.soup.find_all("table")
        historical_seasons = tables[2]
        first = True
        odd_row = False
        season_name = ""
        level = ""  # TODO
        rows = historical_seasons.find_all("tr")
        for tr in rows:
            if first:
                first = False
                continue
            cells = tr.find_all("td")
            if not odd_row:
                season, level = self.parse_season_level(cells[0].text)
            else:
                team_name = cells[0].a.text
                goals = int(cells[1].text)
                assists = int(cells[2].text)
                pim = int(cells[3].text)
                ga = int(cells[4].text)
                sa = int(cells[5].text)
                sv = int(cells[6].text)
                gp = int(cells[7].text)
                ss = SeasonStats(team_name, level, goals, assists, pim, ga, sa, sv, gp)
                seasons.append(ss)
            odd_row = not odd_row
        return seasons

    @property
    def max_level(self):
        max_level = 0
        for s in self.seasons:
            if s.level_rating > max_level:
                max_level = s.level_rating
        return max_level

    @property
    def weighted_avg_level(self):
        sum_lvl = 0
        sum_gp = 0
        for s in self.seasons:
            sum_gp += s.games_played
            sum_lvl += s.games_played * s.level_rating
        if sum_gp == 0:
            return 0
        return sum_lvl / sum_gp

    @property
    def total_stats(self):
        t_goals = 0
        t_assists = 0
        t_pim = 0
        t_ga = 0
        t_sa = 0 
        t_sv = 0
        t_gp = 0
        for s in self.seasons:
            t_goals += s.goals
            t_assists += s.assists
            t_pim += s.pim
            t_ga += s.goals_against
            t_sa += s.shots_against
            t_sv += s.saves
            t_gp += s.games_played
        return SeasonStats("TOTAL", "TOTAL", t_goals, t_assists, t_pim, t_ga, t_sa, t_sv, t_gp)
        

    def print_full_stats(self):
        print(f"Player: {self.name}")
        print("---------------------------")
        for s in self.seasons:
            print(s)
        print("===========================")
        print(self.total_stats)