import base64
import os
import re
import pandas as pd
#from flask_session import Session  # Server-side sessions
from flask import Flask, request, send_file, render_template#, session
import nav_algo as n

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
#Session(app)

# Read the Database
map_database = pd.read_csv('Database - Database.csv')
# Rename 'Room/Facilities' to 'room'
map_database = map_database.rename(columns={'Room/Facilities': 'room'})
# Select only the columns you want
map_database = map_database[['Faculty', 'Block', 'Floor', 'room']]
# Convert column names to lowercase
map_database.columns = map_database.columns.str.lower()
# Convert the DataFrame to JSON
map_data = map_database.to_dict(orient='records')

# Read the Database
event_database = pd.read_csv('Database.csv')
# Convert column names to lowercase
event_database.columns = event_database.columns.str.lower()
# Convert the DataFrame to JSON
event_data = event_database.to_dict(orient='records')

connections_words = ["First", "Next", "Then", "After that", "Lastly"]
session = {}


@app.route('/', methods=['GET', 'POST'])
def home():
    data = {"map_data": map_data,
            "event_data": event_data}
    return render_template('index.html', data=data)


def location_exists(faculty, block, floor, room):
    # Remove the "Block " prefix from the block variable
    if block.startswith("Block "):
        block = block[6:]

    # Remove the "Floor " prefix from the floor variable
    if floor.startswith("Floor "):
        floor = floor[6:]

    # Iterate over each location in the list
    for location in map_data:
        # Check if the department, block, floor, and room match the user's input
        if (location["faculty"] == faculty.strip() and
                location["block"] == block.strip() and
                location["floor"] == floor.strip() and
                location["room"] == room.strip()):
            return True
    return False


def event_exists(name):
    # Iterate over each event in the list
    for event in event_data:
        # Check if the name, time, venue, and description match the user's input
        if event["name"] == name:
            return True, event
    return False, None



