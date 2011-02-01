#!/usr/bin/python2
import ConfigParser
import sys
import os

from lala import Bot

def main():
    """Main method"""
    config = ConfigParser.SafeConfigParser()
    #configfile = os.path.join(os.getenv("XDG_CONFIG_HOME"),"lala","config")
    configfile = "config.test"
    config.read(configfile)
    lalaconfig = config._sections["lala"]
    if "-d" in sys.argv:
        debug = True
    else:
        debug = False
    nickserv_password = lalaconfig["nickserv_password"] if "nickserv_password"\
            in lalaconfig else None
    plugins = lalaconfig["plugins"].split(",")
    bot = Bot(
            server=lalaconfig["server"],
            admin=lalaconfig["admin"],
            port=int(lalaconfig["port"]),
            nick=lalaconfig["nick"],
            #channel=lalaconfig["channel"],
            debug=debug,
            plugins=plugins,
            nickserv = nickserv_password
            )
    #try:
    bot.mainloop()
    #except RuntimeError, e:
        #print e

if __name__ == '__main__':
    main()
