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
import io
import json
import os

# TODO: Load this in from file on startup
ANSWER_SHEET = {
    "crypto1": {"answer": "bloop", "score": 150},
    "crypto2": {"answer": "baasdfsdf", "score": 200},
}


def get_score(question, answer, answer_sheet):
    """Returns an integer score for correct answers, 0 for incorrect answers, and ``None``
    otherwise"""
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


class Clegg(BotPlugin):
    """
    Clegg
    """

    def load_team_data(self):
        filename = self.data_file
        with open(filename) as f:
            try:
                self.team_data = json.load(f)
            except Exception:
                self.log.exception("JSON Exception")

    def save_team_data(self):
        filename = self.data_file
        with open(filename, mode="w") as f:
            json.dump(self.team_data, f, indent=2)

    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """

        try:
            self.data_file = os.environ["CLEGG_DATA_FILE"]
        except Exception:
            self.log.error("Missing CLEGG_DATA_FILE env var")
            raise Exception("Missing CLEGG_DATA_FILE env var")

        self.load_team_data()

        super(Clegg, self).activate()

    # TODO: implement this
    @botcmd(split_args_with=" ")
    def register(self, message, args):
        """Registers a new team"""

        team_name = args[0]
        sender = str(message.frm)
        team_captains = {
            self.team_data[team_name]["captain"] for team_name in self.team_data
        }

        if team_name in self.team_data.keys():
            return "That team is already registered"

        if sender in team_captains:
            return "You've already registered a team: {}".format("team")

        self.team_data[team_name] = {
            "captain": sender,
            "answers": {}
        }

        self.save_team_data()

        return ("We registered you as the captain of \"{}\". "
                "Only you can submit answers for your team.".format(team_name))

    # TODO: Help, arg checking
    @botcmd(split_args_with=" ")
    def submit_answer(self, message, args):
        """<team_name> <question> <answer>"""

        sender = str(message.frm)

        team_name, question, answer, *rest = args

        self.log.info(
            "Sender: %s, Team: %s, Question: %s, Answer: %s",
            sender,
            team_name,
            question,
            answer,
        )

        def is_captain(team, captain, team_data):
            if captain is None:
                return False
            data = team_data.get(team, {})
            return data.get("captain", None) == captain

        def is_valid_question(question):
            return question in ANSWER_SHEET

        self.log.info("Teams: %s", self.team_data.keys())

        if team_name not in set(self.team_data.keys()):
            return "That's not even a team"

        if not is_captain(team_name, sender, self.team_data):
            return "You're not the boss of me. Or of that team."

        if not is_valid_question(question):
            return "That's not a real question"

        self.team_data[team_name]["answers"][question] = answer
        self.save_team_data()
        if ANSWER_SHEET[question]["answer"] == answer:
            return "Correct!"
        else:
            return "Nice try. But not good enough. Try again."



    # TODO: Make sure we're getting the team name properly
    # TODO: Template the response
    @botcmd(split_args_with=" ")
    def team_status(self, message, args):
        """Returns a dict of ``{team_name: {question, status}}``"""

        def result(question, team_answers, answer_sheet):
            if team_answers.get(question, None) is not None:
                if team_answers.get(question) == answer_sheet[question]["answer"]:
                    return "correct"
                else:
                    return "incorrect"
            else:
                return "unanswered"

        if len(args) < 1 or args[0] == "":
            return "Which team?"

        team_name = args[0]

        if team_name not in set(self.team_data.keys()):
            return "That's not a team"

        team_answers = self.team_data[team_name]["answers"]

        answers = {
            question: result(question, team_answers, ANSWER_SHEET)
            for question in ANSWER_SHEET
        }
        return answers

    # TODO: template the response to this
    @botcmd(split_args_with=None)
    def leaderboard(self, message, args):
        """Returns a list of ``(team_name, score)`` tuples, sorted with winningest team first"""

        answers = {
            team_name: self.team_data[team_name]["answers"]
            for team_name in self.team_data
        }
        scores = [
            (
                team_name,
                total_score(score_team_answers(answers[team_name], ANSWER_SHEET)),
            )
            for team_name in answers
        ]

        return sorted(scores, key=lambda x: x[1], reverse=True)
