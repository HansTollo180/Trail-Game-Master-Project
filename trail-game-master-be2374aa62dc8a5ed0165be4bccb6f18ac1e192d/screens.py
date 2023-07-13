#!/usr/bin/python3
# coding=utf-8

# This file contains data on the screens in the game

import time
from random import randint

import ascii_helper
import figlet_helper
import game
import items
import screen
from debug import dprint
from misc_utils import *

screen_stack = []

previous_screen = None
current_screen = None


def open_screen(new_screen):
    global previous_screen
    global current_screen

    was_same_screen = new_screen is current_screen

    previous_screen = current_screen
    current_screen = new_screen

    previous_screen_name = "console"

    if previous_screen is not None:
        previous_screen_name = previous_screen["name"]

    if not was_same_screen and not new_screen["one_time"]:
        screen_stack.append(new_screen)
        dprint("Moving from the " + previous_screen_name + " screen to the " + current_screen["name"] + " screen.")
        dprint("Stack size: " + str(len(screen_stack)))

    new_screen["draw_function"]()

    if not was_same_screen and not new_screen["one_time"] and previous_screen is not None:
        if len(screen_stack) > 1:
            previous_screen = screen_stack.pop()
            current_screen = screen_stack.pop()
            screen_stack.append(current_screen)
            dprint(
                "Moving from the " + previous_screen["name"] + " screen to the " + current_screen["name"] + " screen.")
            dprint("Stack size: " + str(len(screen_stack)))
        elif len(screen_stack) > 0:
            current_screen = screen_stack.pop()
            screen_stack.append(current_screen)

            previous_screen_name = "console"

            if previous_screen is not None:
                previous_screen_name = previous_screen["name"]

            dprint("Moving from the " + previous_screen_name + " screen to the " + current_screen["name"] + " screen.")
            dprint("Stack size: " + str(len(screen_stack)))


def draw_starting_screen():
    title_text = "Survival Trail"

    big_font = figlet_helper.load_font("resources/fonts/big.flf")

    title_width = figlet_helper.get_text_width(title_text, big_font)

    start_title_x = int((screen.get_width() / 2) - (title_width / 2))

    while True:
        selected_index = 1

        while True:
            screen.set_cursor_visibility(False)
            decisions = ["Travel the trail", "Learn more about the trail", "Exit the trail"]

            screen.draw_ascii_font_text(start_title_x, 0, title_text, big_font)
            screen.draw_decision(None, 10, decisions, selected_index)

            screen.flush()

            selected_index, finished = screen.get_decision_input(decisions, selected_index)

            if finished:
                screen.set_cursor_visibility(True)
                break

        if selected_index == 1:
            screen.set_cursor_visibility(False)
            screen.draw_decision_box(
                "You wake up in a dark, abandoned hospital. Looking around the room you notice that the windows are boarded up with the marks all over the walls: \"There is no escape you will all die and suffer\". You quickly get out of your bed, your legs feel shaky as you notice that the calendar says is turned to October 15th 2020. The last memory you have was a hospital visit for a friend on that exact day four years before.\n\nYou quickly compose your thoughts, and decide to head for New York. Before you leave, you gather up 3 friends you know you can count on.",
                ["Continue"])

            screen.flush()

            screen.wait_key()

            screen.set_cursor_visibility(True)

            open_screen(screen_list["survivor_name"])
        elif selected_index == 2:
            open_screen(screen_list["info"])
        elif selected_index == 3:
            screen.clear()
            quit()
        else:
            continue

        return


def draw_info_screen():
    screen.clear()

    print("There should be some info here!")
    print()
    print("Press enter to continue...")

    screen.wait_key()

    open_screen(screen_list["starting"])


def get_max_user_input(print_text, alt_text, max_length):
    user_input = input(print_text)

    while len(user_input) > max_length:
        user_input = input(alt_text)
    return user_input


def draw_survivor_name_screen():
    screen.clear()
    name = get_max_user_input("Try to remember your name: ", "Enter a valid name: ", 16)
    # Leave the name as default when player enters nothing
    if len(name) > 0:
        survivors.survivor_list[0]["name"] = name

    for i in range(0, 3):
        name = get_max_user_input("Enter a friend's name who you can count on: ", "Enter a valid friend's name: ", 16)
        if len(name) > 0:
            survivors.survivor_list[i + 1]["name"] = name

    open_screen(screen_list["city"])


