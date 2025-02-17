# -*- coding: utf-8 -*-
"""Pyrgg functions module."""
import datetime
import json
import os
import pickle
import random
import textwrap
import yaml

from pyrgg.params import (
    MENU_ITEMS1,
    MENU_ITEMS2,
    PYRGG_LINKS,
    PYRGG_DESCRIPTION,
    PYRGG_FILE_ERROR_MESSAGE,
    PYRGG_INPUT_ERROR_MESSAGE,
    PYRGG_LOGGER_ERROR_MESSAGE,
    SUFFIX_MENU,
)

# random_system=random.SystemRandom()
random_system = random


def get_precision(input_number):
    """
    Return precision of input number.

    :param input_number: input number
    :type input_number: float
    :return: precision as int
    """
    try:
        number_str = str(input_number)
        _, decimalpart = number_str.split(".")
        return len(decimalpart)
    except Exception:
        return 0


def is_float(input_number):
    """
    Check input for float conversion.

    :param input_number: input number
    :type input_number: float or int
    :return: result as bool
    """
    try:
        _, decimalpart = divmod(float(input_number), 1)
    except TypeError:
        return False
    else:
        return True if decimalpart else False


def convert_str_to_number(string):
    """
    Convert string to float or int.

    :param string: input string
    :type string: str
    :return: float or int
    """
    return float(string) if is_float(string) else int(string)


def description_print():
    """
    Print justified description for overview in console.

    :return: None
    """
    print(PYRGG_LINKS)
    line(40)
    print("\n")
    print(textwrap.fill(PYRGG_DESCRIPTION, width=100))
    print("\n")
    line(40)


def line(num=11, char="#"):
    """
    Print line of char.

    :param num: number of character in this line
    :type num : int
    :param char: character
    :type char : str
    :return: None
    """
    print(char * num)