def get_response(userText):
    response_list = []
    # Add the new input at the beginning of the list
    if 'questions_asked' not in session:
        session['questions_asked'] = 0
        session['answers'] = []
        session['nav_ans'] = []
        session['current'] = -1

    # Add the new input at the beginning of the list
    session['answers'].insert(0, userText)

    if session['questions_asked'] == 0 and userText.lower().strip() != "return":
        session['questions_asked'] += 1
        if userText.lower() == "navigation":
            session['current'] = 0
            response_list.append("I am happy that I can help you in navigation. \n\nCan u tell me where are u going "
                                 "to go? You can select ur destination from the selections below.")
        elif userText.lower() == "events":
            session['current'] = 1
            response_list.append("I am happy that I can help you in events. \nWhat events are u interest in?\n You "
                                 "can select one from the selections below.")
        elif session['current'] == 0:
            session['questions_asked'] == 1
            try:
                faculty, block, floor, room = userText.split("\n")
                if location_exists(faculty, block, floor, room):
                    session['questions_asked'] += 1
                    session['nav_ans'].append({"faculty": faculty, "block": block, "floor": floor, "room": room})
                    response_list.append("Great. Where are you starting from?")
                else:
                    response_list.append(
                        "I am sorry, this location is invalid. Can u say again where are you going to?")
            except ValueError:
                response_list.append(
                    "I am sorry, this location is invalid. Can u say again where are you going to?")
        else:
            response_list.append("I am sorry. I cannot understand what you mean.")
    elif userText.lower().strip() == "return":
        session['questions_asked'] = 0
        session['nav_ans'] = []
        session['current'] = -1
        response_list.append("What else can I help u?")
    elif session['questions_asked'] == 1:
        if session['current'] == 0:
            # Split the user's input into department, block, floor, and room
            try:
                faculty, block, floor, room = userText.split("\n")
                if location_exists(faculty, block, floor, room):
                    session['questions_asked'] += 1
                    session['nav_ans'].append({"faculty": faculty, "block": block, "floor": floor, "room": room})
                    response_list.append("Great. Where are you starting from?")
                else:
                    response_list.append(
                        "I am sorry, this location is invalid. Can u say again where are you going to?")
            except ValueError:
                response_list.append(
                    "I am sorry, this location is invalid. Can u say again where are you going to?")
        elif session['current'] == 1:
            is_event, event_details = event_exists(userText)
            if is_event:
                response_list.append("Event Name: " + event_details["name"] + "\n"\
                "Time: " + event_details["time"] + "\n"\
                "Venue: " + event_details["venue"] + "\n"\
                "Description: " + event_details["description"])
                response_list.append("Any other events detail u like to know more?")
            else:
                response_list.append("I am sorry, this event not exist. You can check out the events from selection "
                                     "below.")
    elif session['questions_asked'] == 2:
        # Split the user's input into department, block, floor, and room
        faculty, block, floor, room = userText.split("\n")
        if location_exists(faculty, block, floor, room):
            session['questions_asked'] += 1
            session['nav_ans'].append({"faculty": faculty, "block": block, "floor": floor, "room": room})
            response_list.append("Do you identify as a person with a disability? (if yes, input y/yes):")
        else:
            response_list.append("I am sorry, this location is invalid. Can u say again where are you starting from?")
    elif session['questions_asked'] == 3:
        is_OKU = userText.lower() in ['y', 'yes']
        session['nav_ans'].append(is_OKU)
        session['questions_asked'] = 0
        floor_data = get_nav_image()
        # Get all image files in the directory
        image_dir = 'static//'
        image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
        counter = 0
        for image_file in image_files:
            filename = os.path.basename(image_file)
            if re.match(r'^\d+\.png$', filename):
                with open(os.path.join(image_dir, image_file), 'rb') as f:
                    image_data = f.read()
                    data_url = 'data:image/png;base64,' + base64.b64encode(image_data).decode()
                    if counter == 0 and counter != len(floor_data)-1:
                        response_list.append(connections_words[counter]+", you are at Block "+\
                                             floor_data[counter][0].upper()+" Floor "+\
                                             floor_data[counter][:-2].upper()+".")
                    elif counter < len(floor_data)-1:
                        response_list.append(connections_words[counter]+", go to Block "+\
                                             floor_data[counter][0].upper()+" Floor "+\
                                             floor_data[counter][:-2].upper()+".")
                    else:
                        response_list.append(connections_words[counter]+" you are at Block "+\
                                             floor_data[counter][0].upper()+\
                                             " Floor "+floor_data[counter][:-2].upper()+\
                                             ", Your destination is on this floor.")
                    counter += 1
                response_list.append(data_url)

        session['nav_ans'] = []
        response_list.append("This is your navigation path.")
        response_list.append("Do you still need help in navigation? If yes, please enter ur destination.")
    else:
        response_list.append("I am sorry. I cannot understand what you mean.")
    return response_list


def get_nav_image():
    destination = session['nav_ans'][0]
    # Remove the "Block " prefix from the block variable
    if destination["block"].startswith("Block "):
        block = destination["block"][6:].lower().strip()

    # Remove the "Floor " prefix from the floor variable
    if destination["floor"].startswith("Floor "):
        floor = destination["floor"][6:].lower().strip()

    room = destination["room"].lower().strip()

    destination = block + floor + " " + room

    start = session['nav_ans'][1]
    # Remove the "Block " prefix from the block variable
    if start["block"].startswith("Block "):
        block = start["block"][6:].lower().strip()

    # Remove the "Floor " prefix from the floor variable
    if start["floor"].startswith("Floor "):
        floor = start["floor"][6:].lower().strip()

    room = start["room"].lower().strip()

    start = block + floor + " " + room

    is_OKU = session['nav_ans'][2]

    return n.main(start, destination, is_OKU)



@app.route("/get", methods=['GET', 'POST'])
def get_bot_response():
    userText = request.args.get('msg')
    userText = userText.replace('__n__', '\n')
    return get_response(userText)


if __name__ == "__main__":
    app.run()
