import time

import pulp as pl  # https://coin-or.github.io/pulp/


def sudoku_solve(json_data: dict, solver_cfg: dict, regions = None) -> list:
    """
    Using Integer Programming to solve the killer sudoku

    :param json_data: json dictionary containing sum groups and known numbers
    :param solver_cfg: The config of the solver
    :param regions: All regions in the grid
    :return: list of all known numbers (all large) which is the solution
    """
    solver = pl.getSolverFromDict(solver_cfg)
    
    m = pl.LpProblem()

    if regions is None:
        regions = [[(a, b) for a in range(c, c + 3) for b in range(d, d + 3)] for c in [0, 3, 6] for d in [0, 3, 6]]

    x = {}
    for i in range(9):  # row
        for j in range(9):  # col
            for k in range(1, 10):  # num
                var_id = str(i) + str(j) + str(k)
                x[var_id] = pl.LpVariable(name=f'x_({var_id})', cat='Binary')

    for i in range(9):  # row
        for j in range(9):  # col
            m += pl.lpSum(x[str(i) + str(j) + str(k)] for k in range(1, 10)) == 1, f'row_{i}_col_{j}'

    for i in range(9):
        for k in range(1, 10):
            m += pl.lpSum(x[str(i) + str(j) + str(k)] for j in range(9)) == 1, f'row_{i}_nbr_{k}'

    for j in range(9):
        for k in range(1, 10):
            m += pl.lpSum(x[str(i) + str(j) + str(k)] for i in range(9)) == 1, f'col_{j}_nbr_{k}'

    for k in range(1, 10):
        for idx in range(len(regions)):
            m += pl.lpSum(x[str(a) + str(b) + str(k)] for a, b in regions[idx]) == 1, f'region_({idx})_({k})'

    for i, sum_group in enumerate(json_data['sum_groups']):
        m += pl.lpSum(k * x[str(a) + str(b) + str(k)]
                      for a, b in sum_group['coords']
                      for k in range(1, 10)) == sum_group['sum'], f'sum({i})'

    for known_number in json_data['known_numbers']:
        if not known_number['small']:
            a, b = known_number['coord']
            k = known_number['possible_numbers'][0]
            m += x[str(a) + str(b) + str(k)] == 1

    # m.writeLP('sudoku.lp')
    tic = time.time()
    m.solve(solver=solver)
    print('Solve Time: ' + str(time.time() - tic))

    known_nbrs = []

    for i in range(9):
        for j in range(9):
            for k in range(1, 10):
                var_id = str(i) + str(j) + str(k)
                if pl.value(x[var_id]) is None:
                    continue
                if pl.value(x[var_id]) > 0.9:
                    known_nbrs.append({'coord': (i, j),
                                       'small': False,
                                       'possible_numbers': [k]})

    return known_nbrs
