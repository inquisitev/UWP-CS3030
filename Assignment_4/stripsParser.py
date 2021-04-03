


class Action:
    def invoke():
        pass
    def can_invoke():
        pass

def parse_goal(lines):
    pass

def parse_start(lines):
    pass

def parse_actions(lines):
    def parse_action():
        pass

def read_strips(file_name):
    goal_lines = []
    start_lines = []
    action_lines = []

    current_section = goal_lines
    with open(file_name) as strips_file:
        for line in strips_file.readlines():
            if line =='\n':
                continue
            if "GOAL" in line:
                current_section = goal_lines
                continue
            elif "START" in line:
                current_section = start_lines
                continue
            elif "ACTIONS" in line:
                current_section = action_lines
                continue
            
            cleaned_line = line.replace("\t","").replace(" ", "").replace("\n", "")
            current_section.append(cleaned_line)
    parse_goal(goal_lines)
    parse_start(goal_lines)
    parse_actions(goal_lines)
    
    print(action_lines)

read_strips("/Users/trevorkeegan/development/UWP-CS3030/Assignment_4/blockworld.strips")