import os
import io
from slackclient import SlackClient
from lib.utils import BOT_TOKEN, BOT_CLIENT_ID, BOT_CLIENT_SECRET, BOT_USER_TOKEN


logger = logging.getLogger("flask.app")


class Bot(object):
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "Polygon"
        self.emoji = ":robot_face:"
        self.oauth = {"client_id": BOT_CLIENT_ID,
                      "client_secret": BOT_CLIENT_SECRET,
                      "scope": "chat:write:user"}
        self.verification = BOT_TOKEN
        self.sc = SlackClient(BOT_USER_TOKEN)

    def auth(self, code):
        auth_response = self.sc.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        self.sc = SlackClient(auth_response["bot"]["bot_access_token"])

    def send_message(self, channel, reply_ts, content, color=None):
        if color:
            self.sc.api_call(
                "chat.postMessage",
                channel=channel,
                thread_ts=reply_ts,
                attachments=[{
                    "mrkdwn_in": ["text"],
                    "color": color,
                    "text": content
                }]
            )
        else:
            self.sc.api_call(
                "chat.postMessage",
                channel=channel,
                text="```{}```".format(content)
            )
    
    def add_reaction(self, channel, ts, emoji):
        self.sc.api_call(
            "reactions.add",
            channel=channel,
            timestamp=ts,
            name=emoji
        )

    def remove_reaction(self, channel, ts, emoji):
        self.sc.api_call(
            "reactions.remove",
            channel=channel,
            timestamp=ts,
            name=emoji
        )

bot = Bot()
