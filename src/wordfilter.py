"""
Filters messages sent by players
Word filters defined in config file

example config entry
#wordfilter
[filtered_words]
minecraft = "AOS"
fuck = "I Love"

"""
import re
from piqueserver.commands import command

TELL_USER_MESSAGE_FILTERED = False
FILTER_ADMIN_MESSAGES = True

S_ADD_FILTER_IRC = "* {} will now filter to {}. Added by {}"
S_ADD_FILTER = "{} will now filter to {}"
S_REMOVE_FILTER_IRC = "* {} has been removed from the filter by {}"
S_REMOVE_FILTER = "{} has been removed from the filter"
S_NOT_FOUND = "{} was not found in the filter list"
S_TOGGLE_IRC = '* {} {} the word filter'
S_TOGGLE = 'You {} the word filter'
S_FILTERED_WORD = '"{}" to "{}"'
S_FILTERED_MESSAGE = 'Message filtered to - {}'
S_FILTERED_MESSAGE_IRC = '* Message from {} filtered. Original message: {}'


@command('addfilter')
def add_bad_word(connection, word, filtered_word):
    connection.protocol.bad_words[word] = filtered_word
    connection.protocol.irc_say(S_ADD_FILTER_IRC.format(word, filtered_word, connection.name))
    print(S_ADD_FILTER_IRC.format(word, filtered_word, connection.name))
    if connection in connection.protocol.players:
        return S_ADD_FILTER.format(word, filtered_word)


@command('removefilter')
def remove_bad_word(connection, word):
    if word in connection.protocol.bad_words:
        del connection.protocol.bad_words[word]
        connection.protocol.irc_say(S_REMOVE_FILTER_IRC.format(word, connection.name))
        print(S_REMOVE_FILTER_IRC.format(word, connection.name))
        if connection in connection.protocol.players:
            return S_REMOVE_FILTER.format(word)
    else:
        return S_NOT_FOUND.format(word)


@command('printfilter')
def print_filter_list(connection):
    bad_word_list = []
    for word in connection.protocol.bad_words:
        bad_word_list.append(S_FILTERED_WORD.format(word, connection.protocol.bad_words[word]))
    return ', '.join(bad_word_list)


@command('togglefilter')
def toggle_filter(connection):
    connection.protocol.filter_enabled = not connection.protocol.filter_enabled
    action = 'enabled' if connection.protocol.filter_enabled else 'disabled'
    connection.protocol.irc_say(S_TOGGLE_IRC.format(connection.name, action))
    if connection in connection.protocol.players:
        return S_TOGGLE.format(action)


def apply_script(protocol, connection, config):
    config_bad_words = config.get('filtered_words', {})

    class WordFilterConnection(connection):
        def on_chat(self, value, global_message):
            if self.protocol.filter_enabled:
                if not self.admin or FILTER_ADMIN_MESSAGES:
                    value = self._word_filter(value)
            return connection.on_chat(self, value, global_message)

        def _word_filter(self, value):
            original_message = value
            bad_words = self.protocol.bad_words
            for word in bad_words:
                value = re.sub(word, bad_words[word], value, re.IGNORECASE)

            if value != original_message:
                if TELL_USER_MESSAGE_FILTERED:
                    self.send_chat(S_FILTERED_MESSAGE.format(value))
                print(S_FILTERED_MESSAGE_IRC.format(self.name, original_message))
            return value

    class WordFilterProtocol(protocol):
        def __init__(self, *args, **kwargs):
            protocol.__init__(self, *args, **kwargs)
            self.bad_words = config_bad_words
            self.filter_enabled = True

    return WordFilterProtocol, WordFilterConnection