def draw_dead_screen():
    screen.set_cursor_visibility(False)

    game_over_image = ascii_helper.load_image("resources/dead_game_over.ascii")
    tombstone_image = ascii_helper.load_image("resources/dead_tombstone.ascii")

    game_over_x = int((screen.get_width() / 2) - (game_over_image["width"] / 2)) - 1
    tombstone_x = int((screen.get_width() / 2) - (tombstone_image["width"] / 2))

    screen.draw_ascii_image(game_over_x, 0, game_over_image)
    screen.draw_ascii_image(tombstone_x, game_over_image["height"] + 2, tombstone_image)

    screen.flush()

    time.sleep(2)

    screen.print_notification("Press any key to continue.", False)

    open_screen(screen_list["points"])


def draw_win_screen():
    screen.set_cursor_visibility(False)

    big_font = figlet_helper.load_font("resources/fonts/big.flf")
    contessa_font = figlet_helper.load_font("resources/fonts/contessa.flf")

    win_title_text = "You Win!"
    win_body_text = "You reached New York in time"

    win_title_width = figlet_helper.get_text_width(win_title_text, big_font)
    win_body_width = figlet_helper.get_text_width(win_body_text, contessa_font)

    win_title_x = int((screen.get_width() / 2) - (win_title_width / 2))
    win_body_x = int((screen.get_width() / 2) - (win_body_width / 2))

    screen.draw_ascii_font_text(win_title_x, 0, win_title_text, big_font)
    screen.draw_ascii_font_text(win_body_x, big_font["height"], win_body_text, contessa_font)

    screen.flush()

    time.sleep(4)

    screen.print_notification("Press any key to continue.", False)

    open_screen(screen_list["points"])


def draw_points_screen():
    screen.set_cursor_visibility(False)

    points = 0

    points += survivors.distance_travelled

    for survivor in survivors.survivor_list:
        if survivor["alive"]:
            points += survivor["health"]

    big_font = figlet_helper.load_font("resources/fonts/big.flf")

    score_title_x = int((screen.get_width() / 2) - (figlet_helper.get_text_width("Total Score", big_font) / 2))
    score_x = int((screen.get_width() / 2) - (figlet_helper.get_text_width(str(int(points)), big_font) / 2))

    screen.draw_ascii_font_text(score_title_x - 1, 1, "Total Score", big_font)
    screen.draw_ascii_font_text(score_x - 1, big_font["height"] + 1, str(int(points)), big_font)

    screen.flush()

    time.sleep(2)

    screen.print_notification("Press any key to exit.", False)

    screen.clear()

    quit()


def draw_city_screen():
    if survivors.distance_travelled == 0:
        city = cities.city_list["Los Angeles"]
    else:
        city = get_next_city(survivors.distance_travelled)

    while True:
        decisions = ["Put down bitten survivors", "Trade with other survivors",
                     "Rest", "Use medkits", "Scavenge",
                     "Move on to " + get_next_city(survivors.distance_travelled + survivors.car_speed)["name"]]

        selected_index = 1

        while True:
            screen.set_cursor_visibility(False)
            screen.draw_decision_box(city["description"].replace("\n", " ").strip(), decisions, selected_index)

            screen.flush()

            selected_index, finished = screen.get_decision_input(decisions, selected_index)

            if finished:
                screen.set_cursor_visibility(True)
                break

        if selected_index == 1:
            # Put down
            open_screen(screen_list["put_down"])
        elif selected_index == 2:
            # Trade
            open_screen(screen_list["trading"])
        elif selected_index == 3:
            # Rest
            open_screen(screen_list["resting"])
        elif selected_index == 4:
            # Use medkit
            open_screen(screen_list["medkit"])
        elif selected_index == 5:
            # Scavenge
            open_screen(screen_list["scavenging"])
        elif selected_index == 6:
            if "Fuel" not in survivors.group_inventory:
                screen.print_notification(
                    "You cannot leave the city until you have enough fuel. Try scavenging for some.", False)
            else:
                # Continue to previous screen
                return
        else:
            # Invalid input
            screen.print_notification("Please enter a number between 1 and 7.")


