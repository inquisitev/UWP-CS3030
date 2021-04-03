import yaml, itertools

def fill_vars_with_literals(stmt, var_map):
    for take, put in var_map:
        stmt = stmt.replace(take,put)
    return stmt

def make_new_states(state, actions, forward = True):
        resultant_states = []
        applicable_actions = []
        for action in actions:
            action_name, transformations = action
            pre_conditions = transformations["preconditions"]
            del_effects = transformations["add-effects"]
            add_effects = transformations["delete-effects"]
            condition_name, condition_vars = action_name.split('(')
            condition_vars = condition_vars.replace(')', "").replace(" ", "").split(',')

            num_replacers = len(condition_vars)
            literals = state.get_literals()


            for replacers in itertools.product(*[literals for i in range(num_replacers)]):
                var_map = list(zip(condition_vars, replacers))
                evals = [state.check_condition(fill_vars_with_literals(pc, var_map)) for pc in pre_conditions]
                action_is_valid = all(evals)
                if action_is_valid: 
                    action_label = fill_vars_with_literals(action_name, var_map)
                    if action_label in applicable_actions:
                        continue
                    applicable_actions.append(action_label)
                    new_state = state.copy()
                    if forward:
                        for del_effect in del_effects:
                            del_effect = fill_vars_with_literals(del_effect, var_map)
                            if del_effect in new_state.truths:
                                new_state.truths.remove(del_effect)
                        for add_effect in add_effects:
                            add_effect = fill_vars_with_literals(add_effect, var_map)
                            new_state.truths.append(add_effect)
                    else:
                        for del_effect in del_effects:
                            del_effect = fill_vars_with_literals(del_effect, var_map)
                            new_state.truths.append(del_effects)
                        for add_effect in add_effects:
                            add_effect = fill_vars_with_literals(add_effect, var_map)
                            if add_effect in new_state.truths:
                                new_state.truths.remove(add_effect)
                    resultant_states.append(new_state)

        print(applicable_actions)
        return resultant_states
                



class State:
    def __init__(self):
        self.truths = []

    def copy(self):
        state = State()
        state.truths = [x for x in self.truths]
        return state
    
    def __eq__(self, other):
        def clean_str(string):
            return string.replace(" ", "")
        return [clean_str(t) for t in self.truth] == [clean_str(t) for t in other.truth]
    
    def is_substate_of(self, super):
        def clean_str(string):
            return string.replace(" ", "")
        super_truths = [clean_str(t) for t in other.truth]
        return all([clean_str(t) in super_truths for t in self.truth])

    def get_literals(self):
        literals = set()
        for truth in self.truths:
            line = truth.split('(')[-1].replace(')', "")
            for literal in line.split(','):
                if literal.islower():
                    literals.add(literal)
        return list(iter(literals))

    def check_condition(self, condition):
        condition_name, condition_vars = condition.split('(')
        condition_vars = condition_vars.replace(')', "").replace(" ", "").split(',')
        if condition_name == "noteq":
            return len(set(condition_vars)) == len(condition_vars)
        if condition_name[0] == "   ~":
            return condition.replace(" ", "") not in [x.replace(" ", "") for x in self.truths]
        else:
            return condition.replace(" ", "") in [x.replace(" ", "") for x in self.truths]

with open("C:/Development/UWP-CS3030/Assignment_4/blockworld.strips") as stream:
    implementation_dict = yaml.safe_load(stream)
    s = State()
    s.truths = implementation_dict["start"]
    action = list(implementation_dict["actions"].items())
    print(len(make_new_states(s, action)))