from selenium.webdriver import Chrome
from collections import defaultdict
import cryptohash as chash
from definitions.WebAction import WebAction
from definitions.WebState import WebState
from definitions.Action import Action
from pyymatcher import PyyMatcher
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException
import time
import random
import string
import torch
from torch.nn.functional import gumbel_softmax
import numpy as np
from helpers import get_event_listeners

def default_factory():
    return ["",0,1]

def load_js_helper(driver):
    with open("helperscript.js") as script:
        driver.execute_script(script.read())

def get_actionable_elements_and_state(driver):
    elements = driver.execute_script("return getInteractiveElements();")
    return elements

class Environment:
    def __init__(self, driver: Chrome, base_url: str, login_url: str = "", login_actions: list[WebAction]=[]) -> None:
        self.base_url: str = base_url
        self.login_url: str = login_url
        self.driver: Chrome = driver
        self.Qtable = defaultdict(default_factory)
        self.states: list[WebState] = []
        self.login_actions: list[WebAction] = login_actions
    
    def reset(self):
        """
            Reset the environment to initial state
        """

        # check if there are multiple windows open. if yes, close all except first one
        windows = self.driver.window_handles
        if len(windows) > 1:
            windows = windows[1:]
            # switch to the first window
            for window in windows:
                self.driver.switch_to.window(window)
                self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(self.base_url)
        time.sleep(5)


    def get_state(self):
        """Returns a WebState object representing current page state.

        Returns:
            WebState: An object representing current Webpage state.
        """
        # load js helper scripts
        load_js_helper(self.driver)

        # get all the clickable actions from the page
        actionable_elements,state_sequence = get_actionable_elements_and_state(self.driver)

        # Get the url of the page
        url = self.driver.current_url

        current_state = None

        found = False

        for idx,state in enumerate(self.states):
            # Check if URL is same
            if state.url == url:
                # If URL matches, calculate similarity score based on sequence of tags using gestalt pattern matching
                similarity_score = PyyMatcher(state_sequence,state.sequence).ratio()

                # if similarity threshold is greater than 0.8 then the current state is not treated as a different state.
                # Hence update current_state with the found state value
                if similarity_score >= 0.8:
                    current_state = self.states[idx]
                    found = True
                    break

        # If no state is found, append the current state to the list of visited states
        if not found:
            # get parsed actions
            actions = self.parse_actions(actionable_elements)
            
            # calculate md5 hash of the current page screenshot - this will be the state value.
            state_name = chash.md5(state_sequence)

            # create the state object for the current page
            current_state = WebState(url,actions,state_sequence,state_name)
            self.states.append(current_state)
        
        # save screenshot of discovered states
        self.driver.save_screenshot(f"results/discovered_states/{current_state.name}.png")
        return current_state

    def parse_actions(self,actionable_elements: dict) -> list[WebAction]:
        """Generates a List of valid webactions for the current webpage.

        Returns:
            list[WebAction]: A list of WebAction type objects
        """
        
        #initialize valid actions list as an empty list
        actions = []
        
        # parse the elements list into webactions
        for type, elements in actionable_elements.items():
            if elements != []:
                if type == 'clickable':
                    for el in elements:
                        # try to get event listeners for the element
                        # get dom node id fof element
                        # event_listeners = get_event_listeners(self.driver,el)
                        actions.append(WebAction(el['tag_name'],el['locator'],Action.LEFT_CLICK))
                        # if not el.tag_name in ['a','button','']:
                        #     # actions.append(WebAction(el.tag_name,el.get_attribute('outerHTML'),Action.RIGHT_CLICK))
                        #     actions.append(WebAction(el.tag_name,el.get_attribute('outerHTML'),Action.HOVER))
                elif type == 'editable':
                    for el in elements:
                        actions.append(WebAction(el['tag_name'],el['locator'],Action.TYPE_TEXT))
                elif type == 'selectElements':
                    for el in elements:
                        actions.append(WebAction(el['tag_name'],el['locator'],Action.HANDLE_SELECT))

        return actions

    def take_action(self,action: WebAction):
        # image of the element where action is being performed
        action_image = ""
        # set the action result to 0
        action_result = 0
        # check if the current action is in login actions
        for login_action in self.login_actions:
            similarity = PyyMatcher(action.element,login_action.element).ratio()
            if similarity > 0.85:
                action = login_action
                break
        
        # find the probable elements based on the tag name
        element = None
       
        try:
            wait = WebDriverWait(self.driver,10,1)
            # the default locator strategy to follow
            locator_strategy = By.XPATH

            # if the recorded element locator is not an xpath, fall back to CSS Selector
            if not action.element.startswith("//"):
                locator_strategy = By.CSS_SELECTOR
            
            # check visibility of element
            wait.until(EC.visibility_of_element_located((locator_strategy,action.element)))
            
            # find the element
            element = self.driver.find_element(locator_strategy,action.element)
        except:
            return action_result,action_image
        
        

        if element:
            try:
                # Take the required action based on the action object provided
                match action.action:
                    case Action.LEFT_CLICK:
                        element.click()
                        time.sleep(0.5)
                    case Action.RIGHT_CLICK:
                        ActionChains(self.driver).context_click(element).perform()
                        time.sleep(0.5)
                    case Action.DBL_CLICK:
                        ActionChains(self.driver).double_click(element).perform()
                        time.sleep(0.5)
                    case Action.HOVER:
                        ActionChains(self.driver).move_to_element(element).perform()
                        time.sleep(3)
                    case Action.HANDLE_SELECT:
                        select = Select(element)
                        option = random.choice(select.options)
                        option.click()
                    case Action.TYPE_TEXT:
                        data = action.data or ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                        element.clear()
                        element.send_keys(data)
                # switch to latest opened tab if there is any
                self.driver.switch_to.window(self.driver.window_handles[-1])
                action_result = 1
                try:
                    action_image = element.screenshot_as_base64
                except:
                    pass
            except Exception as e:
                try:
                    action_image = element.screenshot_as_base64
                except:
                    pass

        # return the result of the action
        return action_result,action_image
               
    def get_best_action(self,state: WebState):
        # list of actions (matching)
        actions_list = []
        
        # list of qvalues recorded for the state
        q_values = []

        
        # get the state name
        if state.actions:

            for action in state.actions:
                qstring = "<=>".join([state.name,action.element])
                self.Qtable[qstring]

            for action in state.actions:
                for key,values in self.Qtable.items():
                    st,ac = key.split("<=>")

                    # if found action with matching state name, append it to the list of actions
                    if st == state.name and ac == action.element:
                        actions_list.append(action)

                        # get the qvalue for the state action pair and append it to the q_values list
                        q_values.append(values[1])
        logits = torch.FloatTensor(q_values)

        m = gumbel_softmax(logits,tau=1).cpu().numpy()

        selected = np.random.choice(actions_list,1,p=m)[0]

        return selected
    
    def get_maxQ(self,state: WebState):
        """
        Gets Max Qvalue recorded for a state action pair

        Args:
            state (WebState): a Webstate object

        Returns:
            float: a qvalue from the qtable
        """
        q_values=[]

        for action in state.actions:
            q_values.append(self.Qtable["<=>".join([state.name,action.element])][1])
        
        return max(q_values)
                     
