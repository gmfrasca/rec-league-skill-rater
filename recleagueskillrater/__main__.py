from recleagueskillrater.rec_league_stats import run
import argparse
import getpass


class PasswordPromptAction(argparse.Action):
    def __init__(self,
             option_strings,
             dest=None,
             nargs=0,
             default=None,
             required=False,
             type=None,
             metavar=None,
             help=None):
        super(PasswordPromptAction, self).__init__(
             option_strings=option_strings,
             dest=dest,
             nargs=nargs,
             default=default,
             required=required,
             metavar=metavar,
             type=type,
             help=help)

    def __call__(self, parser, args, values, option_string=None):
        password = getpass.getpass("Daysmart Password: ")
        setattr(args, self.dest, password)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='username', type=str, required=True)
    parser.add_argument('-p', dest='password', action=PasswordPromptAction, type=str, required=True)
    parser.add_argument('-c', dest='company', type=str, required=True)
    parser.add_argument('-i', dest='player_id', type=int)
    parser.add_argument('-t', dest='team_id', type=int)
    parser.add_argument('-l', dest='leagues_team_id', type=int)
    parser.add_argument('-s', dest='subcomponent', action='store_true')

    return parser.parse_args()

def main():
    args = parse_args()
    player_ids = [args.player_id] if args.player_id else []
    team_ids = [args.team_id] if args.team_id else []
    league_ids = [args.leagues_team_id] if args.leagues_team_id else []


    run(args.username,
        args.password,
        args.company,
        player_ids=player_ids,
        team_ids=team_ids,
        league_team_ids=league_ids,
        rate_subcomponents=args.subcomponent
    )


if __name__ == "__main__":
    main()
