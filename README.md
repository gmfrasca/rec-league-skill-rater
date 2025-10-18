# Rec League Skill Rater

A utility to scrape a target rec league stats website, and compare skill levels of various players, teams, and divisions

## Purpose
To address theories that various teams and divisions have been inflating in recent years, this program was written to objectively score players' weighted skill 'rating'.  This score can be used to also create a weighted grade for a team as a whole and even entire divisions or leagues.

## Methodolgy

### Players
To assign a player a true 'skill' rating is difficult based soley on stats and metrics.  For example, a 'ringer' could play purely shutdown defense - they would have 0 points, but also prevent all opponents from scoring.   Given this, it was decided not to look at these metrics at all.  Instead, the metrics we are interested in here are Games Played for specific levels of play.

To calculate this, we assign a point value for each division, ie:
* D League: 1 point
* Lower C:  2 points
* Inter C:  3 points
* Upper C:  4 points
* Lower B:  5 points
* Upper B:  6 points
* A League: 7 points

We then look at the players historical stats, and calculate a weighted average of points based on games played

This means, a player that has played 10 games of Upper B and 2 game of Inter C would have (6 x 10) + (3 x 2) = 66 ponts over 12 games, so their skill rating would be 5.5.  This could be seen as an 'above average Lower B player', but this metric is truly more useful in comparing a player to other players.

### Teams
In a similar fashion, **Teams** can also be compared using these weighted averages.  The program will scrape all player stats and calculate each of their skill ratings.  After it has done this calculation, it will now calculate a team score, again averaging on weight based on games played _for the target season_.  This means a team can have 10 players rated 3, each of whom have played 10 games, and a Lower B sub who played a single game, and this will not drastically throw off the skill calculation.  However, if that same Lower B player had played a full season, the team average skill rating _would_ reflect that.

### Divisions
This is a much simpler calculation, as it is a simple mean average of all the teams within the division.  The assumption here is that all member teams compete against each other and therefore are directly compareable.


## Execution
To run the script, first you will need to get a target player or team ID.

At the current moment, this utily only supports daysmart, so you can get this ID by:

**Teams**: Inspect the URL for that team's page
**Players**: Go to a team page that player is on, click the "Stats" button, and find their name.  Inspect the URL and you can find their ID as the `customerID` param.

Once you have a team or player ID, you can run the program in the following ways:

**Player Rating:**
```
python -m recleagueskillrater \
  --username <daysmart username/email> \
  --password \
  --company <company id> \
  --player_id <player id>
```

**Team Rating:**
```
python -m recleagueskillrater \
  --username <daysmart username/email> \
  --password \
  --company <company id> \
  --team_id <team id>
```

**Division Rating:**
```
python -m recleagueskillrater \
  --username <daysmart username/email> \
  --password \
  --company <company id> \
  --leagues_team_id <team id>
```

**NOTE**: For this one, just use the ID of any team in that division.  The script will figure out the other teams automatically

You can also add the `--subcomponent` flag, which will list the 'subcomponents' individually instead, ie:
* Player mode:   lists stats for each historical season
* Team mode:     lists each member of the team's individual skill rating
* Division mode: lists the skill rating for each team in the division

The script will prompt you for your daysmart password - this is so that it can access and scrape the appropriate stats from the website.
