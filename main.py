import glob
import os
import random
import math

import numpy as np
import pygame
import csv
import heapq
import ast


def distance(start, goal):
    return math.sqrt((start[0] - goal[0]) ** 2 + (start[1] - goal[1]) ** 2)


# A* pathfinding algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, start_floor, goal, goal_floor):
    global transitions
    if start_floor != goal_floor:
        # Check for floor transitions
        current_transitions = {k: v for k, v in transitions.items() if start_floor in k}
        nearest_coords = []
        for transition_key, transition_value in current_transitions.items():
            for current_coord, next_dict in transition_value.items():
                for coord, next_position, next_coord in zip(eval(current_coord), next_dict.keys(), next_dict.values()):
                    if goal_floor in next_position:
                        nearest_coords.append((next_coord, heuristic(start, coord), goal_floor, coord, transition_key))
        if nearest_coords:
            # Sort the list by the heuristic value and get the coordinate with the smallest heuristic value
            nearest = min(nearest_coords, key=lambda x: x[1])
        else:
            goal_block = goal_floor[0]
            to_next_block_list = []
            # If goal_floor is not in next_position, find the nearest next coordinate
            for transition_key, transition_value in current_transitions.items():
                current_block, current_floor = transition_key[0], int(transition_key[2])
                for current_coord, next_dict in transition_value.items():
                    for coord, next_position, next_coord in zip(eval(current_coord), next_dict.keys(), next_dict.values()):
                        # Check if goal_floor is bottom or top
                        next_block, next_floor = next_position[0], int(next_position[2])
                        if goal_block != current_block:
                            if next_block == goal_block:
                                print("got")
                                to_next_block_list.append((next_coord, heuristic(start, coord), next_position[:3], coord, transition_key))
                            else:
                                if int(goal_floor[-1]) < current_floor < next_floor:
                                    # If the goal is at a lower floor and the next floor is above the current floor,
                                    # ignore this transition
                                    continue
                        nearest_coords.append((next_coord, heuristic(start, coord), next_position[:3], coord, transition_key))

            if len(to_next_block_list) > 0:
                nearest_coords = to_next_block_list
            # Sort the list by the heuristic value and get the coordinate with the smallest heuristic value
            nearest = min(nearest_coords, key=lambda x: x[1])
        print(eval(nearest[0])[0], nearest[2], goal, goal_floor)
        astar(eval(nearest[0])[0], nearest[2], goal, goal_floor)
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
        'agf': 'AGF.csv',
        'af1': 'AF1.csv',
        'af2': 'AF2.csv',
        'bgf': 'BGF.csv',
        'bf1': 'BF1.csv',
        'bf2': 'BF2.csv'
    }
    file = floor_map_dict[floor]
    with open(file, 'r') as f:
        reader = csv.reader(f)
        maze = []
        for line in reader:
            maze.append(line)
        return maze


def read_database():
    with open('Database - Database.csv', 'r') as file:
        # Create a CSV reader
        reader = csv.reader(file)

        room_facilities_dict = {}
        # Loop over each row in the CSV
        next(reader)

        for row in reader:
            # Faculty,Block,Floor,Room/Facilities,Label,Color Code
            # Append each column to the respective list
            temp_dict = {
                'block': row[1],
                'floor': row[2],
                'label': row[4],
                'color code': row[5],
                'coordinate': row[6]
            }
            key = (row[1] + row[2] + " " + row[3]).lower().strip()
            room_facilities_dict[key] = temp_dict

    with open('Database - Database2.csv', 'r') as file:
        # Create a CSV reader
        reader = csv.reader(file)

        transition_dict = {}
        # Loop over each row in the CSV
        next(reader)

        for row in reader:  # Skip header
            block = row[0]
            floor = row[1]
            start_location = row[2]
            start_key = f'{block.lower()}{floor.lower()} {start_location.lower()}'.strip()

            transitions = eval(
                row[3].replace('(', '{').replace(')', '}').replace('{\'', '{"').replace('\':', '":').replace(', \'',
                                                                                                             ', "').replace(
                    ': \'', ': "').replace('\'', '"'))

            for t in transitions:
                key, value = list(t.items())[0]
                combined_key = (key + " " + value).lower().strip()
                destination_coordinates = room_facilities_dict[combined_key]["coordinate"]

                if start_key in room_facilities_dict:
                    # Find the coordinates for the start location
                    start_coordinates = room_facilities_dict[start_key]['coordinate']
                    transition_dict[start_key] = {start_coordinates: {combined_key: destination_coordinates}}
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


def main():
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

    destination = input("Destination?['Cancel' to stop]: ").lower()
    while True:
        dest_possible = [key for key in room_facilities_dict if destination in key]
        if destination == 'Cancel':
            return
        if len(dest_possible) == 0:
            print("Invalid Destination")
            destination = input("Destination?['Cancel' to stop]: ").lower()
        elif len(dest_possible) > 1:
            [print(key) for key in dest_possible]
            destination = input("Which location do you mean?")
            if destination in dest_possible:
                break
        else:
            destination = dest_possible[0]
            break

    start = (input("Start Location?['Cancel' to stop]: ")).lower()
    while True:
        start_possible = [key for key in room_facilities_dict if start in key]
        if start == 'Cancel':
            return
        if len(start_possible) == 0:
            print("Invalid Start Position")
            start = (input("Start Location?['Cancel' to stop]: ")).lower()
        elif len(start_possible) > 1:
            [print(key) for key in start_possible]
            start = input("Which location do you mean?")
            if start in start_possible:
                break
        else:
            start = start_possible[0]
            break

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
    astar(start_coordinate, start_floor_plan, nearest_goal, destination_floor_plan)

    files = glob.glob('path/*')
    for f in files:
        os.remove(f)

    font = pygame.font.SysFont(None, 5*TILE_SIZE)
    counter = len(paths)

    for path in paths:
        maze_floor = path[0][1]
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

        pygame.image.save(surface, 'path/'+f'{counter}.png')
        counter -= 1



    #pygame.quit()

main()
