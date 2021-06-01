#!/opt/tds/polygon-slack/venv/bin/python

import json
import logging
from lib.bot import bot
from flask import request, make_response, render_template, Response

from lib.utils import app, BOT_LOG_FILE_NAME, BOT_HOST, BOT_PORT, Status, ContentType
from lib.handlers import FileHandler


logger = app.logger
logfile = BOT_LOG_FILE_NAME
handler = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@app.route("/install", methods=["GET"])
def pre_install():
    client_id = bot.oauth["client_id"]
    scope = bot.oauth["scope"]
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    code_arg = request.args.get('code')
    bot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/listening", methods=["GET", "POST"])
def listen():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], Status.HTTP_200_OK,
                             dict(content_type=ContentType.APPLICATION_JSON))

    if bot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \nPolygonBot has: \
                   %s\n\n" % (slack_event["token"], bot.verification)
        return make_response(message, Status.HTTP_403_FORBIDDEN, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        if slack_event["event"].get("type") == "message":
            if slack_event["event"].get("files"):
                channel = slack_event["event"]["channel"]
                if slack_event["event"].get("thread_ts"):
                    ts = slack_event["event"]["thread_ts"]
                else:
                    ts = slack_event["event"]["ts"]
                for file_info in slack_event["event"]["files"]:
                    if file_info["mimetype"].startswith("image"):
                        continue
                    handler = FileHandler(file_info, channel, ts, slack_event["event"]["ts"])
                    handler.start()
        return Response(status=Status.HTTP_200_OK)
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", Status.HTTP_404_NOT_FOUND, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(host=BOT_HOST, port=BOT_PORT, processes=1, debug=False)
