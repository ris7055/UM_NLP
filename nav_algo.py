import glob
import os
import random
import math
import re
import numpy as np
import pygame
import heapq
import ast
import gspread as gspread


gc = gspread.service_account("./service_account.json")
sht = gc.open_by_key('1Xt_BFbm-I3LBzBLok2af2VGDCiVMSAoHBpYasnlLw5w')

def distance(start, goal):
    return math.sqrt((start[0] - goal[0]) ** 2 + (start[1] - goal[1]) ** 2)


# A* pathfinding algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, start_floor, goal, goal_floor, is_OKU):
    global transitions
    if start_floor != goal_floor:
        # Check for floor transitions
        current_transitions = {k: v for k, v in transitions.items() if start_floor in k}
        """
         for coord, next_position, next_coord in zip(eval(current_coord), next_dict.keys(), next_dict.values()):
            if goal_floor in next_position:
                nearest_coords.append((next_coord, heuristic(start, coord), goal_floor, coord, transition_key))
        """
        nearest_coords = []
        for transition_key, transition_value in current_transitions.items():
            for current_coord, next_dict in transition_value.items():
                for coord in eval(current_coord):
                    for next_position in next_dict:
                        if goal_floor in list(next_position.keys())[0]:
                            nearest_coords.append((list(next_position.values())[0], heuristic(start, coord), goal_floor, coord, transition_key))

        if nearest_coords:
            # Sort the list by the heuristic value and get the coordinate with the smallest heuristic value
            if not is_OKU:
                nearest = min(nearest_coords, key=lambda x: x[1])
            else:
                nearest_coords_with_lift = [coord for coord in nearest_coords if 'lift' in coord[4]]
                # If there are coordinates with a lift, find the nearest one
                if len(nearest_coords_with_lift) > 0:
                    nearest = min(nearest_coords_with_lift, key=lambda x: x[1])
                else:
                    # If there are no coordinates with a lift, find the nearest coordinate regardless
                    nearest = min(nearest_coords, key=lambda x: x[1])
        else:
            goal_block = goal_floor[0]
            to_next_block_list = []
            # If goal_floor is not in next_position, find the nearest next coordinate
            nearest_coords = []
            for transition_key, transition_value in current_transitions.items():
                current_block, current_floor = transition_key[0], int(transition_key[2])
                for current_coord, next_dict in transition_value.items():
                    for coord in eval(current_coord):
                        for next_position in next_dict:
                            # Check if goal_floor is bottom or top
                            next_block, next_floor = list(next_position.keys())[0][0], int(list(next_position.keys())[0][2])
                            next_coord = list(next_position.values())[0]
                            if goal_block != current_block:
                                if next_block == goal_block:
                                    to_next_block_list.append(
                                        (next_coord, heuristic(start, coord), list(next_position.keys())[0][:3], coord,
                                         transition_key))
                                else:
                                    if int(goal_floor[-1]) < current_floor < next_floor:
                                        # If the goal is at a lower floor and the next floor is above the current floor,
                                        # ignore this transition
                                        continue
                            nearest_coords.append(
                                (next_coord, heuristic(start, coord), list(next_position.keys())[0][:3], coord, transition_key))

            if len(to_next_block_list) > 0:
                nearest_coords = to_next_block_list
            # Sort the list by the heuristic value and get the coordinate with the smallest heuristic value

            if not is_OKU:
                nearest = min(nearest_coords, key=lambda x: x[1])
            else:
                nearest_coords_with_lift = [coord for coord in nearest_coords if 'lift' in coord[4]]
                # If there are coordinates with a lift, find the nearest one
                if len(nearest_coords_with_lift) > 0:
                    nearest = min(nearest_coords_with_lift, key=lambda x: x[1])
                else:
                    # If there are no coordinates with a lift, find the nearest coordinate regardless
                    nearest = min(nearest_coords, key=lambda x: x[1])

        astar(eval(nearest[0])[0], nearest[2], goal, goal_floor, is_OKU)
        goal = nearest[3]
        goal_floor = nearest[4][:3]
    global width, height, TILE_SIZE, mazes, paths

    open_set = set()
    closed_set = set()  # Add this line
    open_heap = []
    came_from = {}
    gscore = {(start, start_floor): 0}
    fscore = {(start, start_floor): heuristic(start, goal)}
    heapq.heappush(open_heap, (fscore[(start, start_floor)], (start, start_floor)))
    open_set.add((start, start_floor))

    while open_set:
        current, current_floor = heapq.heappop(open_heap)[1]
        if (current, current_floor) == (goal, goal_floor):
            path = []
            while (current, current_floor) in came_from:
                path.append((current, current_floor))
                current, current_floor = came_from[(current, current_floor)]
            if len(came_from) == 0:
                path.append((current, current_floor))
            path.reverse()
            paths.append(path)
            return

        open_set.remove((current, current_floor))
        closed_set.add((current, current_floor))

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = current[0] + dx, current[1] + dy
            if 0 <= neighbor[0] < len(mazes[current_floor][0]) and 0 <= neighbor[1] < len(mazes[current_floor]):
                if int(mazes[current_floor][neighbor[1]][neighbor[0]]) != -2 or (neighbor, current_floor) in closed_set:
                    continue
                tentative_g_score = gscore[(current, current_floor)] + 1
                if (neighbor, current_floor) not in open_set or tentative_g_score < gscore[(neighbor, current_floor)]:
                    came_from[(neighbor, current_floor)] = (current, current_floor)
                    gscore[(neighbor, current_floor)] = tentative_g_score
                    fscore[(neighbor, current_floor)] = tentative_g_score + heuristic(neighbor, goal)
                    if (neighbor, current_floor) not in open_set:
                        open_set.add((neighbor, current_floor))
                        heapq.heappush(open_heap, (fscore[(neighbor, current_floor)], (neighbor, current_floor)))
    return


