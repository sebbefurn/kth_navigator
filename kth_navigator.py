import openai
import json
import pandas as pd
import datetime
import re
from Levenshtein import distance

# OpanAI setup
openai.api_key_path = "/home/anon/.secret"
llm3 = "gpt-3.5-turbo-0613"

my_functions = [
    {
        "name": "get_location",
        "description": "Get location or direction to any place",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "places, buildings, rooms, parks, etc",
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_schedule",
        "description": "Gets the schedule for a specific date",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": f"The date they want to know the schedule of with format: xxxx-xx-xx. For reference the current date is {datetime.date.today()}",
                },
            },
            "required": ["date"],
        },
    },
    {
        "name": "get_microwave",
        "description": "Anything that has to do with microwaves",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    }
]

# Test if user asked for specific place with regex
def test_name(name, location):
    name = name.lower()
    location = location.lower()
    test1 = location.replace('-', '')
    test2 = location.replace('-', ' ')

    match1 = re.search(f"(?:^|\s)({name})(?=\s|$)", test1)
    match2 = re.search(f"(?:^|\s)({name})(?=\s|$)", test2)
    if (match1 or match2):
        return True
    else:
        return False

# The callable functions
def get_location(location):
    # Check the regex-places
    df = pd.read_csv("./Data/regex_places.csv", delimiter='|')
    for i in df.iterrows():
        name = i[1][0]
        if test_name(name, location) == True:
            coordinates = i[1][1]
            # Do some more stuff with coordinates
            #print(coordinates)
            return coordinates

    # Check the levenshtein-places
    df = pd.read_csv("./Data/levenshtein_places.csv", delimiter='|')
    coordinate_list = []
    best_score = -1
    tracker = -1
    for index, i in enumerate(df.iterrows()):
        name = i[1][0]
        coordinates = i[1][1]
        coordinate_list.append(coordinates)
        score = distance(location, name)
        if (score < best_score or best_score == -1):
            best_score = score
            tracker = index 

    best_guess = coordinate_list[tracker]
    # Do some stuff with coordinates
    #print(best_guess)
    return best_guess

def calculate_date(date):
    current_date = datetime.date.today()
    prompt = f"""
    The current date is {current_date} and I want you to tell me the date that the user refers to, and make sure that your answer is in the same format I gave my date.

    Here is an example so you understand better:
    EXAMPLE CURRENT DATE: 2023-07-14
    EXAMPLE INPUT: tomorrow
    EXAMPLE OUTPUT: 2023-07-15

    INPUT: {date}
    OUTPUT:
    """
    response = openai.ChatCompletion.create(
        model=llm3,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    date_ans = response["choices"][0]["message"]["content"]
    print(f"calculate data: {date}, {date_ans}")

    return date_ans


def calculate_week_number(week_string):
    # Retrieve current week number in case week_string is relative
    current_week = datetime.date(datetime.year, datetime.data.month, datetime.data.day).isocalendar().week
    prompt = f"""
    The current week is {current_week} and I want you to tell me the week number that the user refers to, and make sure that your answer is an integer.

    Here is an example so you understand better:
    EXAMPLE CURRENT WEEK: 10
    EXAMPLE INPUT: next week
    EXAMPLE OUTPUT: 11

    INPUT: {week_string}
    OUTPUT:
    """
    response = openai.ChatCompletion.create(
        model=llm3,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    week_nr = response["choices"][0]["message"]
    try:
        week_nr = int(week_nr)
    except:
        print("AI did not return week as a number")
        exit()

    return week_nr

def get_schedule(date):
    activities = []
    df = pd.read_csv("./Data/tefy_schedule_s2.csv", delimiter=',')
    for i in df.iterrows():
        if i[1][0] == date:
            activities.append([i[1][1], i[1][3], i[1][4], i[1][6], i[1][7]])
    
    answer = ""
    for activity in activities:
        answer += f"start: {activity[0]}\nend: {activity[1]}\nactivity: {activity[2]}\ncourse: {activity[3]}\nroom: {activity[4]}\n---------------\n"
    return answer

def get_microwaves():
    # Read data from microwave file and just return it pretty much
    pass

 
# User interaction
question = input("INPUT: ")

response = openai.ChatCompletion.create(
    model=llm3,
    messages=[
        {"role": "user", "content": question},
    ],
    functions=my_functions,
    function_call="auto",
)

message = response["choices"][0]["message"]
function_name = message["function_call"]["name"]
print(function_name)
callable_function = eval(function_name)
arguments = json.loads(message["function_call"]["arguments"])

function_response = callable_function(**arguments)

# Debug
print(message)
print(function_name)
print(arguments)
# End Debug

response = openai.ChatCompletion.create(
    model=llm3,
    messages=[
        {"role": "user", "content": question},
        {"role": "function", "name": message.function_call.name, "content": function_response},
    ],
    functions=my_functions,
)

# The final response by LLM to user question
second_message = response["choices"][0]["message"]
print(second_message)

# TODO: 
# 1. Finish get_location() function
# 2. Create other useful functions
# 3. Create an agent using ReAct method
# 4. Create a website and setup user interface
# 5. Link user interface to our backend AI