def draw_trading_screen():
    city = get_next_city(survivors.distance_travelled)

    trades = []

    if "saved_trades" in city:
        trades = city["saved_trades"]
    else:
        previous_trades = []

        for i in range(5):
            # None means use money
            survivors_item = None

            random_survivors_item_unit_value = 1

            # 60% chance, use random item - otherwise use money for this trade
            if random.randrange(1, 100) <= 60:
                # Get a random item from the group inventory
                survivors_item = get_random_dict_value(items.item_list)

            if survivors_item is not None:
                random_survivors_item_unit_value = random.randrange(survivors_item["min_value"],
                                                                    survivors_item["max_value"])

            for j in range(10):
                trader_item = None

                if survivors_item is None or random.randrange(1, 100) <= 60:
                    trader_item = get_random_dict_value(items.item_list)

                use_trade = True

                for previous_trade in previous_trades:
                    if previous_trade[0] == survivors_item and previous_trade[1] == trader_item:
                        use_trade = False
                        break

                    if previous_trade[1] == survivors_item and previous_trade[0] == trader_item:
                        use_trade = False
                        break

                if not use_trade:
                    continue

                random_trader_item_unit_value = 1

                if trader_item is not None:
                    random_trader_item_unit_value = random.randrange(trader_item["min_value"], trader_item["max_value"])

                survivors_item_amount = random_trader_item_unit_value / random_survivors_item_unit_value

                if survivors_item_amount < 1:
                    survivors_item_amount = 1

                trader_item_amount = random_survivors_item_unit_value / random_trader_item_unit_value

                if trader_item_amount < 1:
                    trader_item_amount = 1

                if survivors_item is None or trader_item != survivors_item:
                    if random_survivors_item_unit_value <= 10 and survivors_item_amount <= 10:
                        random_increase = random.randrange(11 - random_survivors_item_unit_value,
                                                           15 - random_survivors_item_unit_value)

                        survivors_item_amount *= random_increase
                        trader_item_amount *= random_increase

                    previous_trades.append([survivors_item, trader_item])

                    trades.append({"survivors_item": survivors_item, "trader_item": trader_item,
                                   "survivors_item_amount": survivors_item_amount,
                                   "trader_item_amount": trader_item_amount})

                    break

        city["saved_trades"] = trades

    for trade in list(trades):
        survivors_item = trade["survivors_item"]
        trader_item = trade["trader_item"]
        survivors_item_amount = trade["survivors_item_amount"]
        trader_item_amount = trade["trader_item_amount"]

        survivors_item_name = "Money"

        if survivors_item is not None:
            survivors_item_name = survivors_item["plural_name"]

        trader_item_name = "Money"

        if trader_item is not None:
            trader_item_name = trader_item["plural_name"]

        selected_index = 1

        decisions = ["Decline trade", "Accept trade", "Skip all further trades"]

        while True:
            screen.set_cursor_visibility(False)

            item_count = len(items.item_list) + 1

            decision_x, decision_y = screen.draw_decision_box(
                                              ("\n" * (item_count * 2 + 1))
                                              + "A survivor offers you a trade: \n\n"
                                              + "    You -----> " + str(int(survivors_item_amount)) + " " + survivors_item_name + "\n"
                                              + "    You <----- " + str(int(trader_item_amount)) + " " + trader_item_name,
                                                decisions, selected_index)

            item_index = 0
            for item in items.item_list.values():
                item_amount = 0

                if item["name"] in survivors.group_inventory:
                    item_amount = survivors.group_inventory[item["name"]]["amount"]

                screen.draw_text(decision_x + 6, decision_y + 3 + (item_index * 2),
                                 item["name"] + ": " + str(int(item_amount)))

                item_index += 1

            screen.draw_text(decision_x + 6, decision_y + 3 + (item_index * 2),
                             "Money: " + str(int(survivors.group_money)))

            item_index += 1

            screen.flush()

            selected_index, finished = screen.get_decision_input(decisions, selected_index)

            if finished:
                screen.set_cursor_visibility(True)
                break

        if selected_index == 1:
            continue
        elif selected_index == 2:
            if survivors_item is None:
                if survivors.group_money >= survivors_item_amount:
                    survivors.group_money -= survivors_item_amount
                    screen.print_notification("Trade completed successfully.", True)

                    if trader_item is None:
                        survivors.group_money += trader_item_amount
                    else:
                        survivors.inventory_add_item(trader_item, trader_item_amount)

                    city["saved_trades"].remove(trade)
                else:
                    screen.print_notification(
                        "Trade failed, you do not have enough " + survivors_item_name + " for this trade.", True)
            else:
                if survivors.inventory_remove_item(survivors_item, survivors_item_amount):
                    screen.print_notification("Trade completed successfully.", True)

                    if trader_item is None:
                        survivors.group_money += trader_item_amount
                    else:
                        survivors.inventory_add_item(trader_item, trader_item_amount)

                    city["saved_trades"].remove(trade)
                else:
                    screen.print_notification(
                        "Trade failed, you do not have enough " + survivors_item_name + " for this trade.", True)

            continue
        if selected_index == 3:
            screen.print_notification("Skipped all further trades.", True)
            return
        else:
            continue

    screen.print_notification("There are no more trades to show.", False)


