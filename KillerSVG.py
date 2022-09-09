import io

import cairo  # https://pycairo.readthedocs.io/


def get_points_pos(group: list, cell: (int, int)) -> list:
    """
    from a list of cell indexes find out which corner
    of the cell will have a point (corner) in the sum group.

    :param group: list of cell indexes of a group
    :param cell: current cell index need to process
    :return: list of point positions of this cell
    (tl: top left, tr: top right, bl: bottom left, br: bottom right)
    """
    result = []
    cell_row = cell[0]
    cell_col = cell[1]
    cell_tl = (cell_row - 1, cell_col - 1) in group
    cell_tc = (cell_row - 1, cell_col) in group
    cell_tr = (cell_row - 1, cell_col + 1) in group
    cell_cl = (cell_row, cell_col - 1) in group
    cell_cr = (cell_row, cell_col + 1) in group
    cell_bl = (cell_row + 1, cell_col - 1) in group
    cell_bc = (cell_row + 1, cell_col) in group
    cell_br = (cell_row + 1, cell_col + 1) in group
    if all([cell_tc, cell_cl]) and not cell_tl:
        result.append('tl')
    elif not any([cell_tl, cell_tc, cell_cl]):
        result.append('tl')
    if all([cell_tc, cell_cr]) and not cell_tr:
        result.append('tr')
    elif not any([cell_tc, cell_tr, cell_cr]):
        result.append('tr')
    if all([cell_cl, cell_bc]) and not cell_bl:
        result.append('bl')
    elif not any([cell_cl, cell_bl, cell_bc]):
        result.append('bl')
    if all([cell_cr, cell_bc]) and not cell_br:
        result.append('br')
    elif not any([cell_cr, cell_bc, cell_br]):
        result.append('br')
    return result


def get_points_order(drawing_pts: list) -> list:
    """
    sort all drawing points in order.

    :param drawing_pts: list containing all information of the drawing points (of a sum group)
    :return: list of all drawing points in the order
    """
    drawing_order = []

    # first_pts_x = drawing_pts[0]['x']
    # first_pts_y = drawing_pts[0]['y']
    cur_pts_x = drawing_pts[0]['x']
    cur_pts_y = drawing_pts[0]['y']

    drawing_pts = drawing_pts[1:]
    cur_dir_x = True  # draw to which direction
    drawing_order.append((cur_pts_x, cur_pts_y))

    while len(drawing_pts) != 0:
        pts_on_axis = []
        num_dup_dir = {False: 0, True: 0}
        for pt in drawing_pts:
            # draw on y axis
            if cur_dir_x and pt['x'] == cur_pts_x:
                pt_on_axis = pt
                pt_diff = pt_on_axis['y'] - cur_pts_y
                # calculate the direction and distance
                pt_on_axis['direction'] = pt_diff > 0
                pt_on_axis['diff'] = abs(pt_diff)
                num_dup_dir[pt_on_axis['direction']] += 1
                pts_on_axis.append(pt_on_axis)
            # draw on x axis
            elif not cur_dir_x and pt['y'] == cur_pts_y:
                pt_on_axis = pt
                pt_diff = pt_on_axis['x'] - cur_pts_x
                # calculate the direction and distance
                pt_on_axis['direction'] = pt_diff > 0
                pt_on_axis['diff'] = abs(pt_diff)
                num_dup_dir[pt_on_axis['direction']] += 1
                pts_on_axis.append(pt_on_axis)
        if not pts_on_axis:
            return drawing_order + get_points_order(drawing_pts)

        # count the number of pts in each dir
        if num_dup_dir[False] % 2 != 0:
            direction = False
        elif num_dup_dir[True] % 2 != 0:
            direction = True
        else:
            direction = None

        # go to odd direction
        if direction is not None:
            pts_on_axis = [pt for pt in pts_on_axis if pt['direction'] == direction]

        pts_diff = [pt['diff'] for pt in pts_on_axis]
        pt_drop = pts_diff.index(min(pts_diff))
        # select the pt need to be draw next
        select_pt = pts_on_axis[pt_drop]

        # go to current pt
        cur_pts_x, cur_pts_y = select_pt['x'], select_pt['y']
        drawing_order.append((cur_pts_x, cur_pts_y))

        # delete the current pt in df
        drawing_pts.remove(select_pt)
        # change the current direction
        cur_dir_x = not cur_dir_x

    return drawing_order


