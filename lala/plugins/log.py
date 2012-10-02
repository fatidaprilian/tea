import codecs
import lala.config
import logging

from lala.util import command, msg, regex


chatlogger = None


@command
def last(user, channel, text):
    """Show the last lines from the log"""
    max_lines = int(lala.config.get("max_lines", default=30))
    s_text = text.split()
    try:
        lines = min(max_lines, int(s_text[1]))
    except IndexError:
        lines = max_lines
    logfile = lala.config.get("log_file")
    with codecs.open(logfile, "r", "utf-8") as _file:
        _lines = _file.readlines()
    lines = min(lines, len(_lines))
    msg(user, _lines[-lines:], log=False)


@regex(".*")
def chatlog(user, channel, text, match_obj):
    chatlogger.info("%s: %s" % (user, text))


def setup_log():
    global chatlogger
    logfile = lala.config.get("log_file")
    chatlogger = logging.getLogger("MessageLog")
    chathandler = logging.handlers.TimedRotatingFileHandler(
            encoding="utf-8",
            filename=logfile,
            when="midnight",
            backupCount=int(lala.config.get("max_log_days")))
    chatlogger.setLevel(logging.INFO)
    chathandler.setFormatter(
            logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%d %H:%M"))
    chatlogger.propagate = False
    chatlogger.addHandler(chathandler)

setup_log()