def draw_medkit_screen():
    while True:
        medkit_count = 0

        if "Medkit" in survivors.group_inventory:
            medkit_count = survivors.group_inventory["Medkit"]["amount"]

        decisions = ["Go back to city screen"]

        selected_index = 1

        survivor_count = count_survivors(True, True, True, True)

        for survivor in survivors.survivor_list:
            if survivor["alive"]:
                decisions.append("Use medkit on " + survivor["name"])

        while True:
            screen.set_cursor_visibility(False)

            decision_x, decision_y = screen.draw_decision_box("Your group has " + str(int(medkit_count)) + " " + (
                "Medkit" if medkit_count == 1 else "Medkits") + "." + ("\n" * (survivor_count * 2)), decisions,
                                                              selected_index, max_height=(survivor_count * 6) + 2)

            stats_y_start = decision_y + 4
            stats_x_start = decision_x + 6

            stats_y = stats_y_start

            health_x = 0

            for survivor in survivors.survivor_list:
                survivor_name = survivor["name"]
                name_length = len(survivor_name)

                if name_length > health_x:
                    health_x = name_length

                screen.draw_text(stats_x_start, stats_y + 1, survivor_name)

                stats_y += 2

            stats_y = stats_y_start + 1

            total_bars = 14

            for survivor in survivors.survivor_list:
                if survivor["alive"]:
                    screen.draw_progress_bar(stats_x_start + health_x + 2, stats_y, total_bars,
                                             survivor["health"] / survivor["max_health"])

                    if survivor["zombified"]:
                        screen.draw_text(stats_x_start + health_x + total_bars + 5, stats_y, "(ZOMBIE)")
                    elif survivor["bitten"]:
                        screen.draw_text(stats_x_start + health_x + total_bars + 5, stats_y, "(BITTEN)")
                else:
                    padding = int((total_bars - 4) / 2)
                    screen.draw_text(stats_x_start + health_x + 2, stats_y,
                                     "[" + (padding * " ") + "DEAD" + (padding * " ") + "]")

                stats_y += 2

            screen.flush()

            selected_index, finished = screen.get_decision_input(decisions, selected_index)

            if finished:
                screen.set_cursor_visibility(True)
                break

        if selected_index == 1:
            # Return to city menu screen
            return
        elif selected_index >= 2:
            # Search through options available to find who to kill

            survivor_index = 0

            selected_survivor = None

            for survivor in survivors.survivor_list:
                if survivor["alive"]:
                    if survivor_index == selected_index - 2:
                        selected_survivor = survivor
                        break

                    survivor_index += 1

            if survivors.inventory_remove_item(items.item_list["Medkit"], 1):
                screen.print_notification("You used the medkit on " + selected_survivor["name"] + ".")

                selected_survivor["health"] = selected_survivor["max_health"]
            else:
                screen.print_notification("You don't have enough medkits to heal up this person.")
            continue
        else:
            print("Please enter a number between 1 and 6.")
            continue

    if "Medkit" not in survivors.group_inventory:
        screen.print_notification("Your group has 0 Medkits remaining.")

    screen.print_notification("Press any button to continue...", False)


