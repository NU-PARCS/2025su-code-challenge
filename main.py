from sample_data_reader import SampleDataReader
import time
import json
from datetime import datetime, timedelta

def publish(reminder: str) -> None:
    print(f"publishing: {reminder}")

def run_dynamic_function(code):
    local_vars = {}
    exec(code, {}, local_vars)
    # Return the first function found in local_vars
    for v in local_vars.values():
        if callable(v):
            return v
    raise ValueError("No function found in code")

def main():

    fake_home_data = SampleDataReader("home_data.json")
    with open("home.json", "r") as f:
        home_config = json.load(f)

    curr_time = datetime.now() 
    # set the cur time to 8pm
    curr_time = curr_time.replace(hour=20, minute=0, second=0, microsecond=0)

    functionDict = {}
    # Load all dynamic functions from home_config

    for home in home_config:
        dynamic_function = run_dynamic_function(home["code"])
        if "name" in home:
            functionDict[home["name"]] = dynamic_function

    actions = {}
    with open("actions.json", "r") as f:
        triggers_actions = json.load(f)

    for tfj in triggers_actions:
        dynamic_function = run_dynamic_function(tfj["code"])
        if "name" in tfj:
            actions[tfj["name"]] = dynamic_function

    triggers = {}
    with open("triggers.json", "r") as f:
        triggers_json = json.load(f)

    for tj in triggers_json:
        for t in tj["on"]:
            triggers[t] = []
            for a in tj["actions"]:
                triggers[t].append(actions[a])
    
    

    current_house_data = fake_home_data.get()
    while current_house_data is not None:
        print("current time is", curr_time.strftime("%H:%M:%S"))
        
        # eval function should look like:
        # eval_func(curr_time, current_house_data)
        
        for dynamic_function in functionDict:
            eval_func = functionDict[dynamic_function]
            try:
                status = eval_func(curr_time, current_house_data)
                if status and dynamic_function in triggers:
                    for action in triggers[dynamic_function]:
                        try:
                            action()
                        except Exception as e:
                            print(f"Error executing action {action}: {e}")

            except Exception as e:
                print(f"Error executing function {dynamic_function}: {e}")

        current_house_data = fake_home_data.get()
        curr_time += timedelta(hours=1)


if __name__ == "__main__":
    main()