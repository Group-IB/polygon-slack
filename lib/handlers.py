import requests
from io import BytesIO
from threading import Thread
from pythf import Polygon, Capacity
from urllib.parse import urljoin

from lib.utils import HUNTBOX_URL, HUNTBOX_TOKEN, BOT_USER_TOKEN, Verdict, COLORS, EMOJIES
from lib.bot import bot


class FileHandler(Thread):
    def __init__(self, file_info, channel, reply_ts, msg_ts, *args, **kwargs):
        self._raw_file_info = file_info
        self.channel = channel
        self.reply_ts = reply_ts
        self.msg_ts = msg_ts
        self.filename = file_info["name"]
        self.url = file_info["url_private_download"]
        self.headers = {"Authorization": "Bearer {}".format(BOT_USER_TOKEN)}
        self.polygon = Polygon(api_url=HUNTBOX_URL, api_key=HUNTBOX_TOKEN)
        super().__init__(*args, **kwargs)

    def report_in_progress(self):
        bot.add_reaction(self.channel, self.msg_ts, EMOJIES[Verdict.IN_PROGRESS])
    
    def report_finished(self):
        bot.remove_reaction(self.channel, self.msg_ts, EMOJIES[Verdict.IN_PROGRESS])

    def report(self, verdict, extra=""):
        content = "File: {}\nVerdict: {}".format(self.filename, verdict)
        if extra:
            content += "\n{}".format(extra)
        bot.add_reaction(self.channel, self.msg_ts, EMOJIES[verdict])
        if verdict != Verdict.BENIGN:
            bot.send_message(self.channel, self.reply_ts, content, COLORS[verdict])

    def run(self):
        self.file = requests.get(self.url, headers=self.headers).content
        self.report_in_progress()
        try:
            analysis = self.polygon.upload_file(
                BytesIO(self.file),
                file_name=self.filename,
                capacity=Capacity.x86
            )
        except Exception as err:
            self.report_finished()
            extra = "Error: {}".format(str(err))
            self.report(Verdict.UNKNOWN, extra)
            return
        finished = False
        while not finished:
            analysis_info = analysis.get_info()
            finished = analysis_info["status"] != Verdict.IN_PROGRESS
        self.report_finished()
        if analysis_info["status"] == "FAILED":
            self.report(Verdict.UNKNOWN, "Error: {}".format(analysis_info.get("error")))
        elif analysis_info["verdict"]:
            families = analysis_info["families"]
            probability = analysis_info["probability"]
            attach = self.polygon.client.get_attach(analysis.id)
            report_url = "reports/{}/{}/attaches/{}".format(
                attach["analgin_result"]["commit"],
                attach["analgin_result"]["reports"][0]["id"],
                analysis.id
            )
            report_url = urljoin(analysis.client.base_url, report_url)
            extra = "Probability: {}\nFamilies: {}".format(probability, families)
            extra += "\nExplore the <{}|report> for more information".format(report_url)
            self.report(Verdict.MALICIOUS, extra)
        else:
            self.report(Verdict.BENIGN)