def draw_resting_screen():
    while True:
        screen.clear()

        for survivor in survivors.survivor_list:
            if survivor["alive"]:
                print("{0} ({1} / {2}): ".format(survivor["name"], survivor["health"], survivor["max_health"]))
                print()

        print("Each survivor gains 10 health per hour rested.")
        print("Type 0 hours to go back to the city screen.")
        print()
        sleep_choice = input("How many hours would you like to rest? ")

        try:
            sleep_choice = int(normalise_input(sleep_choice))
        except ValueError:
            print()
            print("<--Please enter a number between 0 and 9-->")
            time.sleep(1)
            continue
        screen.clear()

        if sleep_choice < 10:
            if sleep_choice > 0:
                for survivor in survivors.survivor_list:
                    if survivor["alive"]:
                        old_health = survivor["health"]
                        survivor["health"] += sleep_choice * 10
                        if survivor["health"] > survivor["max_health"]:
                            survivor["health"] = survivor["max_health"]
                        print("{0} has slept for {1} hour(s) and gained {2} health.".format(survivor["name"],
                                                                                            sleep_choice,
                                                                                            survivor[
                                                                                                "health"] - old_health))

            game.pass_time(sleep_choice, False)

            screen.print_notification("Press any button to continue...", False)

            return
        else:
            print("Please enter a number between 1 and 9.")


def draw_put_down_screen():
    # Display options
    while True:
        decisions = ["Go back to city screen"]

        selected_index = 1

        survivor_count = count_survivors(True, True, True, True)

        survivor_index = 0
        for survivor in survivors.survivor_list:
            if survivor_index == 0:
                decisions.append("Put down yourself")
            else:
                if survivor["alive"]:
                    decisions.append("Put down " + survivor["name"])

            survivor_index += 1

        while True:
            screen.set_cursor_visibility(False)

            decision_x, decision_y = screen.draw_decision_box("\n" * ((survivor_count * 2) - 2), decisions,
                                                              selected_index, max_height=(survivor_count * 6))

            stats_y_start = decision_y + 2
            stats_x_start = decision_x + 6

            stats_y = stats_y_start

            health_x = 0

            for survivor in survivors.survivor_list:
                survivor_name = survivor["name"]
                name_length = len(survivor_name)

                if name_length > health_x:
                    health_x = name_length

                screen.draw_text(stats_x_start, stats_y + 1, survivor_name)

                stats_y += 2

            stats_y = stats_y_start + 1

            total_bars = 14

            for survivor in survivors.survivor_list:
                if survivor["alive"]:
                    screen.draw_progress_bar(stats_x_start + health_x + 2, stats_y, total_bars,
                                             survivor["health"] / survivor["max_health"])

                    if survivor["zombified"]:
                        screen.draw_text(stats_x_start + health_x + total_bars + 5, stats_y, "(ZOMBIE)")
                    elif survivor["bitten"]:
                        screen.draw_text(stats_x_start + health_x + total_bars + 5, stats_y, "(BITTEN)")
                else:
                    padding = int((total_bars - 4) / 2)
                    screen.draw_text(stats_x_start + health_x + 2, stats_y,
                                     "[" + (padding * " ") + "DEAD" + (padding * " ") + "]")

                stats_y += 2

            screen.flush()

            selected_index, finished = screen.get_decision_input(decisions, selected_index)

            if finished:
                screen.set_cursor_visibility(True)
                break

        if selected_index == 1:
            # Return to city menu screen
            return
        elif selected_index == 2:
            # Suicide
            open_screen(screen_list["dead"])
        elif selected_index >= 3:
            # Search through options available to find who to kill

            survivor_index = 0

            selected_survivor = None

            for survivor in survivors.survivor_list:
                if survivor["alive"]:
                    if survivor_index == selected_index - 2:
                        selected_survivor = survivor
                        break

                    survivor_index += 1

            selected_survivor["alive"] = False
            screen.print_notification("You put down " + selected_survivor["name"])
            continue
        else:
            print("Please enter a number between 1 and 6.")
            continue


