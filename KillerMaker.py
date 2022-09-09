from GridHelper import *
from KillerFiles import *
from KillerDown import challenge_window_json


class KillerMaker:
    _json_data = {'sum_groups': [], 'known_numbers': []}
    _cell_cages = [[{'group': -1,
                     'sum': 0}
                    for _ in range(9)]
                   for _ in range(9)]

    _dragging = False
    _grp_idx = 0
    _grp = []

    _cur_pt = (-1, -1)

    _sum_mode = False
    _cur_idx = (-1, -1)
    _cur_selection_circle = None

    _delete_mode = False

    _text_dict = {}
    _conn_list = []

    _open_mode = False

    # Window Elements
    _graph = None
    _text = None

    def __init__(self, _configs: dict):
        """
        initializing the layout and element for the sudoku designer

        :param _configs: dict of configs
        """
        self._configs = _configs
        self._grid_parameters = calc_size(_configs["grid_parameters"])

        self._graph_size = _configs["graph_size"]

        self._graph_scale = self._graph_size / self._grid_parameters['size']
        self._graph_cell_size = self._grid_parameters['cell_size'] * self._graph_scale
        self._graph_boarders = [i * self._graph_scale for i in self._grid_parameters['boarders']]

        self.layout = [[sg.Column([[sg.Graph((self._graph_size, int(self._graph_size * 0.04)),
                                             (0, int(self._graph_size * 0.04)),
                                             (self._graph_size, 0),
                                             key='_Design_Title_', visible=False)],
                                   [sg.Graph((self._graph_size, self._graph_size),
                                             (0, self._graph_size),
                                             (self._graph_size, 0),
                                             # background_color='white',
                                             drag_submits=True,
                                             enable_events=True,
                                             key='_Designer_')]]),
                        sg.Column([[sg.Input(size=(5, None), disabled=True, enable_events=True, key='_Design_Text_')],
                                   [sg.Checkbox(self._configs["lang_dict"]["_Design_Sum_"], enable_events=True, key='_Design_Sum_')],
                                   [sg.Checkbox(self._configs["lang_dict"]["_Design_Delete_"], enable_events=True, key='_Design_Delete_')],
                                   [sg.Button(self._configs["lang_dict"]["_Design_Reset_"], key='_Design_Reset_')],
                                   [sg.Button(self._configs["lang_dict"]["_Design_Save_"], key='_Design_Save_')],
                                   [sg.Button(self._configs["lang_dict"]["_Design_Draw_"], key='_Design_Draw_')],
                                   [sg.Button(self._configs["lang_dict"]["_Design_Open_"], key='_Design_Open_')],
                                   [sg.Button(self._configs["lang_dict"]["_Design_Challenge_"], key='_Design_Challenge_')],
                                   [sg.Button(self._configs["lang_dict"]["_Design_Solve_"], disabled=True, key='_Design_Solve_')]],
                                  element_justification='center')
                        ]]

    def reset_all(self):
        """
        reset all fields for the sudoku designer
        """
        self._graph.erase()

        ksvg = KillerSVG(self._grid_parameters)
        svg_bs, img_bs = ksvg.draw(dict(), True, self._graph_size)

        self._graph.draw_image(data=img_bs, location=(0, 0))

        # if self._grid_parameters['grid_label']:
        #     _grid_svg = "./grid.svg"
        # else:
        #     _grid_svg = "./grid_F.svg"
        #
        # _bs = cairosvg.svg2png(url=_grid_svg,
        #                        dpi=72,
        #                        scale=self._graph_scale)
        # self._graph.draw_image(data=_bs, location=(0, 0))

        self._json_data = {'sum_groups': [], 'known_numbers': []}

        self._cell_cages = [[{'group': -1,
                              'sum': 0}
                             for _ in range(9)]
                            for _ in range(9)]

        self._dragging = False
        self._grp_idx = 0
        self._grp = []

        self._cur_pt = (-1, -1)

        self._sum_mode = False
        self._cur_idx = (-1, -1)
        self._cur_selection_circle = None

        self._delete_mode = False

        self._text_dict = {}
        self._conn_list = []

        self._open_mode = False

    def drag_to_grp(self):
        """
        drag the mouse to create a group
        """
        _old_grp_idx = self._grp_idx
        for coord in self._grp:
            if len(self._grp) > 1:
                _coord_grp = self._cell_cages[coord[0]][coord[1]]['group']
                if _coord_grp != -1:
                    _coords_in_grp = [(i, j)
                                      for i in range(9)
                                      for j in range(9)
                                      if self._cell_cages[i][j]['group'] == _coord_grp]
                    for _coord_in_grp in _coords_in_grp:
                        self._cell_cages[_coord_in_grp[0]][_coord_in_grp[1]]['group'] = self._grp_idx
                        self._cell_cages[_coord_in_grp[0]][_coord_in_grp[1]]['sum'] = 0
            self._cell_cages[coord[0]][coord[1]]['group'] = self._grp_idx
            self._cell_cages[coord[0]][coord[1]]['sum'] = 0
        if _old_grp_idx == self._grp_idx:
            self._grp_idx += 1
        self._grp = []

    def input_sum(self, _selected_cell: (int, int), _sum: int) -> int:
        """
        put the input sum into the _cell_cages sum field
        for all the cell in the selected group

        :param _selected_cell: the cell index for the selected cell
        :param _sum: the sum the user input
        :return: The group index for the selected cell
        """
        _selected_grp = self._cell_cages[_selected_cell[0]][_selected_cell[1]]['group']
        if _selected_grp == -1:
            return _selected_grp
        _coords_in_grp = [(i, j)
                          for i in range(9)
                          for j in range(9)
                          if self._cell_cages[i][j]['group'] == _selected_grp]
        for _coord_in_grp in _coords_in_grp:
            self._cell_cages[_coord_in_grp[0]][_coord_in_grp[1]]['sum'] = _sum
        return _selected_grp

    def sum_mode_text_update(self, _input: str):
        """
        update the input sum in the graph and the DataFrame for the sum mode

        :param _input: the input string (for the sum)
        """
        if self._cur_idx == (-1, -1):
            return
        try:
            if _input == '':
                _input_int = 0
            else:
                _input_int = int(_input)
        except ValueError:
            print('input wrong')
            return
        _sum_grp = self.input_sum(self._cur_idx, _input_int)
        if _sum_grp != -1:
            _sum_pt = (self._graph_boarders[self._cur_idx[1]],
                       self._graph_boarders[self._cur_idx[0]])
            if str(_sum_grp) in self._text_dict:
                self._graph.delete_figure(self._text_dict[str(_sum_grp)])
            self._text_dict[str(_sum_grp)] = self._graph.draw_text(_input,
                                                                   _sum_pt,
                                                                   color='red',
                                                                   font=('sans-serif', 16),
                                                                   text_location=sg.TEXT_LOCATION_TOP_LEFT)

    def sum_mode_mouse_up(self):
        """
        update the selected circle and the input field
        (change to current selected cell's sum)
        when the user click on one cell

        :return: None
        """
        if self._cur_idx == (-1, -1):
            return

        self._graph.delete_figure(self._cur_selection_circle)
        _pt_coord = calc_center_coord(self._cur_idx, self._graph_boarders, self._graph_cell_size)
        self._cur_selection_circle = self._graph.draw_circle(_pt_coord,
                                                             self._graph_cell_size / 2,
                                                             fill_color='#ffcccc',
                                                             line_width=0)
        self._graph.send_figure_to_back(self._cur_selection_circle)

        if self._cell_cages[self._cur_idx[0]][self._cur_idx[1]]['group'] == -1:
            self._text.update(value='')
        else:
            _cur_selection_sum = self._cell_cages[self._cur_idx[0]][self._cur_idx[1]]['sum']
            if _cur_selection_sum == 0:
                self._text.update(value='')
            else:
                self._text.update(value=str(_cur_selection_sum))

    def delete_mode_mouse_up(self):
        """
        delete the selected group while click on the corresponding cell

        :return: None
        """
        if self._cur_idx == (-1, -1):
            return
        _selected_grp = self._cell_cages[self._cur_idx[0]][self._cur_idx[1]]['group']
        _cur_del_pt_idx = [(i, j)
                           for i in range(9)
                           for j in range(9)
                           if self._cell_cages[i][j]['group'] == _selected_grp]
        _cur_del_conn = [_conn for _conn in self._conn_list
                         if _conn['start_pt'] in _cur_del_pt_idx
                         or _conn['end_pt'] in _cur_del_pt_idx]

        for _conn in _cur_del_conn:
            _cur_del_key = _conn['key']
            self._graph.delete_figure(_cur_del_key)
            self._conn_list.remove(_conn)

        for _pt in _cur_del_pt_idx:
            self._cell_cages[_pt[0]][_pt[1]] = {'group': -1,
                                                'sum': 0}

    def init_window(self):
        """
        Initialize the GUI window for the Killer Maker
        """
        window = sg.Window('Designer', self.layout)
        window.Finalize()

        _title = window.Element('_Design_Title_')
        self._graph = window.Element('_Designer_')
        _sum_check = window.Element('_Design_Sum_')
        _delete_check = window.Element('_Design_Delete_')
        _draw_button = window.Element('_Design_Draw_')
        _solve_button = window.Element('_Design_Solve_')
        self._text = window.Element('_Design_Text_')

        # if self._grid_parameters['grid_label']:
        #     _grid_svg = "./grid.svg"
        # else:
        #     _grid_svg = "./grid_F.svg"

        # _bs = cairosvg.svg2png(url=_grid_svg,
        #                        dpi=72,
        #                        scale=self._graph_scale)
        # self._graph.draw_image(data=_bs, location=(0, 0))

        ksvg = KillerSVG(self._grid_parameters)
        svg_bs, img_bs = ksvg.draw(dict(), True, self._graph_size)

        self._graph.draw_image(data=img_bs, location=(0, 0))

        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                break

            elif event == '_Designer_':
                if self._sum_mode or self._delete_mode:
                    continue
                if not self._dragging:
                    self._dragging = True
                x, y = values["_Designer_"]
                _next_idx = select_idx(x, y, self._graph_boarders)

                if _next_idx not in self._grp and _next_idx != (-1, -1):
                    self._grp.append(_next_idx)
                    _next_pt = calc_center_coord(_next_idx, self._graph_boarders, self._graph_cell_size)
                    self._conn_list.append({'start_pt': _next_idx,
                                            'end_pt': _next_idx,
                                            'key': self._graph.draw_point(_next_pt)})
                    if self._cur_pt != (-1, -1):
                        self._conn_list.append({'start_pt': self._cur_idx,
                                                'end_pt': _next_idx,
                                                'key': self._graph.draw_line(self._cur_pt, _next_pt)})
                    self._cur_idx = _next_idx
                    self._cur_pt = _next_pt

            elif event == '_Designer_+UP':  # MOUSE_UP + DRAG FINISHED
                if self._sum_mode:
                    x, y = values["_Designer_"]
                    self._cur_idx = select_idx(x, y, self._graph_boarders)
                    self.sum_mode_mouse_up()

                elif self._delete_mode:
                    x, y = values["_Designer_"]
                    self._cur_idx = select_idx(x, y, self._graph_boarders)
                    self.delete_mode_mouse_up()

                else:
                    if not self._dragging:
                        continue
                    self.drag_to_grp()
                    self._dragging = False
                    self._cur_pt = (-1, -1)

            elif event == '_Design_Text_':
                self.sum_mode_text_update(values["_Design_Text_"])

            elif event == '_Design_Sum_':
                self._sum_mode = values["_Design_Sum_"]
                self._text.update(value='', disabled=(not self._sum_mode))
                self._cur_idx = (-1, -1)
                self._cur_pt = (-1, -1)
                self._graph.delete_figure(self._cur_selection_circle)
                self._cur_selection_circle = None

            elif event == '_Design_Delete_':
                self._delete_mode = values["_Design_Delete_"]
                self._cur_idx = (-1, -1)
                self._cur_pt = (-1, -1)

            elif event == '_Design_Reset_':
                self.reset_all()

                _title.hide_row()
                _sum_check.update(disabled=True)
                _draw_button.update(disabled=True)
                _solve_button.update(disabled=False)
                self._text.update(value='', disabled=True)

            elif event == '_Design_Save_':
                # create _json_data for the outputs
                if not self._open_mode:
                    self._json_data['sum_groups'] = create_sum_group(self._cell_cages)
                    self._json_data['known_numbers'] = []

                save_dialog(self._configs, self._json_data)

            elif event == '_Design_Draw_':
                if not self._open_mode:
                    self._json_data['sum_groups'] = create_sum_group(self._cell_cages)
                    self._json_data['known_numbers'] = []
                try:
                    draw_file(self._grid_parameters, self._json_data, self._graph_size, self._graph, _title)
                    _sum_check.update(value=False)
                    # _sum_check.update(disabled=True)
                    _solve_button.update(disabled=False)
                    # _text.update(value='', disabled=True)
                    self._sum_mode = False
                except ValueError:
                    sg.popup_error()

            elif event == '_Design_Open_':
                _open_file = sg.popup_get_file('open ks json', file_types=(('Text File', '*.json'),))
                if _open_file is None:
                    continue
                try:
                    _status, self._json_data = open_ks_file(_open_file)
                    if _status:
                        draw_file(self._grid_parameters, self._json_data, self._graph_size, self._graph, _title)
                    else:
                        continue
                except ValueError:
                    sg.popup_error(self._configs["lang_dict"]["_Error_Data_"])
                    continue

                _sum_check.update(disabled=True)
                _draw_button.update(disabled=True)
                _solve_button.update(disabled=False)
                self._text.update(value='', disabled=True)
                self._open_mode = True
                self._sum_mode = False

            elif event == '_Design_Challenge_':
                _json_data = challenge_window_json(self._configs)
                if not _json_data:
                    continue
                self._json_data = _json_data
                draw_file(self._grid_parameters, self._json_data, self._graph_size, self._graph, _title)

                _sum_check.update(disabled=True)
                _draw_button.update(disabled=True)
                _solve_button.update(disabled=False)
                self._text.update(value='', disabled=True)
                self._open_mode = True
                self._sum_mode = False
                # challenge_window_image(self._graph, _title, self._graph_size)

            elif event == '_Design_Solve_':  # go to solver
                from KillerPlayer import KillerPlayer

                window.close()
                kp = KillerPlayer(self._configs, self._json_data)
                kp.init_window()

        window.close()