def get_maze(floor):
    floor_map_dict = {
        'agf': 'AGF',
        'af1': 'AF1',
        'af2': 'AF2',
        'bgf': 'BGF',
        'bf1': 'BF1',
        'bf2': 'BF2'
    }
    return sht.worksheet(floor.upper()).get_all_values()
    # Convert records to a list of lists (similar to reading a CSV)


def read_database():
    # Get the first sheet
    worksheet1 = sht.worksheet('Room Database')
    room_facilities_records = worksheet1.get_all_records()

    room_facilities_dict = {}
    for record in room_facilities_records:
        temp_dict = {
            'block': record['Block'],
            'floor': record['Floor'],
            'label': record['Label'],
            'color code': record['Color Code'],
            'coordinate': record['Coordinate']
        }
        key = (record['Block'] + record['Floor'] + " " + record['Room/Facilities']).lower().strip()
        room_facilities_dict[key] = temp_dict

    # Get the second sheet
    worksheet2 = sht.worksheet('Transition Database')
    transition_records = worksheet2.get_all_records()

    transition_dict = {}
    for record in transition_records:
        block = record['Block']
        floor = record['Floor']
        start_location = record['Start Location']
        start_key = f'{block.lower()}{floor.lower()} {start_location.lower()}'.strip()

        transitions = eval(record['Transition'].replace('{\'', '{"').replace('\':', '":'))

        trans_list = []
        for t in transitions:
            key, value = list(t.items())[0]
            combined_key = (key + " " + value).lower().strip()
            destination_coordinates = room_facilities_dict[combined_key]["coordinate"]

            if start_key in room_facilities_dict:
                start_coordinates = room_facilities_dict[start_key]['coordinate']
                trans_list.append({combined_key: destination_coordinates})

        transition_dict[start_key] = {start_coordinates: trans_list}

    return room_facilities_dict, transition_dict


def create_tile_map(label_list, color_code_list):
    # Create a dictionary to map tile numbers to colors
    WALL_COLOR = (0, 0, 0)  # Black color
    PATHWAY_COLOR = (255, 255, 255)  # White color
    EMPTY_COLOR = (128, 128, 128)  # Gray color
    tile_map = {
        0: PATHWAY_COLOR,
        1: WALL_COLOR,
        -2: PATHWAY_COLOR,
        -1: EMPTY_COLOR
    }
    for label, color_code in zip(label_list, color_code_list):
        tile_map[int(label)] = ast.literal_eval(color_code)
    return tile_map


def create_label_map(label_list, room_name_list):
    label_map = {}
    for label, name in zip(label_list, room_name_list):
        label_map[int(label)] = name
    return label_map


def draw_arrow(surface, color, start, end):
    pygame.draw.line(surface, color, start, end, 2)
    rotation = math.degrees(math.atan2(start[1]-end[1], end[0]-start[0]))+90
    pygame.draw.polygon(surface, color, ((end[0]+5*math.sin(math.radians(rotation)), end[1]+5*math.cos(math.radians(rotation))), (end[0]+5*math.sin(math.radians(rotation-120)), end[1]+5*math.cos(math.radians(rotation-120))), (end[0]+5*math.sin(math.radians(rotation+120)), end[1]+5*math.cos(math.radians(rotation+120)))))


