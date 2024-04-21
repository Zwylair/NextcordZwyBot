class ErrorOrganizer:
    def __init__(self, chat_state: bool = False, colour_state: bool = False, banner_state: bool = False):
        self.chat_state = chat_state
        self.colour_state = colour_state
        self.banner_state = banner_state

    def is_one_an_error(self):
        return bool(self.chat_state + self.colour_state + self.banner_state)
