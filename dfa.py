import networkx as nx
from environment import Environment
import copy
import numpy as np

class DFA:
    def __init__(self,env:Environment) -> None:
        self.dfa = nx.MultiDiGraph()
        self.env = env
        self.path=[]

    def update(self,state,action,next_state,visited_count):
        try:
            found = False
            for k in self.dfa[state][next_state].keys():
                if self.dfa[state][next_state][k]["action"]==action:
                    self.dfa[state][next_state][k]["weight"] = visited_count
                    found = True
                    break
            if not found:
                self.dfa.add_edges_from([(state, next_state, {"action": action,"weight":visited_count})])                
        except KeyError:
            self.dfa.add_edges_from([(state, next_state, {"action": action,"weight":visited_count})])

    def select_trace(self,currentstate):
        max_count = 9999999
        max_key = ""
        for node in nx.bfs_edges(self.dfa,currentstate):
            for k in self.dfa[node[0]][node[1]].keys():
                if self.dfa[node[0]][node[1]][k]["weight"]<max_count and "" not in node:
                    max_count = self.dfa[node[0]][node[1]][k]["weight"]
                    max_key = node[1]
        
        self.path = nx.shortest_path(self.dfa, currentstate, max_key, weight='weight')
    
    def run_trace(self):
        webstates = []
        for name in self.path:
            for state in self.env.states:
                if state.name==name:
                    webstates.append(copy.deepcopy(state))
        
        start = webstates[0]
        i = 1
        n = len(webstates)
        while i<n:
            next_state = webstates[i]
            filter_keys = []
            for k in self.env.Qtable.keys():
                st,ac = k.split("!@!")
                if st==start.name:
                    if self.env.Qtable[k][0]==next_state.name:
                        filter_keys.append(k)
            
            k = filter_keys[np.argmin([self.env.Qtable[k][2] for k in filter_keys])]
            st,ac = k.split("!@!")
            temp_ac = webstates[i-1].actions[0]
            for action in webstates[i-1].actions:
                if ac == action.action_string:
                    temp_ac = action
                    break
            webstates[i-1].actions = [temp_ac]
            start = webstates[i]
            i+=1
        
        for state in webstates[:-1]:
            action = state.actions[0]
            self.env.take_action(action,self.env.login_actions)