class KillerSVG:
    _svg_surface = None
    _context = None

    def __init__(self, _grid_parameters: dict):
        """
        initializing all drawing parameters

        :param _grid_parameters: dict of drawing parameters
        """
        self._gp = _grid_parameters

    def draw_grid(self):
        """
        Draw the sudoku 9x9 grid on the surface
        """
        _grid_tl = self._gp['boarders'][0] - self._gp['main_width'] / 2
        _grid_size = self._gp['cell_size'] * 9 + self._gp['main_width'] * 3 + self._gp['inside_width'] * 6

        self._context.set_source_rgb(0, 0, 0)

        self._context.set_line_width(self._gp['main_width'])
        self._context.rectangle(_grid_tl, _grid_tl, _grid_size, _grid_size)
        self._context.stroke()
        _grid_start = _grid_tl
        _grid_end = _grid_tl + _grid_size
        # cur_position = _grid_tl + _main_width / 2

        for i in range(8):
            if i in (2, 5):
                cur_position = self._gp['boarders'][i + 1] - self._gp['main_width'] / 2
                self._context.set_line_width(self._gp['main_width'])
                self._context.move_to(cur_position, _grid_start)
                self._context.line_to(cur_position, _grid_end)
                self._context.move_to(_grid_start, cur_position)
                self._context.line_to(_grid_end, cur_position)
                self._context.stroke()
            else:
                cur_position = self._gp['boarders'][i + 1] - self._gp['inside_width'] / 2
                self._context.set_line_width(self._gp['inside_width'])
                self._context.move_to(cur_position, _grid_start)
                self._context.line_to(cur_position, _grid_end)
                self._context.move_to(_grid_start, cur_position)
                self._context.line_to(_grid_end, cur_position)
                self._context.stroke()

    def draw_labels(self):
        """
        draw the grid labels (if needed)
        """
        self._context.select_font_face("sans-serif")
        self._context.set_font_size(self._gp['grid_label_font'])
        for i in range(9):
            _grid_label_tl_s = self._gp['white_boarder_width']
            _grid_label_tl_l = self._gp['boarders'][i]
            self._context.set_source_rgb(0.8, 0.8, 0.8)
            self._context.rectangle(_grid_label_tl_s,
                                    _grid_label_tl_l,
                                    self._gp['grid_label_width'],
                                    self._gp['cell_size'])
            self._context.fill()
            self._context.rectangle(_grid_label_tl_l,
                                    _grid_label_tl_s,
                                    self._gp['cell_size'],
                                    self._gp['grid_label_width'])
            self._context.fill()

            self._context.set_source_rgb(0, 0, 0)
            _text_l = chr(65 + i)
            _textex = self._context.text_extents(_text_l)
            self._context.move_to(_grid_label_tl_s + self._gp['grid_label_width'] / 2 - _textex[0] - _textex[2] / 2,
                                  _grid_label_tl_l + self._gp['cell_size'] / 2 - _textex[1] - _textex[3] / 2)
            self._context.show_text(_text_l)
            _text_u = str(i + 1)
            _textex = self._context.text_extents(_text_u)
            self._context.move_to(_grid_label_tl_l + self._gp['cell_size'] / 2 - _textex[0] - _textex[2] / 2,
                                  _grid_label_tl_s + self._gp['grid_label_width'] / 2 - _textex[1] - _textex[3] / 2)
            self._context.show_text(_text_u)

    def get_grid_point(self, _cell: (int, int), _point_pos: str) -> (float, float):
        """
        calculates the coordinates on the surface by the cell index and the position of the point

        :param _cell: the current cell index
        :param _point_pos: the point position in the cell
        :return: the drawing coordinates (regarding the surface)
        """
        # _cell_pos[0] is row = y, [1] is col = x
        if _point_pos == 'tl':
            _tl_x = (self._gp['boarders'][_cell[1]] +
                     self._gp['inside_box_boarder'] + self._gp['inside_width'] / 2)
            _tl_y = (self._gp['boarders'][_cell[0]] +
                     self._gp['inside_box_boarder'] + self._gp['inside_width'] / 2)
            return _tl_x, _tl_y
        elif _point_pos == 'tr':
            _tr_x = (self._gp['boarders'][_cell[1]] + self._gp['cell_size'] -
                     self._gp['inside_box_boarder'] - self._gp['inside_width'] / 2)
            _tr_y = (self._gp['boarders'][_cell[0]] +
                     self._gp['inside_box_boarder'] + self._gp['inside_width'] / 2)
            return _tr_x, _tr_y
        elif _point_pos == 'bl':
            _bl_x = (self._gp['boarders'][_cell[1]] +
                     self._gp['inside_box_boarder'] + self._gp['inside_width'] / 2)
            _bl_y = (self._gp['boarders'][_cell[0]] + self._gp['cell_size'] -
                     self._gp['inside_box_boarder'] - self._gp['inside_width'] / 2)
            return _bl_x, _bl_y
        elif _point_pos == 'br':
            _br_x = (self._gp['boarders'][_cell[1]] + self._gp['cell_size'] -
                     self._gp['inside_box_boarder'] - self._gp['inside_width'] / 2)
            _br_y = (self._gp['boarders'][_cell[0]] + self._gp['cell_size'] -
                     self._gp['inside_box_boarder'] - self._gp['inside_width'] / 2)
            return _br_x, _br_y

    def get_drawing_points(self, _group: list) -> list:
        """
        Produce a DataFrame of all drawing points (without order)

        :param _group: list of cell indexes in a sum group
        :return: json list containing all drawing points info in a sum group
        # :return: DataFrame containing all drawing coordinates and their cells and the point positions
        """
        _drawing_pts = []
        for i in range(0, len(_group)):
            _cur_cell = _group[i]
            _cur_points = get_points_pos(_group, _cur_cell)
            for pts in _cur_points:
                _pt_x, _pt_y = self.get_grid_point(_cur_cell, pts)
                _drawing_pts.append({'cell': _cur_cell,
                                     'pos': pts,
                                     'x': _pt_x,
                                     'y': _pt_y})
        return _drawing_pts

    def draw_sum_group(self, _sum_group: dict):
        """
        Draw a sum group on the surface

        :param _sum_group: json dict containing the group and sum of a sum group
        """
        self._context.set_line_width(self._gp['inside_width'])
        self._context.set_dash([self._gp['inside_width'] * 4, self._gp['inside_width'] * 2])
        self._context.set_source_rgb(0, 0, 0)

        # find all pts needed to be connected
        _drawing_pts = self.get_drawing_points(_sum_group['coords'])

        _drawing_ordered = get_points_order(_drawing_pts)

        _first_pt = _drawing_ordered[0]

        # draw the line by the ordered points
        self._context.move_to(_first_pt[0], _first_pt[1])
        _prev_pt = _first_pt
        for pt in _drawing_ordered[1:]:
            if pt[0] == _prev_pt[0] or pt[1] == _prev_pt[1]:
                self._context.line_to(pt[0], pt[1])
            else:
                # if the group containing two separate contours
                self._context.line_to(_first_pt[0], _first_pt[1])
                self._context.move_to(pt[0], pt[1])
                _first_pt = pt
            _prev_pt = pt

        # draw the last line back to the first pt
        self._context.line_to(_first_pt[0], _first_pt[1])
        self._context.stroke()

        # write sum (all the steps below)
        self._context.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self._context.set_font_size(self._gp['group_font'])
        _textex = self._context.text_extents(str(_sum_group['sum']))

        # draw a white background
        self._context.set_source_rgb(1, 1, 1)
        _first_cell = _sum_group['coords'][0]
        _first_cell_x = self._gp['boarders'][_first_cell[1]]  # col
        _first_cell_y = self._gp['boarders'][_first_cell[0]]  # row
        self._context.rectangle(_first_cell_x + self._gp['text_boarder'],
                                _first_cell_y + self._gp['text_boarder'],
                                _textex[2] + self._gp['text_boarder'],
                                _textex[3] + self._gp['text_boarder'])
        self._context.fill()

        # write the number
        self._context.set_source_rgb(0, 0, 0)
        self._context.move_to(_first_cell_x + self._gp['text_boarder'] - _textex[0],
                              _first_cell_y + self._gp['text_boarder'] - _textex[1])
        self._context.show_text(str(_sum_group['sum']))

    def draw_known_number(self, _known_number: dict):
        """
        draw all the possible numbers (small numbers) or large number (only one)
        of a given cell on the surface

        :param _known_number: json dictionary containing the details of numbers in a cell
        """
        self._context.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self._context.set_source_rgb(0, 0, 0)

        _cur_cell_x = self._gp['boarders'][_known_number['coord'][1]]
        _cur_cell_y = self._gp['boarders'][_known_number['coord'][0]]

        if not _known_number['small']:
            _cur_nbr = _known_number['possible_numbers'][0]
            self._context.set_font_size(self._gp['cell_big_font'])
            _textex = self._context.text_extents(str(_cur_nbr))
            self._context.move_to(_cur_cell_x + self._gp['cell_size'] / 2 - _textex[0] - _textex[2] / 2,
                                  _cur_cell_y + self._gp['cell_size'] / 2 - _textex[1] - _textex[3] / 2)
            self._context.show_text(str(_cur_nbr))
        else:
            self._context.set_font_size(self._gp['cell_small_font'])
            for _cur_nbr in _known_number['possible_numbers']:
                _nbr_row = (_cur_nbr - 1) // 3
                _nbr_col = (_cur_nbr - 1) % 3
                _textex = self._context.text_extents(str(_cur_nbr))
                # large to small boarder
                self._context.move_to(_cur_cell_x + self._gp['lts_boarder'] +
                                      _nbr_col * self._gp['small_cell_size'] +
                                      self._gp['small_cell_size'] / 2 - _textex[0] - _textex[2] / 2,
                                      _cur_cell_y + self._gp['lts_boarder'] +
                                      _nbr_row * self._gp['small_cell_size'] +
                                      self._gp['small_cell_size'] / 2 - _textex[1] - _textex[3] / 2)
                self._context.show_text(str(_cur_nbr))

    def draw_context(self, _json_data: dict):
        """
        draw the killer sudoku grid on the surface

        :param _json_data: json dictionary containing sum groups and known numbers
        """
        self._context.scale(self._gp['scale'], self._gp['scale'])

        self.draw_grid()

        if self._gp['grid_label']:
            self.draw_labels()

        if 'sum_groups' in _json_data:
            for sum_group in _json_data['sum_groups']:
                self.draw_sum_group(sum_group)

        if 'known_numbers' in _json_data:
            for known_number in _json_data['known_numbers']:
                self.draw_known_number(known_number)

    # def draw_killer_svg(self, _json_data: dict, _filename: str = "example.svg"):
    #     """
    #     draw the killer sudoku grid on an SVG file surface
    #     _json_data example: {'sum_groups':[{'coords': [[a,b], [c,d], ...], 'sum': 999}, ...],
    #                          'known_numbers':[{'coord': [a,b], 'small': , 'possible_numbers': [1, 2, ...]}, ...]}
    #
    #     :param _json_data: json dictionary containing sum groups and known numbers
    #     :param _filename: filename of the output svg
    #     """
    #     with cairo.SVGSurface(_filename, self._gp['size'], self._gp['size']) as surface:
    #         self._context = cairo.Context(surface)
    #         self.draw_context(_json_data)

    # def draw_svg_bs(self, _json_data: dict):
    #     with io.BytesIO() as svg_bsio:
    #         with cairo.SVGSurface(svg_bsio, self._gp['size'], self._gp['size']) as surface:
    #             self._context = cairo.Context(surface)
    #             self.draw_context(_json_data)
    #         svg_bsio.seek(0)
    #         svg_bs = svg_bsio.read()
    #
    #     return svg_bs

    def draw(self, _json_data: dict, flag_img=False, img_size=None):
        svg_bs, img_bs = None, None
        with io.BytesIO() as svg_bsio:
            with cairo.SVGSurface(svg_bsio, self._gp['size'], self._gp['size']) as svg_surface:
                self._context = cairo.Context(svg_surface)
                self.draw_context(_json_data)

            svg_bsio.seek(0)
            svg_bs = svg_bsio.read()

        if flag_img:
            if img_size is None:
                img_size = self._gp['size']
            img_scale = img_size / self._gp['size']

            with io.BytesIO() as img_bsio:
                with cairo.ImageSurface(cairo.FORMAT_ARGB32, img_size, img_size) as img_surface:
                    self._context = cairo.Context(img_surface)
                    self._context.scale(img_scale, img_scale)
                    self.draw_context(_json_data)
                    img_surface.write_to_png(img_bsio)
                img_bsio.seek(0)
                img_bs = img_bsio.read()

        return svg_bs, img_bs
