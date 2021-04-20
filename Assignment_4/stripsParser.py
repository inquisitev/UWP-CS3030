import yaml, itertools
from typing import List

# A varaible is a word that is in all caps. the stmt is the statement that may contain varaibles and the
# var map is a dictionary mapping each variable to a literal
def fill_vars_with_literals(stmt, var_map):
    for take, put in var_map:
        stmt = stmt.replace(take,put)
    return stmt.replace(" ", "")


# Take the current state and develop a list of all combinations of literals to apply to an action. Apply
# the literals to that action and see if the conditions that must be present before that action, when variables
# are replaced with literals, exist in the current truth of STATE. if forward is false, then the postconditions 
# will be replaced with the preconditions and the state is expected to be the goal state. 
def make_new_states(state, actions, forward = True):
        resultant_states = []
        applicable_actions = []
        for action in actions:
            action_name, transformations = action
            pre_conditions = transformations["preconditions"]
            post_conditions= transformations["postconditions"]
            (before_conditions,after_conditions) = (pre_conditions, post_conditions) if forward else (post_conditions, pre_conditions)

            condition_name, condition_vars = action_name.split('(')
            condition_vars = condition_vars.replace(')', "").replace(" ", "").split(',')

            num_replacers = len(condition_vars)
            literals = state.get_literals()

            for replacers in itertools.product(*[literals for i in range(num_replacers)]):
                var_map = list(zip(condition_vars, replacers))

                conditions = [fill_vars_with_literals(pc, var_map) for pc in before_conditions]
                evals = [state.check_condition(condition) for condition in conditions]

                action_label = fill_vars_with_literals(action_name, var_map)

                action_is_valid = all(evals)
                if action_is_valid: 
                    action_label = fill_vars_with_literals(action_name, var_map)
                    if action_label in applicable_actions:
                        continue
                    applicable_actions.append(action_label)
                    new_state = state.mitosis()
                    new_state.action = action_label
                    added_truths = []
                    removed_truths = []
                    for del_effect in before_conditions:
                        del_effect = fill_vars_with_literals(del_effect, var_map)
                        new_state.remove_truth(del_effect)
                        removed_truths.append(del_effect)
                    for add_effect in after_conditions:
                        add_effect = fill_vars_with_literals(add_effect, var_map)
                        new_state.register_truth(add_effect)
                        added_truths.append(add_effect)
                    resultant_states.append(new_state)
        return resultant_states
                


# A state is really just a list of truths and some tools to evaluate and copy. 
class State:

    #initialize with an empty list of truths
    def __init__(self):
        self.truths = []
        self.parent = None
        self.action = ""
    
    def __str__(self):
        return ",".join(self.truths)

    def __repr__(self):
        return str(self)

    # Create a direct copy of self and set self to be the parent of the new state. This helps build the graph as it goes.    
    def mitosis(self):
        state = State()
        state.parent = self
        state.truths = [x for x in self.truths]
        return state

    # Used for set and list interactions.
    def __hash__(self):
        return hash(",".join(self.truths))

    # register a truth. The truth must not already be registered, the truth must not be a negation, and it must not be a negative equality comparison. 
    def register_truth(self, truth):
        truth = truth.replace(' ', '')
        register_conditions = [
            'noteq' not in truth,
            truth not in self.truths,
            truth.split('(')[0] != 'not',
        ]
        if all(register_conditions):
            self.truths.append(truth)

    # remove a truth if it exists
    def remove_truth(self, truth):
        if truth in self.truths:
            self.truths.remove(truth)
    
    # Equality comparison. States are equal if self is a sub state of another other state.
    def __eq__(self, other):
        def clean_str(string):
            return string.replace(" ", "")
        #return [clean_str(t) for t in self.truths] == [clean_str(t) for t in other.truths]
        return self.is_substate_of(other)
    
    # if super.truths ⊆ self.truths then self ⊆ super (no that is not backwards). Every truth of the super must be true in the sub, but the sub can have more. 
    def is_substate_of(self, super):
        def clean_str(string):
            return string.replace(" ", "")
        node_truths = [clean_str(t) for t in self.truths]
        ins = [clean_str(t) in node_truths for t in super.truths]
        all_in =  all(ins)
        return all_in

    # look at all of the truths and extract the literals. return a list of all unique literals in the truth set. If a literal is not present at start, it cannot
    # be present at end. so make sure that all literals are mentioned atleast once. 
    def get_literals(self):
        literals = set()
        for truth in self.truths:
            line = truth.split('(')[-1].replace(')', "")
            for literal in line.split(','):
                if literal.islower():
                    literals.add(literal)
        return list(iter(literals))

    # evaluate if the condition is true. Handle standard truths, negated truths, and negated equality conditions.
    def check_condition(self, condition):
        spl = condition.split('(')
        if (len(spl) > 2):
            if condition.replace(" ", "") in [x.replace(" ", "") for x in self.truths]:
                return True
            _, condition_name, condition_vars = spl
            inversion = True
        else:
            condition_name, condition_vars = spl
            inversion = False
        #condition_name, condition_vars = condition.split('(')
        condition_vars = condition_vars.replace(')', "").replace(" ", "").split(',')
        if condition_name == "noteq":
            return len(set(condition_vars)) == len(condition_vars)
        if inversion :
            condition = f"{condition_name}({','.join(condition_vars)})"
            return condition.replace(" ", "") not in [x.replace(" ", "") for x in self.truths]
        else:
            return condition.replace(" ", "") in [x.replace(" ", "") for x in self.truths]

        return False

# pretty print the traversal from end to start. reversed if forward is false to accomidate goal oriented.
def print_action_to_state(state, forward = True):
    actions = []
    while state is not None:
        actions.append(state.action)
        state = state.parent
    if not forward:
        actions = reversed(actions)
    print('\t' + '\n\t'.join(actions))



# Use iterative deepening depth first search to find a path from start state to goal state
# return the path taken to reach goal, or empty list if path does not exist.
def iterative_deepening_depth_first_search(start: State, goal: State, actions, forward = True) -> List[State]:
    parents = {}
    visited = []
    MAX_DEPTH = 100000 #Pythons max recusion size is 1000 anyways...

    # depth limited search inner recursive function
    def dls(cstart: State, cgoal: State, climit: int):

        visited.append(cstart)
        if cstart.is_substate_of(cgoal):
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

    


# Main driver portion. 
with open("./blockworld.strips") as stream:
    implementation_dict = yaml.safe_load(stream)
    start = State()
    start.truths = implementation_dict["start"]

    
    goal = State()
    goal.truths = implementation_dict["goal"]

    ns = State()
    ns.truths = [x for x in start.truths]



    actions = list(implementation_dict["actions"].items())
    print('-'*90)
    print("Backwards Path Generation")
    print(f"Start: {start}")
    print(f"Goal: {goal}")
    print(f"Path:")
    iterative_deepening_depth_first_search(goal, start, actions, forward=False)
    print('-'*90)



    print('-'*90)
    print("Forward Path Generation")
    print(f"Start: {start}")
    print(f"Goal: {goal}")
    print(f"Path:")
    iterative_deepening_depth_first_search(start, goal, actions, forward=True)
    print('-'*90)

