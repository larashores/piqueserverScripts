from platforms.states.state import State
from platforms.strings import *

S_SILENT = "Button '{label}' will activate quietly"
S_NOISY = "Button '{label}' will animate when activated"
S_TRIGGER_LIST_EMPTY = "Button '{label}' has no triggers"
S_TRIGGER_LIST_HEADER = "Triggers in '{label}': "
S_TRIGGER_LIST_ITEM_IS_TRUE = ' [CHECK]'
S_TRIGGER_LIST_AND = ' AND '
S_TRIGGER_LIST_OR = ' OR '
S_TRIGGER_DELETED = "{trigger} trigger {number} deleted from button '{label}'"
S_TRIGGER_DELETED_ALL = "Deleted all triggers in button '{label}'"
S_TRIGGER_INVALID_NUMBER = "Invalid trigger number! Use '/trigger list' to check"
S_LOGIC_AND = "Button '{label}' will activate when ALL its triggers yield true"
S_LOGIC_OR = "Button '{label}' will activate when ANY of its triggers fire"


class TriggerCommandState(State):
    name = 'trigger'
    button = None

    def __init__(self, command):
        self.command = command

    def on_exit(self, protocol, player):
        button = self.button
        if not button:
            return S_COMMAND_CANCEL.format(command='trigger ' + self.command)

        if self.command == 'list':
            if not button.triggers:
                return S_TRIGGER_LIST_EMPTY.format(label=button.label)

            items = []
            for i, trigger in enumerate(button.triggers):
                item = '#%s %s' % (i, trigger)
                if trigger.status:
                    item += S_TRIGGER_LIST_ITEM_IS_TRUE
                items.append(item)
            separator = (S_TRIGGER_LIST_AND if button.logic == 'and' else S_TRIGGER_LIST_OR)
            items = separator.join(items)
            return S_TRIGGER_LIST_HEADER.format(label=button.label) + items
        elif self.command == 'del':
            if self.number == 'all':
                button.clear_triggers()
                return S_TRIGGER_DELETED_ALL.format(label = button.label)
            else:
                try:
                    trigger = button.triggers[self.number]
                    index = button.triggers.index(trigger)
                except IndexError:
                    return S_TRIGGER_INVALID_NUMBER

                trigger.unbind()
                button.trigger_check()
                trigger_type = trigger.type.capitalize()
                return S_TRIGGER_DELETED.format(trigger=trigger_type, number=index, label=button.label)
        elif self.command == 'logic':
            button.logic = self.logic
            button.trigger_check()
            result = S_LOGIC_AND if self.logic == 'and' else S_LOGIC_OR
            return result.format(label=button.label)
        elif self.command == 'quiet':
            button.silent = not button.silent
            result = S_SILENT if button.silent else S_NOISY
            return result.format(label = button.label)
