import logging
import subprocess

from lala.util import command,msg

@command
def fortune(user, channel, text):
    """Show a random, hopefully interesting, adage"""
    try:
        p = subprocess.Popen(["fortune", "fortunes"],
                stdout=subprocess.PIPE)
        result = p.communicate()[0]
        msg(channel,"%s: %s" % (user, result.replace("\n","")))
    except OSError, e:
        logging.error("Error while calling fortune: %s" % e)
