import base64
import os
import re
import gspread as gspread
import numpy as np
import pandas as pd
#from flask_session import Session  # Server-side sessions
from flask import Flask, request, send_file, render_template
import nav_algo as n

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
connections_words = ["First", "Next", "Then", "After that", "Lastly"]
#Session(app)
session = {}

gc = gspread.service_account("./service_account.json")
sht = gc.open_by_key('1Xt_BFbm-I3LBzBLok2af2VGDCiVMSAoHBpYasnlLw5w')


def read_map_data():
    # Read the Database
    map_database = pd.DataFrame(
        sht.worksheet("Room Database").get_all_records())
    # Rename 'Room/Facilities' to 'room'
    map_database = map_database.rename(columns={'Room/Facilities': 'room'})
    # Select only the columns you want
    map_database = map_database[['Faculty', 'Block', 'Floor', 'room']]
    # Convert column names to lowercase
    map_database.columns = map_database.columns.str.lower()
    return map_database.to_dict(orient='records')


def read_event_data(NameColOnly=False):
    # Read the Database
    event_database = pd.DataFrame(sht.worksheet("Event Database").get_all_records())
    # Convert column names to lowercase
    event_database.columns = event_database.columns.str.lower()
    event_database["name"] = event_database["name"].str.replace("'", "__q__")
    event_database["name"] = event_database["name"].str.replace('"', "__q2__")
    if NameColOnly:
        return event_database[["name", "date", "time"]].to_dict(orient='records')
    else:
        return event_database.to_dict(orient='records')


def read_course_data():
    room_mapping = {
        'DK': 'Lecture Hall',
        'MM': 'Micro Lab',
        'MLANJUTAN': 'Postgraduate Lab',
        'M STROU': 'Stroustrup Lab 1',
        'B KULIAH2': 'Lecture Room 2',
        'B KULIAH': 'Lecture Room',
        'M CCNA': 'CCNA Lab',
        'BT': 'Tutorial Room'
    }
    pd.set_option('future.no_silent_downcasting', True)
    expected_headers = ['Module Code', 'Module Name', 'Occurrence', 'Academic Year', 'Period Slot',
                        'Day / Start Duration ', 'Tutor', 'Location', 'Room']
    # Read the Database
    course_database = pd.DataFrame.from_records(sht.worksheet("STU_MVT4")
                                                .get_all_records(head=11, expected_headers=expected_headers))
    course_database = course_database[expected_headers]
    # Replace placeholders with np.nan
    course_database = course_database.replace('', np.nan)

    course_database['Module Code'] = course_database['Module Code'].ffill(axis=0)

    course_database = course_database[course_database['Module Code'].str.startswith('W')]

    course_database = course_database.groupby('Module Code').apply(lambda x: x.ffill())

    course_database = course_database.dropna()

    course_database['Faculty'] = course_database['Room'].apply(
        lambda x: 'Computer Science and Information Technology' if 'FSKTM' in x else '')

    # Replace the values in the 'Room' column
    for key, value in room_mapping.items():
        course_database['Room'] = course_database['Room'].str.replace(key, value, regex=True)

    # Remove 'FSKTM' from the 'Room' column
    course_database['Room'] = course_database['Room'].str.replace('FSKTM', '')
    # Convert column names to lowercase
    course_database.columns = course_database.columns.str.lower()

    # Replace unescaped double quotes in the 'tutor' column
    course_database['tutor'] = course_database['tutor'].str.replace("\'", "\\'")
    # Convert the DataFrame to JSON
    return course_database.to_dict(orient='records')


map_data = read_map_data()
event_data = read_event_data()
course_data = read_course_data()


@app.route('/', methods=['GET', 'POST'])
def home():
    data = {"map_data": map_data,
            "event_data": read_event_data(True),
            "course_data": course_data}
    return render_template('index.html', data=data)


def location_exists(faculty, block, floor, room):
    if block is None and floor is None:
        # Iterate over each location in the list
        for location in map_data:
            # Check if the department, block, floor, and room match the user's input
            if location["room"].lower().strip() == room.lower().strip():
                return True
        return False
        pass
    else:
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
        # Check if the name, time, venue, and description match the user's input'
        event_name = event["name"].replace("__q__","'")
        event_name = event_name.replace("__q2__",'"')
        if event_name.strip().lower() == name.strip().lower():
            return True, event
    return False, None