def main(start, destination, is_OKU):
    global width, height, TILE_SIZE, mazes, transitions, paths
    pygame.init()
    # Set the dimensions of each tile
    TILE_SIZE = 3
    PATH_COLOR = (255, 0, 0)
    room_facilities_dict, transitions = read_database()

    TILE_MAP = create_tile_map([room['label'] for room in room_facilities_dict.values()],
                               [room['color code'] for room in room_facilities_dict.values()])
    LABEL_MAP = create_label_map([room['label'] for room in room_facilities_dict.values()],
                                 room_facilities_dict.keys())

    start_floor_plan = start[:3]
    start_coordinate = random.choice(ast.literal_eval(room_facilities_dict[start]['coordinate']))
    destination_floor_plan = destination[:3]
    destination_coordinates = ast.literal_eval(room_facilities_dict[destination]['coordinate'])

    # Calculate distances from start to each goal
    distances = [distance(start_coordinate, goal) for goal in destination_coordinates]
    # Find the goal with the shortest distance
    nearest_goal = destination_coordinates[distances.index(min(distances))]

    mazes = {
        'af0': get_maze('agf'),
        'af1': get_maze('af1'),
        'af2': get_maze('af2'),
        'bf0': get_maze('bgf'),
        'bf1': get_maze('bf1'),
        'bf2': get_maze('bf2')
    }

    # Get the width and height of the maze
    width = len(mazes[start_floor_plan][0]) * TILE_SIZE
    height = len(mazes[start_floor_plan]) * TILE_SIZE

    # Draw the path
    paths = []
    astar(start_coordinate, start_floor_plan, nearest_goal, destination_floor_plan, is_OKU)

    files = glob.glob('static/*')
    for f in files:
        filename = os.path.basename(f)
        if re.match(r'^\d+\.png$', filename):
            os.remove(f)

    font = pygame.font.SysFont(None, 5*TILE_SIZE)
    counter = len(paths)
    each_floor_data = []
    for path in paths:
        maze_floor = path[0][1]
        each_floor_data.append(maze_floor)
        surface = pygame.Surface((len(mazes[maze_floor][0]) * TILE_SIZE, len(mazes[maze_floor]) * TILE_SIZE))
        # Draw the maze
        for y, row in enumerate(mazes[maze_floor]):
            for x, tile in enumerate(row):
                pygame.draw.rect(surface, TILE_MAP.get(int(tile), (0, 0, 0)),
                                 pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        for i in range(0, len(path) - 1, 5):  # Change this line
            start = (path[i][0][0] * TILE_SIZE, path[i][0][1] * TILE_SIZE)
            if i + 5 < len(path):
                end = (path[i + 5][0][0] * TILE_SIZE, path[i + 5][0][1] * TILE_SIZE)
            else:
                end = (path[-1][0][0] * TILE_SIZE, path[-1][0][1] * TILE_SIZE)
            draw_arrow(surface, PATH_COLOR, start, end)

        for label in np.unique(mazes[maze_floor]):
            place = np.where(np.array(mazes[maze_floor]) == label)
            if len(place) > 0:
                lab = LABEL_MAP.get(int(label), "        ")[4:]
                lab_split_list = lab.split(" ")
                t_count = 0
                max_len = max(len(x) for x in lab_split_list)
                for t in lab_split_list:
                    text = font.render(t, True, (0, 0, 0))
                    center_x = ((place[1].min() + place[1].max()) / 2 * TILE_SIZE) - (max_len * TILE_SIZE)
                    if center_x <= 0:
                        center_x = 1 * TILE_SIZE
                    elif center_x <= place[1].min() * TILE_SIZE:
                        center_x = (place[1].min() + 1) * TILE_SIZE
                    center_y = ((place[0].min() + place[0].max()) / 2 * TILE_SIZE) - (len(lab_split_list) * TILE_SIZE) + (3 * TILE_SIZE * t_count)
                    if center_y <= 0:
                        center_y = 1 * TILE_SIZE

                    surface.blit(text, (int(center_x), int(center_y)))
                    t_count += 1

        pygame.image.save(surface, 'static/'+f'{counter}.png')
        counter -= 1
    return list(reversed(each_floor_data))