from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from .store import player_store as ps
from .league import League
from .const import BASEURL


class Team(object):
    
    def __init__(self, session, team_id, company):
        self.session = session
        self.id = team_id
        self.company = company

        self.soup = self.fetch_team_page()
        self.name = self.retrieve_name()
        self.players = self.retrieve_players()

    def fetch_team_page(self):
        team_stats_url = f"{BASEURL}/dash/index.php?Action=Element/Stats/team_stats&hideForm=false&teamID={self.id}&company={self.company}"
        team_page = self.session.get(team_stats_url).text
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
                    player = ps.get_player(self.session, player_id, self.company)
                    players.append(player)
                except:
                    pass  # TODO Handle Error (example: stats not available for minor players)

        return players
        
    def rate(self):
        print(f"{self.name:>15}: Skill {self.avg_weighted_skill:.3f}")

    def rate_players(self):
        print(f"=== {self.name} ===")
        for p in self.players:
            p.rate()

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
            teams.append(Team(self.session, team_id, self.company))
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
        player_store.get_player(self.session, player_id, self.company).rate()
