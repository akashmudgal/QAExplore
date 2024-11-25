from .Action import Action

class WebAction:
    def __init__(self,tag_name,element: str,action: Action,data: str = "") -> None:
        """
        Class represenmting a web action.

        Args:
            tag_name (str): The Tag Name of the target element
            element (str): The outerHTML attribute of the target element
            action_code (Action): The action to be taken (left/right/double click, hover, type text) for the element
            data (str): The data to be used while interacting with element, in case the element is editable
        """
        self.tag_name = tag_name
        self.element = element
        self.action = action
        self.data = data