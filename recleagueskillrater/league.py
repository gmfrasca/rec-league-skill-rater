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
        print(f"=== {self.name} ===")
        for t in self.teams:
            t.rate()

    @property
    def avg_weighted_skill(self):
        avg_skill = 0
        if len(self.teams) == 0:
            return 0
        for t in self.teams:
            avg_skill += t.avg_weighted_skill
        return avg_skill / len(self.teams)