def draw_travelling_screen():
    if previous_screen is None:
        open_screen(screen_list["starting"])

    screen.set_cursor_visibility(False)

    show_next_city_notification = previous_screen is not None and previous_screen["name"] == "city"

    car_body_image = ascii_helper.load_image("resources/car_body.ascii")
    car_wheel_image_1 = ascii_helper.load_image("resources/car_wheel_1.ascii")
    car_wheel_image_2 = ascii_helper.load_image("resources/car_wheel_2.ascii")

    stats_x_start = int(screen.get_width() / 10)
    stats_y_start = screen.get_height() - ((len(survivors.survivor_list) + 1) * 2) - 1

    car_x = int((screen.get_width() / 2) - (car_body_image["width"] / 2))
    car_y = stats_y_start - car_body_image["height"] - 5

    iterations = 0
    wheel = 0
    road = 0

    while True:
        # Draw travelling progress bar
        progress_bar_box_width = int(screen.get_width() / 1.5)
        progress_bar_box_x = int((screen.get_width() / 2) - (progress_bar_box_width / 2))

        progress_bar_width = progress_bar_box_width - 6

        screen.draw_bordered_rect(progress_bar_box_x, -1, progress_bar_box_width, 5)

        for x in range(progress_bar_box_x + 3, progress_bar_box_x + progress_bar_box_width - 3):
            screen.draw_pixel(x, 1, "-")

        progress_bar_current_x = progress_bar_box_x + 3 + (
            (survivors.distance_travelled / get_end_distance()) * progress_bar_width)

        end_distance = get_end_distance()

        for city in cities.city_list.values():
            screen.draw_pixel(
                progress_bar_box_x + 3 + int((city["distance_from_start"] / end_distance) * (progress_bar_width - 1)),
                1, "|")

        screen.draw_pixel(int(progress_bar_current_x), 2, "^")

        # Draw survivors and car stats
        stats_y = stats_y_start

        health_x = 0

        name_length = len("Fuel")

        if name_length > health_x:
            health_x = name_length

        screen.draw_text(stats_x_start, stats_y + 1, "Fuel")

        stats_y += 2

        for survivor in survivors.survivor_list:
            survivor_name = survivor["name"]
            name_length = len(survivor_name)

            if name_length > health_x:
                health_x = name_length

            screen.draw_text(stats_x_start, stats_y + 1, survivor_name)

            stats_y += 2

        stats_y = stats_y_start + 1

        total_bars = 14

        fuel_amount = 0

        if "Fuel" in survivors.group_inventory:
            fuel_amount = survivors.group_inventory["Fuel"]["amount"]

        screen.draw_progress_bar(stats_x_start + health_x + 2, stats_y, total_bars, fuel_amount / max(fuel_amount, 60))

        stats_y += 2

        for survivor in survivors.survivor_list:
            if survivor["alive"]:
                screen.draw_progress_bar(stats_x_start + health_x + 2, stats_y, total_bars,
                                         survivor["health"] / survivor["max_health"])

                if survivor["zombified"]:
                    screen.draw_text(stats_x_start + health_x + total_bars + 5, stats_y, "(ZOMBIE)")
                elif survivor["bitten"]:
                    screen.draw_text(stats_x_start + health_x + total_bars + 5, stats_y, "(BITTEN)")
            else:
                padding = int((total_bars - 4) / 2)
                screen.draw_text(stats_x_start + health_x + 2, stats_y,
                                 "[" + (padding * " ") + "DEAD" + (padding * " ") + "]")

            stats_y += 2

        # Draw stats
        next_city = get_next_city(survivors.distance_travelled)

        amount_of_food = 0

        if "Food" in survivors.group_inventory:
            amount_of_food = survivors.group_inventory["Food"]["amount"]

        stat_lines = ["Time: " + format_time(survivors.current_datetime),
                      "Date: " + format_date(survivors.current_datetime),
                      "Next City: " + next_city["name"], "Food: " + str(int(amount_of_food))]

        longest_line = 0

        for stat_line in stat_lines:
            stat_line_length = len(stat_line)
            if stat_line_length > longest_line:
                longest_line = stat_line_length

        stat_x = int(screen.get_width() - longest_line - (screen.get_width() / 10) + 2)
        stat_y = stats_y_start + 1

        for stat_line in stat_lines:
            screen.draw_text(stat_x, stat_y, stat_line)

            stat_y += 2

        # Draw the car
        screen.draw_ascii_image(car_x, car_y, car_body_image)

        if wheel <= 0.25:
            screen.draw_ascii_image(car_x + 14, car_y + 7, car_wheel_image_2)
            screen.draw_ascii_image(car_x + 53, car_y + 7, car_wheel_image_2)
        else:
            screen.draw_ascii_image(car_x + 14, car_y + 7, car_wheel_image_1)
            screen.draw_ascii_image(car_x + 53, car_y + 7, car_wheel_image_1)

        for x in range(screen.get_width()):
            pixel_char = "="

            if road < 1:
                if x % 2 == 0:
                    pixel_char = "-"
            else:
                if x % 2 != 0:
                    pixel_char = "-"

            screen.draw_pixel(x, car_y + car_body_image["height"] + 2, pixel_char)

        screen.flush()

        if show_next_city_notification:
            next_city = get_next_city(survivors.distance_travelled)
            screen.print_notification(next_city["name"] + " is " + str(
                int(next_city["distance_from_start"] - survivors.distance_travelled)) + " miles away.")
            show_next_city_notification = False

        wheel += 0.25
        road += 1

        if wheel > 1:
            iterations += 1

            if iterations > 2:
                return

        if road > 1:
            road = 0

        time.sleep(0.5 - (survivors.car_speed / 100.0))

        screen.set_cursor_visibility(False)


