import imp
import logging
import lala.config
import lala.util


_callbacks = {}
_join_callbacks = list()
_regexes = {}
_cbprefix = "!"

def _make_pluginfunc(func, admin_only=False):
    return {'enabled': True, 'func': func, 'admin_only': admin_only}

def is_admin(user):
    """Check whether ``user`` is an admin.

    If a nickserv password is set, this will work by checking an internal
    list of identified admins.

    If not nickserv password is set, this simply checks if ``user`` is in
    the "admins" option of the "base" section."""
    if lala.util._BOT.factory.nspassword is not None:
        return user in lala.util._BOT.identified_admins
    else:
        return user in lala.config._get("base",
                                        "admins").split(lala.config._LIST_SEPARATOR)

def load_plugin(name):
    logging.debug("Trying to load %s" % name)
    if not lala.config._CFG.has_section(name):
        lala.config._CFG.add_section(name)
    name = "lala/plugins/%s" % name
    (f, p, d) = imp.find_module(name)
    imp.load_module(name, f, p, d)

def register_callback(trigger, func, admin_only=False):
    """ Adds ``func`` to the callbacks for ``trigger``."""
    logging.debug("Registering callback for %s" % trigger)
    _callbacks[trigger] = _make_pluginfunc(func, admin_only)

def register_join_callback(func):
    """ Registers ``func`` as a callback for join events."""
    _join_callbacks.append(func)

def register_regex(regex, func):
    """ Registers ``func`` as a callback for every message that matches
    ``regex``."""
    _regexes[regex] = _make_pluginfunc(func)

def _handle_message(user, channel, message):
    if message.startswith(_cbprefix):
        command = message.split()[0].replace(_cbprefix, "")
        funcdict = _callbacks.get(command)
        if funcdict is not None:
            logging.debug(funcdict)
            if funcdict["enabled"]:
                if ((funcdict["admin_only"] and is_admin(user))
                        or not funcdict["admin_only"]):
                    _callbacks[command]["func"](
                        user,
                        channel,
                        message)
                else:
                    lala.util.msg(channel,
                                    "Sorry %s, you're not allowed to do that" % user)
            else:
                lala.util.msg(channel, "%s is not enabled" % command)
                logging.info("%s is not enabled" % command)
        return

    for regex in _regexes:
        match = regex.search(message)
        if match is not None:
            funcdict = _regexes[regex]
            if funcdict["enabled"]:
                logging.info("%s matched %s" % (message, regex))
                _regexes[regex]["func"](
                        user,
                        channel,
                        message,
                        match)
            else:
                logging.info("%s is not enabled" % regex.pattern)

def on_join(user, channel):
    """ Calls all callbacks for on_join events that were previously
    registered with :meth:`lala.util.on_join`.
    """
    for cb in _join_callbacks:
        cb(user, channel)

def disable(trigger):
    """Disables `trigger`.

    :trigger: The trigger to disable. Can be a key for a callback or a
    regular expression
    """
    if trigger in _callbacks:
        _callbacks[trigger]["enabled"] = False

    for regex in _regexes:
        if regex.pattern == trigger:
            _regexes[regex]["enabled"] = False
            break

def enable(trigger):
    """Enables `trigger`.

    :trigger: The trigger to enable. Can be a key for a callback or a
    regular expression

    """
    if trigger in _callbacks:
        _callbacks[trigger]["enabled"] = True

    for regex in _regexes:
        if regex.pattern == trigger:
            _regexes[regex]["enabled"] = True

def _get_enabled_plugins():
    """Returns a list of all the enabled plugins.
    """
    return lala.config._get("base",
            "plugins").split(lala.config._LIST_SEPARATOR)

def setup():
    """Loads all enabled plugins
    """
    for plugin in _get_enabled_plugins():
        load_plugin(plugin)
    load_plugin("base")
