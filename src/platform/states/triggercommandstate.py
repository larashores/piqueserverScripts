from platform.states.state import State


class TriggerCommandState(State):
    name = 'trigger'
    button = None

    def __init__(self, command):
        self.command = command

    def on_exit(self, protocol, player):
        button = self.button
        if not button:
            return S_COMMAND_CANCEL.format(command = 'trigger ' + self.command)

        if self.command == 'list':
            if not button.triggers:
                return S_TRIGGER_LIST_EMPTY.format(label = button.label)

            items = []
            for i, trigger in enumerate(button.triggers):
                item = '#%s %s' % (i, trigger)
                if trigger.status:
                    item += S_TRIGGER_LIST_ITEM_IS_TRUE
                items.append(item)
            separator = (S_TRIGGER_LIST_AND if button.logic == 'and' else
                S_TRIGGER_LIST_OR)
            items = separator.join(items)
            return S_TRIGGER_LIST_HEADER.format(label = button.label) + items
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
                return S_TRIGGER_DELETED.format(trigger = trigger_type,
                    number = index, label = button.label)
        elif self.command == 'logic':
            button.logic = self.logic
            button.trigger_check()
            result = S_LOGIC_AND if self.logic == 'and' else S_LOGIC_OR
            return result.format(label = button.label)
        elif self.command == 'quiet':
            button.silent = not button.silent
            result = S_SILENT if button.silent else S_NOISY
            return result.format(label = button.label)