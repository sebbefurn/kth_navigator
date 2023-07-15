import openai
import json
import pandas as pd
import datetime
import re
from Levenshtein import distance

# OpanAI setup
openai.api_key_path = "/home/anon/.secret"
llm3 = "gpt-4-0613"

system_template = """
I will give you a question and I want you to go about answering my question in a very specific way following this system:
Question: My question to you
Thought: You will think about the question and think step by step on how to find the information needed to answer the question based on the actions you have available
Action: You will now decide which action to take next based on your plan
Action Input: The input to your action, and make sure it's the same number of arguments as the actions are defined with
Observation: The result of the action
(This Thought, Action, Action Input, Observation can repeat 6 times)
Thought: I have the answer
Final Answer: The final answer to the original question

Here are the actions you have in place along with a description of each one so you know when to use them:
{
    {
        Action: get_location,
        Description: Returns a google maps link to the location the user is asking for,
        {
            Argument: location,
            Description: The location the user is asking for,
        },
        Required arguments: [location],
    },
    {
        Action: get_schedule,
        Description: Returns the schedule for the date,
        {
            Argument: date,
            Description: The date to get the schedule for, and needs to be in correct format
        },
        Required arguments: [date],
    },
    {
        Action: format_date,
        Description: Formats the date into correct format,
        {
            Argument: date,
            Description: The date to format,
        },
        Required arguments: [date],
    },
}

EXAMPLES:
Question: What does the schedule look like tomorrow?
Thought: In order to get the schedule for tomorrow we can look in the schedule for tomorrow, but according to the description for the date arguement it needs to be in correct format. Therefor we first need to format the date and then look it up in the schedule
Action: format_date
Action Input: tomorrow
Observation: 2023-07-16
Thought: Now when we have the date of tomorrow in the correct format, we can retrieve the schedule for that date
Action: get_schedule
Action Input: 2023-07-16
Observation: start: 08:00\nend: 10:00\nactivity: Lecture\ncourse: SF1456\nroom: V1,V2\n---------------\nstart: 15:00\nend: 17:00\nactivity: Lecture\ncourse: SF1683\nroom: M2\n--------------\n
Thought: I now have the answer
Final Answer: Your schedule for September 26th is as follows:\n\n1. Lecture for course SF1456 from 08:00 to 10:00 in room V1 and V2.\n2. Lecture for course SF1683 from 15:00 to 17:00 in room M2.
"""

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
            # print(coordinates)
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

def format_date(date):
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
    date = date.strip()
    activities = []
    df = pd.read_csv("./Data/tefy_schedule_s2.csv", delimiter=',')
    for i in df.iterrows():
        print(i[1][0])
        if i[1][0] == date:
            activities.append([i[1][1], i[1][3], i[1][4], i[1][6], i[1][7]])
    
    answer = ""
    for activity in activities:
        answer += f"start: {activity[0]}\nend: {activity[1]}\nactivity: {activity[2]}\ncourse: {activity[3]}\nroom: {activity[4]}\n---------------\n"
    if answer == "":
        return "There are no activities"
    return answer

def get_microwaves():
    # Read data from microwave file and just return it pretty much
    pass

 
# User interaction
question = input("INPUT: ")

response = openai.ChatCompletion.create(
    model=llm3,
    messages=[
        {"role": "system", "content": system_template},
        {"role": "user", "content": question},
    ],
)

print("First step passed")

message = response["choices"][0]["message"]["content"]
function_name_start = message.index("Action") + len("Action: ")
function_name_end = message.index("Action Input")
function_args_start = function_name_end + len("Action Input: ")
function_args_end = message.index("Observation")
function_name = message[function_name_start:function_name_end]
function_args = message[function_args_start:function_args_end]

#print(f"--------------\nENTIRE MESSAGE:\n{message}\n-----------------")
print(f"Function name is {function_name}")
callable_function = eval(function_name)

print(f"Calling function {function_name} with args {function_args}")
function_response = callable_function(function_args)

prev_content = message[:function_args_end]
prev_content += f"Observation: {function_response}"

safe_net = 7
final_answer = ""

while(safe_net >= 0):
    print(f"{8-safe_net} loop about to happen")
    safe_net -= 1
    response = openai.ChatCompletion.create(
        model=llm3,
        messages=[
            {"role": "system", "content": system_template},
            {"role": "user", "content": question},
            {"role": "assistant", "content": prev_content},
        ],
    )
    message = response["choices"][0]["message"]["content"]
    if "Final Answer" in message:
        start_end = message.index("Final Answer") + len("Final Answer: ")
        final_answer = message[start_end: ]
        break
    function_name_start = message.index("Action") + len("Action: ")
    function_name_end = message.index("Action Input")
    function_args_start = function_name_end + len("Action Input: ")
    function_args_end = message.index("Observation")
    function_name = message[function_name_start:function_name_end]
    function_args = message[function_args_start:function_args_end]

    #print(f"-------------\nENTIRE MESSAGE:\n{message}\n---------------")
    print(f"Function name is {function_name}")
    callable_function = eval(function_name)

    print(f"Calling function {function_name} with args {function_args}")
    function_response = callable_function(function_args)

    prev_content = message[:function_args_end]
    prev_content += f"Observation: {function_response}"

print(final_answer)

# TODO: 
# 1. Finish get_location() function
# 2. Create other useful functions
# 3. Create an agent using ReAct method
# 4. Create a website and setup user interface
# 5. Link user interface to our backend AI