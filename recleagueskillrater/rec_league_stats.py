from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import requests
import getpass

# URLS
URL = "https://apps.daysmartrecreation.com/"
LOGIN_EXT = "dash/jsonapi/api/v1/customer/auth/token?company="
STATS_EXT = "dash/index.php?Action=Stats/index&customerID="
TEAM_STATS_EXT = "dash/index.php?Action=Element/Stats/team_stats&hideForm=false&teamID="
LOGIN_PAGE = f"{URL}{LOGIN_EXT}"
STATS_PAGE = f"{URL}{STATS_EXT}"
TEAM_PAGE = f"{URL}{TEAM_STATS_EXT}"

# Session
session = requests.Session()
a = requests.adapters.HTTPAdapter(max_retries=5)
session.mount('http://', a)
session.mount('https://', a)

# Variables
SKILL_LEVEL_MAPPING = {
    "D League": 1,
    "Lower C": 2,
    "Intermediate C": 3,
    "Upper C": 4,
    "Lower B": 5,
    "Upper B": 6,
    "A League": 7
}


class League(object):

    def __init__(self, teams=[], name="<Unknown League>"):
        self.teams = teams
        self.name = name

    # TODO: figure out a way to get these instead of going indirectly through a team page
    #def fetch_league_page(self):
    #    league_url = f"{URL}dash/x/#/online/{self.company}/leagues/{self.id}"
    #    league_url = f"{URL}dash/index.php?Action=League/index&company={self.company}&league={self.id}"
    #    league_page = session.get(league_url).text
    #    return BeautifulSoup(league_page, 'html.parser')

    #def retrieve_name(self):
    #    print(self.soup)
    #    return self.soup.find("h2").text

    #def retrieve_teams(self):
    #    teams = []
    #    standings_div = self.soup.find("div", {"class": "standings"})
    #    standings_table = standings_div.find("table", {"class": "dataTable"})
    #    print(standings_table.text)

    def rate(self):
        print(f"{self.name:>15}: Skill {self.avg_weighted_skill:.3f}")

    def rate_teams(self):
        for t in self.teams:
            t.rate()

    @property
    def avg_weighted_skill(self):
        avg_skill = 0
        for t in self.teams:
            avg_skill += t.avg_weighted_skill
        return avg_skill / len(self.teams)


class Team(object):
    
    def __init__(self, team_id, company):
        self.id = team_id
        self.company = company

        self.soup = self.fetch_team_page()
        self.name = self.retrieve_name()
        self.players = self.retrieve_players()

    def fetch_team_page(self, team_url=TEAM_PAGE):
        team_page = session.get(f"{team_url}{self.id}&company={self.company}").text
        return BeautifulSoup(team_page, 'html.parser')

    def retrieve_name(self):
        return self.soup.find("h2").text

    def retrieve_players(self):
        players = []
        tstat_table = self.soup.find("div", {"id": "teamStats"})
        rows = tstat_table.find_all("tr")
        for tr in rows:
            attrs = tr.attrs
            id = attrs.get('id')
            if id and 'cust' in id:
                player_id = id[4:]
                try:
                    players.append(Player(player_id, self.company))
                except:
                    pass  # TODO Handle Error (example: stats not available for minor players)

        return players
        
    def rate(self):
        print(f"{self.name:>15}: Skill {self.avg_weighted_skill:.3f}")

    def get_league(self):
        teams, league_name = self.retrieve_teams_in_league()
        return League(teams=teams, name=league_name)


    def retrieve_teams_in_league(self):
        teams = []
        standings_table = self.soup.find_all("table")[1]
        league_name = standings_table.find_all("th")[0].text.split(":")[1].strip()

        team_links=standings_table.find_all("a")
        for l in team_links:
            href = l['href']
            parsed = urlparse(href)
            team_id = parse_qs(parsed.query)['teamID'][0]
            teams.append(Team(team_id, self.company))
        return teams, league_name

    @property
    def avg_weighted_skill(self):
        avg_skill = 0
        for p in self.players:
            avg_skill += p.weighted_avg_level
        return avg_skill / len(self.players)

    def print_roster(self):
        for p in self.players:
            print(p)

    def rate_player(self, player_id):
        Player(player_id, self.company).rate()

class Player(object):

    def __init__(self, player_id, company):
        self.id = player_id
        self.company = company

        self.soup = self.fetch_stats_page()
        self.name = self.retrieve_name()
        self.seasons = self.retrieve_stats()

    def __repr__(self):
        return f"{self.name:<15}: Max Level {self.max_level}, Weighted Avg Level {self.weighted_avg_level:.3f}"

    def rate(self):
        print(self)
    
    def retrieve_name(self):
        return self.soup.find("h4").text 

    def fetch_stats_page(self, stats_url=STATS_PAGE):
        stats_text = session.get(f"{stats_url}{self.id}&company={self.company}").text
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


class RecLeagueStats(object):
    
    def __init__(self, company):
        self.company = company

    def login(self, username, password, url=LOGIN_PAGE):
        login_payload = {
            "grant_type": "client_credentials",
            "client_id": username,
            "client_secret": password,
            "stay_signed_in": True,
            "company": self.company,
            "company_code": self.company
        }
        r = session.post(f"{url}{self.company}", data=login_payload)

    def rate_player(self, player_id):
        self.get_player(player_id).rate()

    def rate_team(self, team_id):
        self.get_team(team_id).rate()

    def rate_teams_league(self, team_id):
        self.get_teams_league(team_id).rate()

    def get_team(self, team_id):
        return Team(team_id, self.company)

    def get_player(self, player_id):
        return Player(player_id, self.company)

    def get_teams_league(self, team_id):
        team = Team(team_id, self.company)
        league_teams, league_name = team.retrieve_teams_in_league()
        return League(teams=league_teams, name=league_name)


def run(username, password, company, player_ids=[], team_ids=[], league_team_ids=[]):
    rls = RecLeagueStats(company)
    rls.login(username, password)

    for p in player_ids:
        rls.rate_player(p)

    for t in team_ids:
        rls.rate_team(t)

    for l in league_team_ids:
        rls.rate_teams_league(l)
    

