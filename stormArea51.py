import configparser
import os
import random
from enum import  Enum


class FightResult(Enum):
    """
    Enum for better handling of fight results
    """
    WIN = 'win'
    LOSS = 'loss'


def read_config():
    """
    Reads the config file or creates one if it doesn't exist.
    :return:  config
    """
    # Create var.ini if not found in directory
    if not os.path.exists('var.ini'):
        print("No config found, creating config.")
        config = configparser.ConfigParser()
        config['people'] = {'civilians': '150',
                            'civilianHitRate': '33',
                            'troops': '250',
                            'troopHitRate': '85'}
        config['base'] = {'troopsPerFloor': '45',
                          'floorMinimum': '50',
                          'floorMaximum': '90',
                          'aliensSpawn': '15',
                          'doorTime': '15',
                          'reinforcements': '60'
                          }
        config['aliens'] = {'alignment': 'good'}

        with open('var.ini', 'w') as configfile:
            config.write(configfile)
    else:
        config = configparser.ConfigParser()
        config.sections()
        config.read('var.ini')

    return config


def fight(mil_pop, civ_pop, mil_killed, civ_hit_rate, mil_hit_rate):
    """
    Fighting simulation
    this determines who wins a battle and who looses it

    :param mil_pop:      military population count
    :param civ_pop:      civilian population count
    :param mil_killed:   number of military killed
    :param civ_hit_rate: hit rate of the civilians
    :param mil_hit_rate: hit rate of the military
    :return:
    """
    attack_round = 0

    mil_start_pop = mil_pop
    civ_start_pop = civ_pop
    while civ_pop > 0 and mil_pop > 0:
        turn = random.randrange(1, 3)
        if turn == 1:
            atk = random.randrange(0, 101)
            if atk <= civ_hit_rate:
                mil_pop = mil_pop - 1
        else:
            atk = random.randrange(0, 101)
            if atk <= mil_hit_rate:
                civ_pop = civ_pop - 1
        attack_round = attack_round + 1
    if civ_pop <= 0:
        print("After a long battle the civilans have lost.")
        print("the fight Lasted ", attack_round, " rounds.")
        mil_killed = mil_killed + mil_start_pop - mil_pop
        print(mil_start_pop - mil_pop, " Military personal were killed that floor.")
        return FightResult.LOSS, mil_killed, civ_pop
    else:
        print("Civilans have won the fight.")
        print("the fight Lasted ", attack_round, " rounds.")
        print(civ_pop, " civilans remain.")
        mil_killed = mil_killed + mil_start_pop
        print(civ_start_pop - civ_pop, " Civilans were killed that floor.")
        return FightResult.WIN, mil_killed, civ_pop


def building_fight(alien_alignment, alien_spawn, civ_hit_rate, civ_pop, config, current_floor, mil_hit_rate,
                   mil_killed):
    """
    Fighting in the area 51 building
    This function is called in the main loop and simulates fights on each floor of the builiding.

    :param alien_alignment: good or bad aliens?
    :param alien_spawn:     spawn rate of the aliens
    :param civ_hit_rate:    hit rate of the civilians
    :param civ_pop:         population of the civilians
    :param config:          configuration object
    :param current_floor:   current floor for the fight
    :param mil_hit_rate:    hit rate of the military
    :param mil_killed:      killed military
    :return: [civ_pop, current_floor]
    """
    troops_per_floor = int(config['base']['troopsPerFloor'])
    print("Current floor ", current_floor)
    if current_floor >= alien_spawn and alien_alignment == 'good' and civ_hit_rate < 100:
        civ_hit_rate += 20
        if civ_hit_rate > 100:
            civ_hit_rate = 100
    elif config['aliens']['alignment'] == 'bad':
        troops_per_floor = troops_per_floor - round(troops_per_floor / 10)
        print("Due to aliens there will only be", troops_per_floor, "troops on this floor.")
        civ_pop -= 10
    result, mil_killed, civ_pop = fight(troops_per_floor, civ_pop, mil_killed, civ_hit_rate, mil_hit_rate)
    if result == FightResult.WIN:
        current_floor = current_floor + 1
    else:
        print("You made it to floor ", current_floor)
        print(mil_killed, " Military personal were killed.")
        print(int(config['people']['civilians']), "Civilans were killed.")
    return civ_pop, current_floor


def main():
    """
    Main entry function
    First simulates the storm to area 51 and then the fighting inside the building.
    """
    config = read_config()

    civ_pop = int(config['people']['civilians'])
    mil_pop = int(config['people']['troops'])
    civ_hit_rate = int(config['people']['civilianHitRate'])
    mil_hit_rate = int(config['people']['troopHitRate'])
    mil_killed = 0

    print("storming Area-51")
    print("civilian hit rate set to :" + config['people']['civilianHitRate'])
    print("military hit rate set to :" + config['people']['troopHitRate'])

    # First call of fight,
    result, mil_killed, civ_pop = fight(mil_pop, civ_pop, mil_killed, civ_hit_rate, mil_hit_rate)

    # Only if the civialans have won the first fight will it generate the rest of the base
    # no point running code that will never be used.
    if result == FightResult.WIN:
        alien_spawn = int(config['base']['aliensSpawn'])
        alien_alignment = config['aliens']['alignment']

        floor_min = int(config['base']['floorMinimum'])
        floor_max = int(config['base']['floorMaximum'])

        number_of_floors = random.randrange(floor_min, floor_max + 1)
        current_floor = 1
        while current_floor <= number_of_floors and civ_pop > 0:
            civ_pop, current_floor = building_fight(alien_alignment, alien_spawn, civ_hit_rate, civ_pop, config,
                                                    current_floor, mil_hit_rate, mil_killed)


if __name__ == '__main__':
    main()
