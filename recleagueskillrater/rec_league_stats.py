from bs4 import BeautifulSoup
from .league import League
from .team import Team
from .player import Player
from .const import BASEURL
from .store import PlayerStore
import requests
import getpass
import json
import csv


class RecLeagueStats(object):
    
    def __init__(self, company):
        self.company = company

        self.session = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('http://', a)
        self.session.mount('https://', a)

        # Cache Stores
        self.player_store = PlayerStore()

    def login(self, username, password):
        login_page=f"{BASEURL}/dash/jsonapi/api/v1/customer/auth/token?company={self.company}"
        login_payload = {
            "grant_type": "client_credentials",
            "client_id": username,
            "client_secret": password,
            "stay_signed_in": True,
            "company": self.company,
            "company_code": self.company
        }
        r = self.session.post(login_page, data=login_payload)

    def rate_player(self, player_id):
        self.get_player(player_id).rate()

    def rate_team(self, team_id):
        self.get_team(team_id).rate()

    def rate_league(self, team_id):
        self.get_teams_league(team_id).rate()

    def rate_all_seasons_for_player(self, player_id):
        self.get_player(player_id).rate_seasons()

    def rate_all_players_on_team(self, team_id):
        self.get_team(team_id).rate_players()

    def rate_all_teams_in_league(self, team_id):
        self.get_teams_league(team_id).rate_teams()

    def get_team(self, team_id):
        return Team(self.session, team_id, self.company)

    def get_player(self, player_id):
        return Player(self.session, player_id, self.company)

    def get_teams_league(self, team_id):
        team = Team(self.session, team_id, self.company)
        league_teams, league_name = team.retrieve_teams_in_league()
        return League(teams=league_teams, name=league_name)

def _get_max_roster_size(data):
    max_size = 0
    for t in data:
        roster_size = len(t.get("players", []))
        if roster_size > max_size:
            max_size = roster_size
    return max_size

def export_to_csv(csv_name, username, password, company, player_ids=[], team_ids=[], league_team_ids=[], rate_subcomponents=False):
    data = retrieve_data(username,
                         password,
                         company,
                         player_ids,
                         team_ids,
                         league_team_ids,
                         rate_subcomponents)
    teams = _normalize_data(data)

    max_roster = _get_max_roster_size(teams)
    csv_data = [[] for x in range(max_roster+3)]
    for t in teams:
        csv_data[0].extend(["Team Name", "Team ID", "Team Skill"])
        csv_data[1].extend([t["name"], t["id"], t["avg_weighted_skill"]])
        players = t.get("players", [])
        csv_data[2].extend(["Name", "Max Level", "Weighted Avg"])
        for i in range(0, max_roster):
            row = ['', '', '']
            if i < len(players):
                p = players[i]
                row = [p["name"], p["max_level"], f"{p['weighted_avg_level']:.3f}"]
            csv_data[i+3].extend(row)

    with open(csv_name, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)


def _normalize_data(data):
    def normalize_player_list(player_data):
        def normalize_player_data(p):
            return {
                "name": p.name,
                "max_level": p.max_level,
                "weighted_avg_level": p.weighted_avg_level
            }

        players = player_data if isinstance(player_data, list) else player_data.values()

        return [normalize_player_data(x) for x in players]
    teams = []
    if data["players"]:
        teams.append({"id": 0, "name": "Default Team", "players": normalize_player_list(data["players"]), "avg_weighted_skill": "N/A"})

    for id, t in data["teams"].items():
        if id not in teams:
            teams.append({
                            "id": t.id,
                            "name": t.name,
                            "players": normalize_player_list(t.players),
                            "avg_weighted_skill": t.avg_weighted_skill
                        })

    for l_id, l in data["leagues"].items():
        for t in l.teams:
            if t.id not in teams:
                teams.append({
                            "id": t.id,
                            "name": t.name,
                            "players": normalize_player_list(t.players),
                            "avg_weighted_skill": t.avg_weighted_skill
                        })
    return teams


def retrieve_data(username, password, company, player_ids=[], team_ids=[], league_team_ids=[], rate_subcomponents=False):
    rls = RecLeagueStats(company)
    rls.login(username, password)

    leagues = {}
    teams = {}
    players = {}

    for p in player_ids:
        players[p] = rls.get_player(p)

    for t in team_ids:
        teams[t] = rls.get_team(t)

    for l in league_team_ids:
        league_id = f"league-{l}"  # TODO: get the actual league name
        leagues[l] = rls.get_teams_league(l)

    return {
        "leagues": leagues,
        "teams": teams,
        "players": players
    }


def run(username, password, company, player_ids=[], team_ids=[], league_team_ids=[], rate_subcomponents=False):
    rls = RecLeagueStats(company)
    rls.login(username, password)

    if rate_subcomponents:
        for p in player_ids:
            rls.rate_all_seasons_for_player(p)

        for t in team_ids:
            rls.rate_all_players_on_team(t)

        for l in league_team_ids:
            rls.rate_all_teams_in_league(l)

    else:
        for p in player_ids:
            rls.rate_player(p)

        for t in team_ids:
            rls.rate_team(t)

        for l in league_team_ids:
            rls.rate_league(l)
    