def draw_scavenging_screen():
    screen.clear()
    print("Type 0 hours to go back to the city screen.")
    print("")
    # Declaring variables
    number_of_survivors = count_survivors()

    scavenging_time = 0

    # Input
    while True:
        try:
            scavenging_time = int(input("How many hours would you like to scavenge for? "))
        except ValueError:
            print("Invalid input, please enter a number greater than 0")
            continue

        if scavenging_time == 0:
            screen.print_notification("Press any key to continue...", False)
            return
        if scavenging_time > 4:
            print("You cannot scavenge for longer than 4 hours at a time.")
        elif scavenging_time < 1:
            print("Invalid input, please enter a number greater than 0")
        else:
            break

    items_found = {}

    # Random generators
    # Get prob - determines the probability of finding an object based on number of survivors present
    def get_prob_val():
        if number_of_survivors == 4:
            return randint(0, 5)
        elif number_of_survivors == 3:
            return randint(0, 7)
        elif number_of_survivors == 2:
            return randint(0, 12)
        elif number_of_survivors == 1:
            return randint(0, 15)

    # Get health - determines how much health a survivor should lose based on number of survivors present
    def get_health_val():
        if number_of_survivors > 2:
            return randint(0, 2)
        elif number_of_survivors == 2:
            return randint(0, 4)
        elif number_of_survivors == 1:
            return randint(0, 8)

    for i in range(0, scavenging_time * 7):
        for x in range(0, 4):
            if survivors.survivor_list[x]["alive"]:
                survivors.survivor_list[x]["health"] = survivors.survivor_list[x]["health"] - get_health_val()
        if survivors.survivor_list[0]["health"] <= 0:
            screen.clear()
            screen.print_notification("You died whilst scavenging.", False)
            survivors.survivor_list[0]["alive"] = False
            open_screen(screen_list["dead"])
        if get_prob_val() == 1:
            random_item = get_random_dict_value(items.item_list)
            random_item_unit_value = random.randrange(random_item["min_value"], random_item["max_value"])

            item_amount = 1

            if random_item_unit_value <= 20:
                random_increase = random.randrange(21 - random_item_unit_value,
                                                   25 - random_item_unit_value)

                item_amount *= random_increase

            item_amount = int(item_amount)

            if random_item["name"] in items_found:
                items_found[random_item["name"]]["amount"] += item_amount
            else:
                items_found[random_item["name"]] = {"item": random_item, "amount": item_amount}

            survivors.inventory_add_item(random_item, item_amount)
    screen.clear()
    print("During your time scavenging your party took damage:")

    for survivor in survivors.survivor_list:
        if survivor["alive"] and survivor["health"] > 0:
            print(survivor["name"] + " has " + str(survivor["health"]) + " health.")
        elif survivor["alive"] and survivor["health"] <= 0:
            print(survivor["name"] + " died while scavenging")
            survivor["alive"] = False

    print("")

    if survivors.is_first_time_scavenging and "Fuel" not in items_found:
        random_item = items.item_list["Fuel"]
        item_amount = random.randrange(10, 40)

        items_found["Fuel"] = {"item": random_item, "amount": item_amount}
        survivors.inventory_add_item(random_item, item_amount)

    survivors.is_first_time_scavenging = False

    if len(items_found) == 0:
        print("You did not find anything useful while scavenging.")
    else:
        print("While scavenging you found the following items:")

        for item_found in items_found.values():
            item_found_amount = int(item_found["amount"])
            print(str(item_found_amount) + " " + (
                item_found["item"]["name"] if item_found_amount <= 0 else item_found["item"]["plural_name"]))

        print()
        print("Your group now has:")

        for item_found in survivors.group_inventory.values():
            item_found_amount = int(item_found["amount"])
            print(str(item_found_amount) + " " + (
                item_found["item"]["name"] if item_found_amount <= 0 else item_found["item"]["plural_name"]))

    # Need to pass time
    game.pass_time(scavenging_time, False)

    screen.print_notification("Press any key to continue...", False)


