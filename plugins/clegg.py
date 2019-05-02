# Clegg is a competition bot.

# All commands need to initiate 1:1 conversations
# Handle public disclosure of answers -- demerit

# Register a team

# !register

# > register <team-name>

# !register WinningestTeam
# > You're registered as the team captain for team "WinningestTeam". Only you can submit answers for the team.
# > That team is already registered.
# > There's a bad character in there.

# !submit_answer
# > submit_answer <team-name> <event> <answer>
#   Valid events are: Crypto1, Crypto2, Crypto3

# !submit_answer WinningestTeam Cryptography-1 FooBarBaz
# > Nice try. But that's not correct.
# > Correct!

# !submit_answer NotMyTeam Cryptography-1 FooBarBaz
# > That's not your team

# !team_status WinnengestTeam
# - Crypto1 - incomplete
# - Crypto2 - incorrect
# - Crypto3 - correct    - 1250 pts
# - Crypto4 - incorrect
# - ...
# Total: 1200 pts

# !scoreboard
# 1) FooTeam - 1500 pts
# 2) BarTeam - 1200 pts
# 2) NopNinjas - 1200 pts
# 2) WinningestTeam - 1200 pts <<<<
# 6) NextPlace - 1000 pts

# Add team members -- then we can send them audio files to their badges


from errbot import BotPlugin, botcmd, arg_botcmd, webhook

# TODO: Load this in from file on startup
ANSWER_SHEET = {
    "crypto1": {"answer": "bloop", "score": 150},
    "crypto2": {"answer": "baasdfsdf", "score": 200},
}


def get_score(question, answer, answer_sheet):
    """Returns an integer score for correct answers, 0 for incorrect answers, and ``None`` otherwise"""
    if question in answer_sheet:
        if answer_sheet[question]["answer"] == answer:
            return answer_sheet[question]["score"]
        else:
            return 0
    else:
        return None


def score_team_answers(answers, answer_sheet):
    results = {}
    for question, answer in answers.items():
        score = get_score(question, answer, answer_sheet)
        if score is not None:
            results[question] = score
    return results


def total_score(scored_answers):
    """Returns a total score.

    Params:
    - scored_answers: map of questions to integers scores.
    """
    return sum([scored_answers[question] for question in scored_answers])


leaderboard = {
    "team_a": {
        "answers": {
            # A score of 0 indicates an answer was submitted but was wrong.
            # A non-zero score mea
            "crypto1": "bloop",
            "crypto2": "",
        }
    }
}


class Clegg(BotPlugin):
    """
    Clegg
    """

    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """

        self.team_data = {
            "team_a": {
                "captain": "@luser",
                "answers": {
                    # A score of 0 indicates an answer was submitted but was wrong.
                    # A non-zero score mea
                    "crypto1": "bloop",
                    "crypto2": "",
                }
            },
            "team_b": {
                "captain": "@bob",
                "answers": {
                    # A score of 0 indicates an answer was submitted but was wrong.
                    # A non-zero score mea
                    "crypto1": "",
                    "crypto2": "",
                }
            },
            "team_c": {
                "captain": "@alice",
                "answers": {
                    # A score of 0 indicates an answer was submitted but was wrong.
                    # A non-zero score mea
                    "crypto1": "bloop",
                    "crypto2": "baasdfsdf",

                }
            },
        }

        super(Clegg, self).activate()

    # TODO: implement this
    @botcmd(split_args_with=None)
    def register(self, message, args):
        """A command which simply returns 'Example'"""
        return "Example"

    # TODO: implement this
    @botcmd(split_args_with=None)
    def submit_answer(self, message, args):
        """A command which simply returns 'Example'"""
        return "Example"

    # TODO: implement this
    @botcmd(split_args_with=None)
    def team_status(self, message, args):
        """A command which simply returns 'Example'"""
        return "Example"

    # TODO: template the response to this
    @botcmd(split_args_with=None)
    def leaderboard(self, message, args):
        answers = {
            team_name: self.team_data[team_name]["answers"]
            for team_name in self.team_data
        }
        scores = [
            (team_name, total_score(score_team_answers(answers[team_name], ANSWER_SHEET)))
            for team_name in answers
        ]

        return sorted(scores, key=lambda x: x[1], reverse=True)