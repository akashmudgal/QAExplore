from dfa import DFA
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome,ChromeService
from environment import Environment
from definitions.WebAction import WebAction
from definitions.Action import Action
from pyymatcher import PyyMatcher
import time,random
from threading import Thread
import math
import pickle
import os
from helpers import get_image_similarity_score
from reporter.RLReporter import RLReportGenerator

url = "https://teams.microsoft.com/"
login_url = "https://login.microsoftonline.com/"

login_actions = [
    WebAction("input",
                '//input[@id="i0116"]',
                Action.TYPE_TEXT,"Alexw@M365x82551115.onmicrosoft.com"
    ),
    WebAction("input",
                '//input[@id="i0118"]',
                Action.TYPE_TEXT,"Hotdesking@123"),
]
reporter = RLReportGenerator(report_path="reports/")

def init_driver():
    chromedriver_folder = os.path.dirname(ChromeDriverManager().install())
    chromedriver_path = os.path.join(chromedriver_folder,"chromedriver.exe")
    driver = Chrome(service=ChromeService(chromedriver_path))
    driver.set_page_load_timeout(30)
    return driver

discovered_states=None
existing_q_table = None
discovered_dfa = None

# check if env_ states exists. if yes, load it
if os.path.exists("env_states"):
    with open("env_states","rb") as f:
        discovered_states = pickle.load(f)

# check if qtable exists. if yes, load it
if os.path.exists("qtable"):
    with open("qtable","rb") as f:
        existing_q_table = pickle.load(f)


# check if dfa exists. if yes, load it
if os.path.exists("env_states"):
    with open("dfa","rb") as f:
        discovered_dfa = pickle.load(f)


driver = init_driver()
env = Environment(driver,url,login_url,login_actions)
if discovered_states:
    env.states = discovered_states

if existing_q_table:
    env.Qtable = existing_q_table

dfa = DFA(env=env)

if discovered_dfa:
    dfa.dfa = discovered_dfa
activity_time = 900
steps = 100
tracetime = 120
gamma = 0.95
CLOSE = False

def some_task():
    global CLOSE,activity_time
    time.sleep(activity_time)
    CLOSE=True

t = Thread(target=some_task)
t.start()


episode = 0
istep = 0
tracetime1 = time.time()
total_states = len(env.states)
startstate = None

# create the necessary folders
if not os.path.exists("results"):
    os.makedirs("results/discovered_states")

# Initiate a run instance
reporter.start_run()

# the training loop
while True:
    # If max time is reached, break the loop
    if CLOSE:
        # end the run
        reporter.end_run()

        # generate the HTML report
        reporter.generate_html_report()
        break
    # reset the environment
    env.reset()

    if len(dfa.path) > 1:
        dfa.run_trace()
    # start the episode in reporter
    reporter.start_episode()

    # run the loop till the max steps reached
    for i in range(steps):
        try:
            # get the state of the current webpage
            state = env.get_state()

            if env.Qtable == {}:
                # if the Qtable is empty, select a random action from the current state
                startstate = state
                action = random.choice(startstate.actions)
            else:
                # else, select the best action based on the learned policy
                action = env.get_best_action(state)
            
            # take a screenshot of the page before action
            state_before_action = driver.get_screenshot_as_base64()
            # perform the action
            action_result,action_image = env.take_action(action)

            # add the step to reporter
            reporter.add_step(state_name=f"'{driver.title}' page",
                              state_image=state_before_action,
                              action=f"Action {action.action.name} {"passed" if action_result == 1 else "failed"} on {action.element}",
                              action_image=action_image)
            
            time.sleep(3)
            
            # if the current action results in the Agent staying on same website, the action is counted as successful
            if (env.base_url in driver.current_url or env.login_url in driver.current_url) and action_result:
                # get the updated state
                next_state = env.get_state()
                
                # create the Qtable key for state
                qtable_state_key = "<=>".join([state.name,action.element])

                # calculate the curiosity value based on the visted_count value
                reward = 1/math.sqrt(env.Qtable[qtable_state_key][2])

                existing_states = [state.name for state in env.states]

                # if a novel state is discovered by the action, add an exploration bonus
                if existing_states and next_state.name not in existing_states:
                    reward += 1

                # update the next state as the updated state for previously discovered state
                env.Qtable[qtable_state_key][0] = next_state.name

                # update the visit count for state
                env.Qtable[qtable_state_key][2] += 1

                # get the max Q value for next state and actions
                max_q = env.get_maxQ(next_state)

                # calculate the q value for the state and update the qtable
                env.Qtable[qtable_state_key][1] =  reward + gamma * max_q

                # update the dfa with the state transition
                dfa.update(state,action,next_state,env.Qtable[qtable_state_key][2])
            else:
                # create the Qtable key for state
                qtable_state_key = "<=>".join([state.name,action.element])

                # negatively reward the agent
                reward = -9999

                # get the updated state
                next_state = env.get_state()

                
                # update the next state as the updated state for previously discovered state
                env.Qtable[qtable_state_key][0] = next_state.name

                # update the visit count for state as very high, so that agent ignores this action in future
                env.Qtable[qtable_state_key][2] = 9999

                # calculate the q value for the state and update the qtable
                env.Qtable[qtable_state_key][1] = reward

                # update the dfa with the state transition
                dfa.update(state,action,next_state,env.Qtable[qtable_state_key][2])
                break

            # if there are no new states found
            if len(env.states) == total_states:
                # if activity time has been reached
                if time.time() - tracetime1 >= tracetime:
                    dfa.select_trace(startstate.name)
                    tracetime1 = time.time()
                    break
                else:
                    total_states = len(env.states)
                    tracetime1 = time.time()
        except Exception as e:
            print(e)
            if "session id" in str(e):
                driver = Chrome(service=Service(ChromeDriverManager().install()))
            break
    
    episode+=1
    with open("qtable","wb") as file:
        pickle.dump(env.Qtable, file)
    with open("dfa","wb") as file:
        pickle.dump(dfa.dfa, file)
    with open("env_states","wb") as file:
        pickle.dump(env.states, file)