def draw_fuel_screen():
    decisions = ["Scavenge", "Rest", "Use medkit", "Continue on trail"]

    selected_index = 1

    while True:
        while True:
            screen.set_cursor_visibility(False)

            screen.draw_decision_box(
                "You have run out of fuel and cannot travel any further. You must scavenge for fuel. You may use medkits and resting in order to heal. Don't stick around too long, who knows what's hanging around here!",
                decisions, selected_index)

            screen.flush()

            selected_index, finished = screen.get_decision_input(decisions, selected_index)

            if finished:
                screen.set_cursor_visibility(True)
                break

        if selected_index == 1:
            # Scavenge
            open_screen(screen_list["scavenging"])
        elif selected_index == 2:
            # Rest
            open_screen(screen_list["resting"])
        elif selected_index == 3:
            # Medkit
            open_screen(screen_list["medkit"])
        elif selected_index == 4:
            if "Fuel" in survivors.group_inventory:
                # Continue travelling
                return
            else:
                screen.print_notification("You do not have enough fuel to keep travelling.")


screen_list = {
    "starting": {
        "name": "starting",

        "draw_function": draw_starting_screen,

        "one_time": True
    },

    "dead": {
        "name": "dead",

        "draw_function": draw_dead_screen,

        "one_time": True
    },

    "win": {
        "name": "win",

        "draw_function": draw_win_screen,

        "one_time": True
    },

    "points": {
        "name": "points",

        "draw_function": draw_points_screen,

        "one_time": True
    },

    "city": {
        "name": "city",

        "draw_function": draw_city_screen,

        "one_time": False
    },

    "trading": {
        "name": "trading",

        "draw_function": draw_trading_screen,

        "one_time": False
    },

    "resting": {
        "name": "resting",

        "draw_function": draw_resting_screen,

        "one_time": False
    },

    "put_down": {
        "name": "put_down",

        "draw_function": draw_put_down_screen,

        "one_time": False
    },

    "travelling": {
        "name": "travelling",

        "draw_function": draw_travelling_screen,

        "one_time": False
    },

    "info": {
        "name": "info",

        "draw_function": draw_info_screen,

        "one_time": False
    },

    "survivor_name": {
        "name": "survivor_name",

        "draw_function": draw_survivor_name_screen,

        "one_time": True
    },

    "medkit": {
        "name": "medkit",

        "draw_function": draw_medkit_screen,

        "one_time": False
    },

    "scavenging": {
        "name": "scavenging",

        "draw_function": draw_scavenging_screen,

        "one_time": False

    },

    "fuel": {
        "name": "fuel",

        "draw_function": draw_fuel_screen,

        "one_time": False
    },
}