def convert_bytes(num):
    """
    Convert num to idiomatic byte unit.

    :param num: the input number.
    :type num: int
    :return: str
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def filesize(fileaddr):  # pragma: no cover
    """
    Calculate output file size.

    :param fileaddr: file addresses
    :type fileaddr: str
    :return: file size for print as string
    """
    file_info = os.stat(fileaddr)
    file_size = file_info.st_size
    print("Graph File Size : " + convert_bytes(file_size))


def logger(vertices_number, edge_number, file_name, elapsed_time):
    """
    Save generated graphs log.

    :param vertices_number: number of vertices
    :type vertices_number:int
    :param edge_number: number of edges
    :type edge_number: int
    :param file_name: file name
    :type file_name: str
    :param elapsed_time: elapsed time
    :type elapsed_time : str
    :return:  None
    """
    try:
        with open("logfile.log", "a") as file:
            file.write(str(datetime.datetime.now()) + "\n")
            file.write("Filename : " + file_name + "\n")
            file.write("Vertices : " + str(vertices_number) + "\n")
            file.write("Edges : " + str(edge_number) + "\n")
            file.write("Elapsed Time : " + str(elapsed_time) + "\n")
            file.write("-------------------------------\n")
    except Exception:
        print(PYRGG_LOGGER_ERROR_MESSAGE)


def time_convert(input_string):
    """
    Convert input_string from sec to DD,HH,MM,SS format.

    :param input_string: input time string in sec
    :type input_string: str
    :return: converted time as str
    """
    sec = float(input_string)
    days, sec = divmod(sec, 24 * 3600)
    hours, sec = divmod(sec, 3600)
    minutes, sec = divmod(sec, 60)
    return ", ".join([
        "{:02.0f} days".format(days),
        "{:02.0f} hour".format(hours),
        "{:02.0f} minutes".format(minutes),
        "{:02.0f} seconds".format(sec),
    ])


def input_filter(input_dict):
    """
    Filter input data.

    :param input_dict: input dictionary
    :type input_dict: dict
    :return: filtered data as dict
    """
    filtered_dict = input_dict.copy()
    edge_upper_threshold = filtered_dict["vertices"]
    for key in ["min_edge", "max_edge", "vertices"]:
        if filtered_dict[key] < 0:
            filtered_dict[key] *= -1

    if filtered_dict["min_weight"] > filtered_dict["max_weight"]:
        filtered_dict["min_weight"], filtered_dict["max_weight"] = (
            filtered_dict["max_weight"], filtered_dict["min_weight"]
        )

    if filtered_dict["min_edge"] > filtered_dict["max_edge"]:
        filtered_dict["min_edge"], filtered_dict["max_edge"] = (
            filtered_dict["max_edge"], filtered_dict["min_edge"]
        )

    if filtered_dict["sign"] not in [1, 2]:
        filtered_dict["sign"] = 2

    for key in ["direct", "self_loop", "multigraph"]:
        if filtered_dict[key] not in [1, 2]:
            filtered_dict[key] = 1

    if filtered_dict["self_loop"] == 2:
        edge_upper_threshold -= 1

    if filtered_dict["output_format"] not in list(
            range(1, len(SUFFIX_MENU) + 1)):
        filtered_dict["output_format"] = 1

    if filtered_dict["multigraph"] == 1:
        for key in ["min_edge", "max_edge"]:
            filtered_dict[key] = min(filtered_dict[key], edge_upper_threshold)
    return filtered_dict


def get_input(input_func=input):
    """
    Get input from user and return as dictionary.

    :param input_func : input function
    :type input_func : function object
    :return: inputs as dict
    """
    result_dict = {
        "file_name": "",
        "vertices": 0,
        "max_weight": 1,
        "min_weight": 1,
        "min_edge": 0,
        "max_edge": 0,
        "sign": 1,
        "output_format": 1,
        "weight": 1,
        "direct": 1,
        "self_loop": 1,
        "multigraph": 1,
    }

    result_dict = _update_using_first_menu(result_dict, input_func)
    result_dict = _update_using_second_menu(result_dict, input_func)
    return input_filter(result_dict)


def _update_using_first_menu(result_dict, input_func):
    """
    Update result_dict using user input from the first menu.

    :param result_dict: result data
    :type result_dict: dict
    :param input_func : input function
    :type input_func : function object
    :return: result_dict as dict
    """
    MENU_ITEMS_KEYS1 = sorted(list(MENU_ITEMS1.keys()))
    for item in MENU_ITEMS_KEYS1:
        while True:
            try:
                if item != "file_name":
                    result_dict[item] = int(input_func(MENU_ITEMS1[item]))
                else:
                    result_dict[item] = input_func(MENU_ITEMS1[item])
            except Exception:
                print(PYRGG_INPUT_ERROR_MESSAGE)
            else:
                break
    return result_dict


def _update_using_second_menu(result_dict, input_func):
    """
    Update result_dict using user input from the second menu.

    :param result_dict: result data
    :type result_dict: dict
    :param input_func : input function
    :type input_func : function object
    :return: result_dict as dict
    """
    MENU_ITEMS_KEYS2 = sorted(list(MENU_ITEMS2.keys()))
    for item in MENU_ITEMS_KEYS2:
        if result_dict["weight"] != 1 and item in ["max_weight", "min_weight"]:
            continue
        while True:
            try:
                user_input = input_func(MENU_ITEMS2[item])
                if item in ["max_weight", "min_weight"]:
                    result_dict[item] = convert_str_to_number(user_input)
                else:
                    result_dict[item] = int(user_input)
            except Exception:
                print(PYRGG_INPUT_ERROR_MESSAGE)
            else:
                break
    return result_dict


def _threshold_calc(random_edge, max_edge, vertex_degree):
    """
    Calculate threshold for branch_gen function.

    :param random_edge: number of vertex edges
    :type random_edge: int
    :param max_edge : maximum edge number
    :type max_edge : int
    :param vertex_degree: vertex degree
    :type vertex_degree: int
    :return: threshold as int
    """
    threshold = min(random_edge, abs(max_edge - vertex_degree))
    return threshold


def sign_gen():
    """
    Return random sign.

    :return: 1 or -1
    """
    flag = random_system.randint(0, 1)
    if flag == 0:
        return 1
    return -1


def random_edge_limits(vertex_index, min_edge, max_edge, degree_dict):
    """
    Calculate random_edge parameter limits.

    :param vertex_index: vertex index
    :type vertex_index: int
    :param min_edge: minimum edge number
    :type min_edge: int
    :param max_edge : maximum edge number
    :type max_edge : int
    :param degree_dict: all vertices degree
    :type degree_dict: dict
    :return: status,lower_limit,upper_limit
    """
    lower_limit = 0
    status = False
    vertex_degree = degree_dict[vertex_index]
    upper_limit = max_edge - vertex_degree
    if vertex_degree < min_edge:
        lower_limit = min_edge - vertex_degree
    if upper_limit > lower_limit:
        status = True
    return status, lower_limit, upper_limit


def branch_gen(
        vertex_index,
        max_edge,
        random_edge,
        min_weight,
        max_weight,
        sign,
        direct,
        self_loop,
        multigraph,
        used_vertices,
        degree_dict,
        degree_sort_dict):
    """
    Generate branch and weight vector of each vertex.

    :param vertex_index: origin vertex index
    :type vertex_index: int
    :param max_edge : maximum edge number
    :type max_edge : int
    :param random_edge: number of vertex edges
    :type random_edge: int
    :param min_weight: weight min range
    :type min_weight: int
    :param max_weight: weight max range
    :type max_weight: int
    :param sign: weight sign flag
    :type sign: int
    :param direct: directed and undirected graph flag
    :type direct: int
    :param self_loop: self loop flag
    :type self_loop: int
    :param multigraph: multigraph flag
    :type multigraph: int
    :param used_vertices: used vertices dictionary
    :type used_vertices: dict
    :param degree_dict: all vertices degree
    :type degree_dict: dict
    :param degree_sort_dict: degree to vertices list
    :type degree_sort_dict: dict
    :return: branch and weight list
    """
    index = 0
    branch_list = []
    weight_list = []
    reference_vertices = []
    max_weight_flag = is_float(max_weight)
    min_weight_flag = is_float(min_weight)
    weight_float_flag = min_weight_flag or max_weight_flag
    random_unit = random_system.randint
    vertex_degree = degree_dict[vertex_index]
    threshold = _threshold_calc(
        random_edge=random_edge,
        max_edge=max_edge,
        vertex_degree=vertex_degree)
    for i in range(max_edge + 1):
        reference_vertices.extend(list(degree_sort_dict[i].values()))
        if len(reference_vertices) >= threshold:
            break
    weight_precision = max(
        get_precision(max_weight),
        get_precision(min_weight))
    if weight_float_flag:
        random_unit = random_system.uniform
    if direct == 2 and (
            vertex_index in used_vertices.keys()) and multigraph == 1:
        reference_vertices = list(
            set(reference_vertices) - set(used_vertices[vertex_index]))
    if self_loop == 2 and vertex_index in reference_vertices:
        reference_vertices.remove(vertex_index)
    reference_vertices.sort()
    while (index < threshold):
        vertex_degree = degree_dict[vertex_index]
        if vertex_degree >= max_edge:
            break
        if len(reference_vertices) == 0:
            break
        random_tail_index = random_system.choice(
            range(len(reference_vertices)))
        random_tail = reference_vertices[random_tail_index]
        random_tail_degree = degree_dict[random_tail]
        if random_tail_degree >= max_edge or (
            random_tail == vertex_index and random_tail_degree >= (
                max_edge - 1)):
            reference_vertices.pop(random_tail_index)
            continue
        if direct == 2:
            if random_tail in used_vertices.keys():
                used_vertices[random_tail].append(vertex_index)
            else:
                used_vertices[random_tail] = [vertex_index]
        if sign == 2:
            random_weight = random_unit(min_weight, max_weight)
        else:
            random_weight = sign_gen() * random_unit(min_weight, max_weight)
        if weight_float_flag:
            random_weight = round(random_weight, weight_precision)
        branch_list.append(random_tail)
        weight_list.append(random_weight)
        index += 1
        del degree_sort_dict[vertex_degree][vertex_index]
        if random_tail != vertex_index:
            del degree_sort_dict[random_tail_degree][random_tail]
        degree_dict[random_tail] += 1
        degree_dict[vertex_index] += 1
        degree_sort_dict[degree_dict[vertex_index]
                         ][vertex_index] = vertex_index
        if random_tail != vertex_index:
            degree_sort_dict[degree_dict[random_tail]
                             ][random_tail] = random_tail
        if multigraph == 1:
            reference_vertices.pop(random_tail_index)
    return [branch_list, weight_list]


def edge_gen(
        vertices_number,
        min_weight,
        max_weight,
        min_edge,
        max_edge,
        sign,
        direct,
        self_loop,
        multigraph):
    """
    Generate each vertex connection number.

    :param vertices_number: number of vertices
    :type vertices_number: int
    :param min_weight: weight min range
    :type min_weight: int
    :param max_weight: weight max range
    :type max_weight: int
    :param min_edge : minimum edge number
    :type min_edge : int
    :param max_edge : maximum edge number
    :type max_edge : int
    :param sign: weight sign flag
    :type sign: int
    :param direct: directed and undirected graph flag
    :type direct: int
    :param self_loop: self loop flag
    :type self_loop: int
    :param multigraph: multigraph flag
    :type multigraph: int
    :return: list of dicts
    """
    temp = 0
    vertices_id = list(range(1, vertices_number + 1))
    vertices_edge = []
    weight_list = []
    used_vertices = {}
    degree_dict = {i: 0 for i in vertices_id}
    degree_sort_dict = {i: {} for i in range(max_edge + 1)}
    degree_sort_dict[0] = {i: i for i in vertices_id}
    random_edge = min_edge
    for i in vertices_id:
        status, lower_limit, upper_limit = random_edge_limits(
            i, min_edge, max_edge, degree_dict)
        if status:
            random_edge = random_system.randint(lower_limit, upper_limit)
        temp_list = branch_gen(
            i,
            max_edge,
            random_edge,
            min_weight,
            max_weight,
            sign,
            direct,
            self_loop,
            multigraph,
            used_vertices,
            degree_dict,
            degree_sort_dict)
        vertices_edge.append(temp_list[0])
        weight_list.append(temp_list[1])
        temp = temp + len(temp_list[0])
    return [dict(zip(vertices_id, vertices_edge)),
            dict(zip(vertices_id, weight_list)), temp]


def json_to_yaml(filename):
    """
    Convert json file to yaml file.

    :param filename: filename
    :type filename: str
    :return: None
    """
    try:
        with open(filename + ".json", "r") as json_file:
            json_data = json.loads(json_file.read())
            with open(filename + ".yaml", "w") as yaml_file:
                yaml.safe_dump(json_data, yaml_file, default_flow_style=False)
    except FileNotFoundError:
        print(PYRGG_FILE_ERROR_MESSAGE)


def json_to_pickle(filename):
    """
    Convert json file to pickle file.

    :param filename: filename
    :type filename: str
    :return: None
    """
    try:
        with open(filename + ".json", "r") as json_file:
            json_data = json.loads(json_file.read())
            with open(filename + ".p", "wb") as pickle_file:
                pickle.dump(json_data, pickle_file)
    except FileNotFoundError:
        print(PYRGG_FILE_ERROR_MESSAGE)
