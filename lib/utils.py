import logging
import json
from flask import Flask


app = Flask(__name__)
logger = logging.getLogger("flask.app")
options = json.load(open('../conf.json'))


BOT_HOST = options['slack']['host']
BOT_PORT = options['slack']['port']
BOT_LOG_FILE_NAME = options['slack']['log_file_name']
BOT_CLIENT_ID = options['slack']['client_id']
BOT_CLIENT_SECRET = options['slack']['client_secret']
BOT_TOKEN = options['slack']['token']
BOT_USER_TOKEN = options['slack']['bot_user_token']

HUNTBOX_URL = options['huntbox']['url']
HUNTBOX_TOKEN = options['huntbox']['token']


class Status:
    HTTP_200_OK = 200
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404


class ContentType:
    APPLICATION_JSON = "application/json"


class Verdict:
    UNKNOWN = "UNKNOWN"
    MALICIOUS = "MALICIOUS"
    BENIGN = "BENIGN"
    IN_PROGRESS = "IN PROGRESS"


COLORS = {
    Verdict.UNKNOWN: "#888888",
    Verdict.MALICIOUS: "#CC0000",
    Verdict.BENIGN: "#00CC00"
}

EMOJIES = {
    Verdict.UNKNOWN: "man-shrugging",
    Verdict.MALICIOUS: "smiling_imp",
    Verdict.BENIGN: "angel",
    Verdict.IN_PROGRESS: "male-detective"
}
