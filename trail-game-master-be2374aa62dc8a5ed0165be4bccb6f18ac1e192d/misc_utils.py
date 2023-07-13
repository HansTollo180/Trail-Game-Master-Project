#!/usr/bin/python3
# coding=utf-8

import random

import cities
import survivors


# This file contains misc utility functions that have no other place


def get_random_dict_value(dictionary):
    if len(dictionary) == 0:
        return None

    return dictionary[random.choice(list(dictionary))]


def get_month_name(month_number):
    return \
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
         "December"][month_number - 1]


def format_date(datetime_object):
    date = str(datetime_object.day)

    if datetime_object.day < 11 or datetime_object.day > 19:
        if datetime_object.day % 10 == 1:
            date += "st "
        elif datetime_object.day % 10 == 2:
            date += "nd "
        elif datetime_object.day % 10 == 3:
            date += "rd "
        else:
            date += "th "
    else:
        date += "th "

    date += get_month_name(datetime_object.month) + " "

    date += str(datetime_object.year)

    return date


def format_time(datetime_object):
    time = ""

    if datetime_object.hour > 12:
        time += str(datetime_object.hour - 12)
    else:
        time += str(datetime_object.hour)

    if datetime_object.minute < 10:
        time += ":0" + str(datetime_object.minute)
    else:
        time += ":" + str(datetime_object.minute)

    if datetime_object.hour < 12:
        time += " am"
    else:
        time += " pm"

    return time


def get_end_distance():
    biggest_distance = 0

    for city in cities.city_list.values():
        distance_from_start = city["distance_from_start"]

        if distance_from_start > biggest_distance:
            biggest_distance = distance_from_start

    return biggest_distance


def get_next_city(distance):
    chosen_city = None

    for city in cities.city_list.values():
        distance_from_start = city["distance_from_start"]

        if distance_from_start > distance:
            if chosen_city is None or distance_from_start < chosen_city["distance_from_start"]:
                chosen_city = city

    return chosen_city


def get_random_survivor(if_player=True, if_bitten=True, if_zombified=False, if_dead=False):
    if count_survivors(if_player, if_bitten, if_zombified, if_dead) == 0:
        return None

    survivor_count = len(survivors.survivor_list)

    while True:
        random_survivor_index = random.randrange(survivor_count)

        if not if_player and random_survivor_index == 0:
            continue

        random_survivor = survivors.survivor_list[random_survivor_index]

        if not if_bitten and random_survivor["bitten"]:
            continue

        if not if_dead and not random_survivor["alive"]:
            continue

        if not if_zombified and random_survivor["zombified"]:
            continue

        return random_survivor


def count_survivors(if_player=True, if_bitten=True, if_zombified=False, if_dead=False):
    survivor_count = len(survivors.survivor_list)

    remaining_survivor_count = 0

    for survivor_index in range(survivor_count):
        if not if_player and survivor_index == 0:
            continue

        survivor = survivors.survivor_list[survivor_index]

        if not if_bitten and survivor["bitten"]:
            continue

        if not if_dead and not survivor["alive"]:
            continue

        if not if_zombified and survivor["zombified"]:
            continue

        remaining_survivor_count += 1

    return remaining_survivor_count


# Dealing with the player input:
def normalise_input(user_input):
    user_input = str(user_input)

    # Convert to lower case:
    user_input = user_input.lower()

    # Remove any symbols:
    newStr = ""
    for char in user_input:
        if char.isalpha() or char.isdigit() or char == " ":
            newStr += char

    # Players input to be used:
    return newStr