def get_block_and_floor(room):
    for data in map_data:
        if data['room'].lower().strip() == room.lower().strip():
            return data['block'].lower().strip(), data['floor'].lower().strip()
    return None, None


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
        elif userText.lower() == "course":
            session['current'] = 2
            response_list.append("I am happy that I can help you in course. \nWhat course u wish to know more?\n"
                                 "You can select one from the selections below.")
        elif session['current'] == 0:
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
        elif session['current'] == 2:
            # Split the user's input
            try:
                course, day, tutor, room = userText.split("\n")
                if location_exists(None, None, None, room):
                    session['questions_asked'] += 1
                    block, floor = get_block_and_floor(room)
                    session['nav_ans'].append({"block": block, "floor": floor, "room": room})
                    response_list.append("Great. I can bring u there. Where are you now?")
                else:
                    response_list.append(
                        "I am sorry, this location/course is invalid. Can u say again which class are you going to?")
            except ValueError:
                response_list.append(
                    "I am sorry, this location/course is invalid. Can u say again which class are you going to?")
        else:
            session['questions_asked'] -= 1
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
                response_list.append("Event Name: " + event_details["name"] + "\n" + "Date: " + \
                                     event_details["date"].upper() + "\n" + "Time: " + \
                                     event_details["time"].upper() + "\n" + "Venue: " +
                                     event_details["venue"] + "\n" + "Description: " + \
                                     event_details["description"])
                response_list.append("Any other events detail u like to know more?")
            else:
                response_list.append("I am sorry, this event not exist. You can check out the events from selection "
                                     "below.")
        elif session['current'] == 2:
            # Split the user's input
            try:
                course, day, tutor, room = userText.split("\n")
                if location_exists(None, None, None, room):
                    session['questions_asked'] += 1
                    block, floor = get_block_and_floor(room)
                    session['nav_ans'].append({"block": block, "floor": floor, "room": room})
                    response_list.append("Great. I can bring u there. Where are you now?")
                else:
                    response_list.append(
                        "I am sorry, this location/course is invalid. Can u say again which class are you going to?")
            except ValueError:
                response_list.append(
                    "I am sorry, this location/course is invalid. Can u say again which class are you going to?")
    elif session['questions_asked'] == 2:
        if session['current'] == 0:
            # Split the user's input into department, block, floor, and room
            faculty, block, floor, room = userText.split("\n")
            if location_exists(faculty, block, floor, room):
                session['questions_asked'] += 1
                session['nav_ans'].append({"faculty": faculty, "block": block, "floor": floor, "room": room})
                response_list.append("Do you identify as a person with a disability? (if yes, input y/yes):")
            else:
                response_list.append("I am sorry, this location is invalid. Can u say again where are you starting "
                                     "from?")
        elif session['current'] == 2:
            # Split the user's input
            try:
                # Split the user's input into department, block, floor, and room
                faculty, block, floor, room = userText.split("\n")
                if location_exists(faculty, block, floor, room):
                    session['questions_asked'] += 1
                    session['nav_ans'].append({"faculty": faculty, "block": block, "floor": floor, "room": room})
                    response_list.append("Do you identify as a person with a disability? (if yes, input y/yes):")
                else:
                    response_list.append(
                        "I am sorry, this location/course is invalid. Can u say again which class are you going to?")
            except ValueError:
                response_list.append(
                    "I am sorry, this location/course is invalid. Can u say again which class are you going to?")
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
                    if counter == 0 and counter != len(floor_data) - 1:
                        response_list.append(connections_words[counter] + ", you are at Block " + \
                                             floor_data[counter][0].upper() + " Floor " + \
                                             floor_data[counter][-2:].upper() + ".")
                    elif counter < len(floor_data) - 1:
                        response_list.append(connections_words[counter] + ", go to Block " + \
                                             floor_data[counter][0].upper() + " Floor " + \
                                             floor_data[counter][-2:].upper() + ".")
                    else:
                        response_list.append(connections_words[counter] + " you are at Block " + \
                                             floor_data[counter][0].upper() + \
                                             " Floor " + floor_data[counter][-2:].upper() + \
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
    else:
        block = destination["block"]

    # Remove the "Floor " prefix from the floor variable
    if destination["floor"].startswith("Floor "):
        floor = destination["floor"][6:].lower().strip()
    else:
        floor = destination["floor"]

    room = destination["room"].lower().strip()

    destination = block + floor + " " + room

    start = session['nav_ans'][1]
    # Remove the "Block " prefix from the block variable
    if start["block"].startswith("Block "):
        block = start["block"][6:].lower().strip()
    else:
        block = start["block"]

    # Remove the "Floor " prefix from the floor variable
    if start["floor"].startswith("Floor "):
        floor = start["floor"][6:].lower().strip()
    else:
        floor = start["floor"]

    room = start["room"].lower().strip()

    start = block + floor + " " + room

    is_OKU = session['nav_ans'][2]

    return n.main(start, destination, is_OKU)


@app.route('/get_stored_data', methods=['GET'])
def get_stored_data():
    return {"nav_ans": session['nav_ans'], "current": session['current']}


@app.route("/get", methods=['GET', 'POST'])
def get_bot_response():
    userText = request.args.get('msg')
    userText = userText.replace('__n__', '\n')
    return get_response(userText)


if __name__ == "__main__":
    app.run()
