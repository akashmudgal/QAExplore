from definitions.WebAction import WebAction

class WebState:

    def __init__(self,url: str,actions: list[WebAction],sequence: str,name: str) -> None:
        """Class representing state of a webpage.

        Args:
            url (str): url of the webpage.
            actions (list[WebAction]): list of valid actions on the webpage.
            sequence (str): a string representation of a sequence of actionable nodes on the page.
            name (str): name of the state. This is an md5 hash of the sequence.
        """
        self.url = url
        self.actions = actions
        self.sequence = sequence
        self.name = name