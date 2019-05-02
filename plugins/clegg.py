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





import datetime
import errbot
from errbot import BotPlugin, botcmd, re_botcmd
#from errbot_backend_zulip import zulip
#from errbot_backend_zulip import ZulipIdentifier
import pprint
import requests


class Clegg(BotPlugin):
    """
    Clegg
    """

    # def activate(self):
    #     """
    #     Triggers on plugin activation

    #     You should delete it if you're not using it to override any default behaviour
    #     """
    #     super(Bloopty, self).activate()

    # def deactivate(self):
    #     """
    #     Triggers on plugin deactivation

    #     You should delete it if you're not using it to override any default behaviour
    #     """
    #     super(Bloopty, self).deactivate()

    # def get_configuration_template(self):
    #     """
    #     Defines the configuration structure this plugin supports

    #     You should delete it if your plugin doesn't use any configuration like this
    #     """
    #     return {'EXAMPLE_KEY_1': "Example value",
    #             'EXAMPLE_KEY_2': ["Example", "Value"]
    #            }

    # def check_configuration(self, configuration):
    #     """
    #     Triggers when the configuration is checked, shortly before activation

    #     Raise a errbot.ValidationException in case of an error

    #     You should delete it if you're not using it to override any default behaviour
    #     """
    #     super(Bloopty, self).check_configuration(configuration)

    # def callback_connect(self):
    #     """
    #     Triggers when bot is connected

    #     You should delete it if you're not using it to override any default behaviour
    #     """
    #     pass

    def callback_message(self, message):
        """
        Triggered for every received message that isn't coming from the bot itself
        """
        utc_now = datetime.datetime.utcnow()

        try:
            document = {
                "topic": message.frm.room.title,
                "subtopic": message.frm.room.subject,
                "from_name": message.frm.fullname,
                "from_email": message.frm.person,
                "url": message.extras["url"],
                "source": "zulip",
                "message": message.body,
                "timestamp": (str(utc_now) + "Z").replace(" ", "T"),
            }
        except Exception:
            self.log.debug("Can't get correct message data for indexing.")
            return

        pp = pprint.PrettyPrinter()

        index_base = "topic_thunder"
        index = "{}_{}_week{:02d}".format(
            index_base, utc_now.year, utc_now.isocalendar()[1]
        )

        self.log.debug("Indexing into %s: %s", index, pp.pformat(document))
        r = requests.post("http://localhost:9200/{}/_doc".format(index), json=document)
        self.log.debug("ES index result: %s - %s", r.status_code, r.json())
