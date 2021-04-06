import yaml, itertools
from typing import List

def fill_vars_with_literals(stmt, var_map):
    for take, put in var_map:
        stmt = stmt.replace(take,put)
    return stmt.replace(" ", "")


def make_new_states(state, actions, forward = True):
        resultant_states = []
        applicable_actions = []
        for action in actions:
            action_name, transformations = action
            pre_conditions = transformations["preconditions"]
            add_effects= transformations["add-effects"]
            del_effects = transformations["delete-effects"]
            condition_name, condition_vars = action_name.split('(')
            condition_vars = condition_vars.replace(')', "").replace(" ", "").split(',')

            num_replacers = len(condition_vars)
            literals = state.get_literals()


            for replacers in itertools.product(*[literals for i in range(num_replacers)]):
                var_map = list(zip(condition_vars, replacers))
                if forward:
                    evals = [state.check_condition(fill_vars_with_literals(pc, var_map)) for pc in pre_conditions]
                    action_is_valid = all(evals)
                    if action_is_valid: 
                        action_label = fill_vars_with_literals(action_name, var_map)
                        if action_label in applicable_actions:
                            continue
                        applicable_actions.append(action_label)
                        new_state = state.copy()
                        new_state.action = action_label
                        print('-'*90)
                        print(f"Current State: {','.join(state.truths)}")
                        print(f"Action: {action_label}")
                        added_truths = []
                        removed_truths = []
                        for del_effect in del_effects:
                            del_effect = fill_vars_with_literals(del_effect, var_map)
                            if del_effect in new_state.truths:
                                new_state.truths.remove(del_effect)
                                removed_truths.append(del_effect)
                            else:
                                removed_truths.append(f"{del_effect} dne")
                        for add_effect in add_effects:
                            add_effect = fill_vars_with_literals(add_effect, var_map)
                            if add_effect not in new_state.truths:
                                new_state.truths.append(add_effect)
                                added_truths.append(add_effect)
                            else:
                                added_truths.append(f"{add_effect} ae")
                        resultant_states.append(new_state)

                        
                        print(f"Adding Truths: {','.join(added_truths)}")
                        print(f"Removing Truths: {','.join(removed_truths)}")
                        print(f"New State: {new_state.truths}")

                        print('-'*90)
                else:
                    adds = [fill_vars_with_literals(pc, var_map) for pc in add_effects]
                    dels = [fill_vars_with_literals(pc, var_map)for pc in del_effects]
                    add_evals = [state.check_condition(cond) for cond in add_effects] 
                    del_evals =  [state.check_condition(cond, delete_cond = True) for cond in dels]
                    action_is_valid = all(add_evals + del_evals)
                    if action_is_valid: 
                        action_label = fill_vars_with_literals(action_name, var_map)
                        if action_label in applicable_actions:
                            continue
                        applicable_actions.append(action_label)
                        new_state = state.copy()
                        new_state.action = action_label
                        print('-'*90)
                        print(f"Current State: {','.join(state.truths)}")
                        print(f"Action: {action_label}")
                        added_truths = []
                        for pc in pre_conditions:
                            pc = fill_vars_with_literals(pc, var_map)
                            if pc not in new_state.truths:
                                new_state.truths.append(pc)
                                added_truths.append(pc)
                            else:
                                added_truths.append(f"{pc} ae")
                        
                        
                        removed_truths = []
                        for pc in add_effects:
                            pc = fill_vars_with_literals(pc, var_map)
                            if pc in new_state.truths:
                                new_state.truths.remove(pc)
                                removed_truths.append(pc)
                            else:
                                removed_truths.append(f"{pc} dne")
                        
                        print(f"Adding Truths: {','.join(added_truths)}")
                        print(f"Removing Truths: {','.join(removed_truths)}")
                        print(f"New State: {new_state.truths}")

                        print('-'*90)
                        
                        resultant_states.append(new_state)


        return resultant_states
                



class State:
    def __init__(self):
        self.truths = []
        self.parent = None
        self.action = ""
    
    def __str__(self):
        return ",".join(self.truths)

    def __repr__(self):
        return str(self)

    def copy(self):
        state = State()
        state.parent = self
        state.truths = [x for x in self.truths]
        return state

    def __hash__(self):
        return hash(",".join(self.truths))
    
    def __eq__(self, other):
        def clean_str(string):
            return string.replace(" ", "")
        #return [clean_str(t) for t in self.truths] == [clean_str(t) for t in other.truths]
        return self.is_substate_of(other)
    
    def is_substate_of(self, super):
        def clean_str(string):
            return string.replace(" ", "")
        super_truths = [clean_str(t) for t in super.truths]
        return all([clean_str(t) in super_truths for t in self.truths])

    def get_literals(self):
        literals = set()
        for truth in self.truths:
            line = truth.split('(')[-1].replace(')', "")
            for literal in line.split(','):
                if literal.islower():
                    literals.add(literal)
        return list(iter(literals))

    def check_condition(self, condition, delete_cond = False):
        condition_name, condition_vars = condition.split('(')
        condition_vars = condition_vars.replace(')', "").replace(" ", "").split(',')
        if condition_name == "noteq":
            return len(set(condition_vars)) == len(condition_vars)
        if condition_name[0] == "~" or delete_cond:
            return condition.replace(" ", "") not in [x.replace(" ", "") for x in self.truths]
        else:
            return condition.replace(" ", "") in [x.replace(" ", "") for x in self.truths]

def print_action_to_state(state):
    while state is not None:
        print(state.action)
        state = state.parent


# Use iterative deepening depth first search to find a path from start state to goal state
# return the path taken to reach goal, or empty list if path does not exist.
def iterative_deepening_depth_first_search(start: State, goal: State, actions, forward = True) -> List[State]:
    parents = {}
    visited = []
    MAX_DEPTH = 100000 #Pythons max recusion size is 1000 anyways...

    # depth limited search inner recursive function
    def dls(cstart: State, cgoal: State, climit: int):

        visited.append(cstart)
        if cstart == cgoal:
            print_action_to_state(cstart)
            return True

        if climit <= 0:
            return False

        neighbors = make_new_states(cstart, actions, forward = forward)

        for neighbor in neighbors:
            if neighbor not in visited:
                if dls(neighbor, cgoal, climit - 1):
                    return True

    found = False
    for limit in range(0, MAX_DEPTH):
        visited = []
        if dls(start, goal, limit):
            found = True
            break

    



with open("./Assignment_4/blockworld.strips") as stream:
    implementation_dict = yaml.safe_load(stream)
    start = State()
    start.truths = implementation_dict["start"]

    
    goal = State()
    goal.truths = implementation_dict["goal"]


    actions = list(implementation_dict["actions"].items())
    iterative_deepening_depth_first_search(goal, start, actions, forward=False)
    #iterative_deepening_depth_first_search(start, goal, actions, forward=True)
