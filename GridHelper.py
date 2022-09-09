def calc_size(grid_parameters: dict) -> dict:
    """
    calculates additional parameters using the given grid parameters dict

    :param grid_parameters: dict of drawing parameters
    :return: the same dict with some new parameters
    """
    # calculate overall grid size
    size = (grid_parameters['white_boarder_width'] * 2 +  # two white boarders (left/right & top/bottom)
            grid_parameters['cell_size'] * 9 +  # nine cells each direction
            grid_parameters['main_width'] * 4 +  # four bold lines each direction (separates all boxes)
            grid_parameters['inside_width'] * 6)  # another six lines each direction (separates all cells)

    # first boarder position
    cur_position = (grid_parameters['white_boarder_width'] +  # one white boarders (left & top)
                    grid_parameters['main_width'])  # one bold line width (the left/top most point of the cell)

    if grid_parameters['grid_label']:  # if the params specify draw labels
        # another one bold line's width and the label width
        size += grid_parameters['main_width'] + grid_parameters['grid_label_width']
        cur_position += grid_parameters['grid_label_width'] + grid_parameters['main_width']
    size = int(size * grid_parameters['scale'])  # final size = scale
    grid_parameters['size'] = size

    boarders = [cur_position]  # inside boarders

    for i in range(9):
        cur_position += grid_parameters['cell_size']
        if i in (2, 5, 8):  # bold line position
            cur_position += grid_parameters['main_width']
        else:  # normal line position
            cur_position += grid_parameters['inside_width']
        boarders.append(cur_position)

    # cur_position += grid_parameters['cell_size']
    # boarders.append(cur_position)
    grid_parameters['boarders'] = boarders

    return grid_parameters


def select_idx(x: float, y: float, boarders: list, y_boarders = None) -> tuple[int, int]:
    """
    transform the coordinates to the cell index.
    (when boarders are given)

    :param x: x of drawing coordinates
    :param y: y of drawing coordinates
    :param boarders: the boarders of different cells (in drawing coordinates)
    :param y_boarders: the y-axis boarders of different cells (if differ from x-axis boarders)
    :return: the cell index of the selected position
    """
    if y_boarders is None:
        y_boarders = boarders

    ind_row, ind_col = -1, -1
    for i in range(9):
        if ind_row != -1:
            break
        range_start = y_boarders[i]
        range_end = y_boarders[i + 1]
        if range_start <= y <= range_end:
            ind_row = i

    for i in range(9):
        if ind_col != -1:
            break
        range_start = boarders[i]
        range_end = boarders[i + 1]
        if range_start <= x <= range_end:
            ind_col = i
    if ind_row < 0 or ind_col < 0:
        return -1, -1
    return ind_row, ind_col


def calc_center_coord(cell: tuple[int, int], boarders: list, cell_size: float) -> tuple[float, float]:
    """
    calculates the drawing coordinates of the center of a given cell

    :param cell: the selected cell index
    :param boarders: the boarders of different cells (in drawing coordinates)
    :param cell_size: the size (in graph) of each cell
    :return: the drawing coordinates of the center of the cell
    """
    coord_x = boarders[cell[1]] + cell_size / 2
    coord_y = boarders[cell[0]] + cell_size / 2
    return coord_x, coord_y


def create_sum_group(cell_cages: list) -> list:
    """
    convert the _cell_cages list to sum groups list

    :param cell_cages: all cell cages information
    :return: list containing all sum groups
    """
    sum_grps = []
    unique_grps = set([cell_cages[i][j]['group'] for i in range(9) for j in range(9)])
    for grp in unique_grps:
        if grp == -1:
            continue
        unique_sum = set([cell_cages[i][j]['sum']
                          for i in range(9)
                          for j in range(9)
                          if cell_cages[i][j]['group'] == grp and 'sum' in cell_cages[i][j]])
        if len(unique_sum) != 1:
            return []
        sum_coords = [(i, j)
                      for i in range(9)
                      for j in range(9)
                      if cell_cages[i][j]['group'] == grp]
        sum_grps.append({'coords': sum_coords, 'sum': list(unique_sum)[0]})
    return sum_grps
