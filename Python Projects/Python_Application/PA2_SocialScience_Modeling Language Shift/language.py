"""
MACS 30121: Language shifts

Jingwen Lu

Functions for language shift simulation.

This program takes the following parameters:
    grid _file (string): the name of a file containing a sample region
    R (int): neighborhood radius
    A (float): the language state transition threshold A
    Bs (list of floats): a list of the transition thresholds B to
      use in the simulation
    C (float): the language state transition threshold C
      centers (list of tuples): a list of community centers in the
      region
    max_steps (int): maximum number of steps

Example use:
    $ python3 language.py -grid_file tests/writeup-grid-with-cc.txt
	  --r 2 --a 0.5 --b 0.9 --c 1.2 --max_steps 5
While shown on two lines, the above should be entered as a single command.
"""

import copy
import click
import utility


def if_in_com_center(home_loc, com_center):
    '''
    Judge whether the given home is within the community 
    center's service distance (when there is at least one
    community center)

    Inputs:
        home_loc (tuple): the location of the given home
        com_center (tuple with (tuple, int) as elements):
            the location of the community center(tuple),
            the service distance (int)

    Returns: whether the given home is within the community 
        center's service distance (bool)
    '''

    i_home_loc = home_loc[0]
    j_home_loc = home_loc[1]
    i_center_home = com_center[0][0]
    j_center_home = com_center[0][1]
    r = com_center[1]
    cen_result = (i_home_loc >= i_center_home - r) and (
        i_home_loc <= i_center_home + r) and (
            j_home_loc >= j_center_home - r) and (
                j_home_loc <= j_center_home + r)
    return cen_result


def engage_level(rad, home_loc, grid):
    '''
    Calculate the engagement level of a given home

    Inputs:
        rad (int): neighborhood radius
        home_loc (tuple): the home's location
        grid (list of lists of ints): the grid

    Returns: the engagement level of the given home (float)
    '''

    sum_lang_prefer = 0
    n_grid = len(grid)
    low_i = home_loc[0] - rad
    up_i = home_loc[0] + rad
    low_j = home_loc[1] - rad
    up_j = home_loc[1] + rad
    low_i = max(low_i, 0)
    low_j = max(low_j, 0)
    up_i = min(up_i, n_grid - 1)
    up_j = min(up_j, n_grid - 1)
    for i in range(low_i, up_i + 1):
        for j in range(low_j, up_j + 1):
            sum_lang_prefer += grid[i][j]
    total_homes = (up_i - low_i + 1) * (up_j - low_j + 1)
    return sum_lang_prefer / total_homes


def transmission_home(rad, home_loc, grid, centers, thresholds):
    '''
    Determine the language state of the next generation in a given
    home according to the transmission rules

    Inputs:
        rad (int): neighborhood radius
        home_loc (tuple): the home's location
        grid (list of lists of ints): the grid
        centers (list of tuples): a list of community centers in the
            region
        thresholds (float, float, float): the language
            state transition thresholds (A, B, C)

    Return:the language state of the next generation in the given
        home (int)
    '''

    if centers == []:
        if_in_community_center = False
    else:
        for com_center in centers:
            if_in_community_center = if_in_com_center(home_loc, com_center)
            if if_in_community_center:
                break

    i_home = home_loc[0]
    j_home = home_loc[1]
    status_home = grid[i_home][j_home]
    thresh_a, thresh_b, thresh_c = thresholds[0], thresholds[1], thresholds[2]
    engagement_level = engage_level(rad, home_loc, grid)

    if status_home == 0:
        if engagement_level <= thresh_b:
            next_stage = 0
        else:
            next_stage = 1
    elif status_home == 1:
        if engagement_level < thresh_b:
            if if_in_community_center:
                next_stage = 1
            else:
                next_stage = 0
        elif engagement_level <= thresh_c:
            next_stage = 1
        else:
            next_stage = 2
    else:
        if if_in_community_center:
            next_stage = 2
        elif engagement_level >= thresh_b:
            next_stage = 2
        elif engagement_level > thresh_a:
            next_stage = 1
        else:
            next_stage = 0

    return next_stage


def run_simulation(grid, rad, thresholds, centers, max_steps):
    """
    Do the simulation.

    Inputs:
      grid (list of lists of ints): the grid
      rad (int): neighborhood radius
      thresholds (float, float, float): the language
        state transition thresholds (A, B, C)
      centers (list of tuples): a list of community centers in the
        region
      max_steps (int): maximum number of steps

    Returns: the frequency of each language state (int, int, int)
    """

    n_grid = len(grid)
    stop_signal = True

    for step in range(max_steps):
        for i in range(n_grid):
            for j in range(n_grid):
                home_loc = (i, j)
                transmitted = transmission_home(rad, home_loc, grid,
                                                centers, thresholds)
                if grid[i][j] != transmitted and stop_signal:
                    stop_signal = False
                grid[i][j] = transmitted
        if stop_signal:
            break

    count_0, count_1, count_2 = 0, 0, 0
    for row in grid:
        for status in row:
            if status == 0:
                count_0 += 1
            elif status == 1:
                count_1 += 1
            else:
                count_2 += 1

    return tuple([count_0, count_1, count_2])


def simulation_sweep(grid, rad, a, bs, c, centers, max_steps):
    """
    Run the simulation with various values of threshold B.

    Inputs:
      grid (list of lists of ints): the grid
      rad (int): neighborhood radius
      a (float): the language state transition threshold A
      bs (list of floats): a list of the transition thresholds B to
        use in the simulation
      c (float): the language state transition threshold C
      centers (list of tuples): a list of community centers in the
        region
      max_steps (int): maximum number of steps

    Returns: a list of frequencies (tuples) of language states for
      each threshold B.
    """

    frequencies = []

    for thresh_b in bs:
        grid_copy = copy.deepcopy(grid)
        thresholds = (a, thresh_b, c)
        frequency = run_simulation(grid_copy, rad, thresholds,
                                   centers, max_steps)
        frequencies.append(frequency)

    return frequencies


@click.command(name="language")
@click.option('--grid_file', type=click.Path(exists=True),
              default="tests/writeup-grid.txt", help="filename of the grid")
@click.option('--r', type=int, default=1, help="neighborhood radius")
@click.option('--a', type=float, default=0.6, help="transition threshold A")
@click.option('--b', type=float, default=0.8, help="transition threshold B")
@click.option('--c', type=float, default=1.6, help="transition threshold C")
@click.option('--max_steps', type=int, default=1,
              help="maximum number of simulation steps")
def cmd(grid_file, r, a, b, c, max_steps):
    '''
    Run the simulation.
    '''

    grid, centers = utility.read_grid(grid_file)
    print_grid = len(grid) < 20

    print("Running the simulation...")

    if print_grid:
        print("Initial region:")
        for row in grid:
            print("   ", row)
        if len(centers) > 0:
            print("With community centers:")
            for center in centers:
                print("   ", center)

    # run the simulation
    frequencies = run_simulation(grid, r, (a, b, c), centers, max_steps)

    if print_grid:
        print("Final region:")
        for row in grid:
            print("   ", row)

    print("Final language state frequencies:", frequencies)

if __name__ == "__main__":
    cmd()
