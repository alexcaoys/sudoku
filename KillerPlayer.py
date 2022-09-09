from GridHelper import *
from KillerFiles import *
from KillerDown import challenge_window_json
from SudokuSolve import sudoku_solve


class KillerPlayer:
    _timer_start = False

    _json_data = None

    _cur_pt_center = None
    _cur_selection_circle = None
    _cur_idx = (-1, -1)

    _small_nbr = False
    _text_matrix = [[{'small': None,
                      'possible_numbers': [],
                      'key': None}
                     for _ in range(9)]
                    for _ in range(9)]

    _input_mode = False
    _comment_matrix = [[{'comment': None,
                         'key': None}
                        for _ in range(9)]
                       for _ in range(9)]

    # Window Elements
    _graph = None
    _title = None
    _timer = None

    def __init__(self, _configs: dict, _json_data = None):
        """
        Initializing the layout and element for the sudoku player.
        Can use existing _json_data to initializing

        :param _configs: dict of configs
        :param _json_data: json dictionary containing sum groups and known numbers
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
                                             key='_Play_Title_', visible=False)],
                                   [sg.Graph((self._graph_size, self._graph_size),
                                             (0, self._graph_size),
                                             (self._graph_size, 0),
                                             background_color='white',
                                             enable_events=True,
                                             key='_Player_')]]),
                        sg.Column([[sg.Button(str(i),
                                              size=(4, 2),
                                              key='_Play_' + str(i) + '_') for i in range(1, 4)],
                                   [sg.Button(str(i),
                                              size=(4, 2),
                                              key='_Play_' + str(i) + '_') for i in range(4, 7)],
                                   [sg.Button(str(i),
                                              size=(4, 2),
                                              key='_Play_' + str(i) + '_') for i in range(7, 10)],
                                   [sg.Text('00:00:00', key='_Play_Timer_')],
                                   [sg.Checkbox(self._configs["lang_dict"]["_Play_Small_"], enable_events=True, key='_Play_Small_')],
                                   [sg.Checkbox(self._configs["lang_dict"]["_Play_Comment_"], enable_events=True, key='_Play_Comment_')],
                                   [sg.Input(size=(8, None),
                                             disabled=True,
                                             enable_events=True,
                                             key='_Play_Input_')],
                                   [sg.Button(self._configs["lang_dict"]["_Play_Clear_"], key='_Play_Clear_')],
                                   [sg.Button(self._configs["lang_dict"]["_Play_Open_"], key='_Play_Open_')],
                                   [sg.Button(self._configs["lang_dict"]["_Play_Challenge_"], key='_Play_Challenge_')],
                                   [sg.Button(self._configs["lang_dict"]["_Play_Save_"], key='_Play_Save_')],
                                   [sg.Button(self._configs["lang_dict"]["_Play_Solve_"], key='_Play_Solve_')],
                                   [sg.Button(self._configs["lang_dict"]["_Play_Design_"], key='_Play_Design_')]
                                   ], element_justification='center')
                        ]]

        self._button_keys = {}
        for i in range(1, 10):
            self._button_keys['_Play_' + str(i) + '_'] = i

        self._keypress_lst = list(map(str, range(1, 10)))

        if _json_data is not None:
            self._json_data = _json_data

    def clear_player(self):
        """
        reset the graph to the default one
        """
        # if self._grid_parameters['grid_label']:
        #     _grid_svg = "./grid.svg"
        # else:
        #     _grid_svg = "./grid_F.svg"
        #
        # _bs = cairosvg.svg2png(url=_grid_svg,
        #                        dpi=72,
        #                        scale=self._graph_scale)

        ksvg = KillerSVG(self._grid_parameters)
        svg_bs, img_bs = ksvg.draw(dict(), True, self._graph_size)

        self._graph.draw_image(data=img_bs, location=(0, 0))

    def reset_all(self):
        """
        reset all fields for the sudoku player
        """
        self._graph.delete_figure(self._cur_selection_circle)
        self._cur_pt_center = None
        self._cur_selection_circle = None
        self._cur_idx = (-1, -1)

        for i in range(9):
            for j in range(9):
                if self._text_matrix[i][j]['key'] is not None:
                    self._graph.delete_figure(self._text_matrix[i][j]['key'])
                self._text_matrix[i][j] = {'small': None,
                                           'possible_numbers': [],
                                           'key': None}
                if self._comment_matrix[i][j]['key'] is not None:
                    self._graph.delete_figure(self._comment_matrix[i][j]['key'])
                self._comment_matrix[i][j] = {'comment': None,
                                              'key': None}

        self._timer_start = False
        self._timer.update("00:00:00")

    def write_comment(self, _comment: str):
        """
        write the comment on the top of the cell (_cur_idx)

        :param _comment: the comment need to write in the cell
        :return: None
        """
        if self._cur_idx == (-1, -1):
            return
        _comment_pt = (self._cur_pt_center[0],
                       self._cur_pt_center[1] - self._graph_cell_size * 0.3)
        selected_idx = self._comment_matrix[self._cur_idx[0]][self._cur_idx[1]]
        if selected_idx['key'] is not None:
            self._graph.delete_figure(selected_idx['key'])
        if _comment == '':
            self._comment_matrix[self._cur_idx[0]][self._cur_idx[1]] = {'comment': None,
                                                                        'key': None}
        else:
            _new_key = self._graph.draw_text(_comment,
                                             _comment_pt,
                                             font=('sans-serif', 8),
                                             text_location=sg.TEXT_LOCATION_CENTER)
            self._comment_matrix[self._cur_idx[0]][self._cur_idx[1]] = {'comment': _comment,
                                                                        'key': _new_key}

    def write_nbr(self, _selected_nbr: int, _cur_small_mode: bool):
        """
        Write the selected numbers on the graph, maybe large or small
        (depends on the _cur_small_mode)

        :param _selected_nbr: The number selected to be written in the cell
        :param _cur_small_mode: The current small/large mode for the written numbers
        :return: None
        """
        if self._cur_idx == (-1, -1):  # if no selected cell
            return
        if not self._timer_start:  # start the timer if not
            self._timer_start = time.time()

        _exists_small = self._text_matrix[self._cur_idx[0]][self._cur_idx[1]]['small']

        if _cur_small_mode:  # if in small number mode
            _cur_nbrs = []
            if _exists_small is not None and _exists_small:  # if the current cell has other small numbers
                # _cur_df_idx = _exists_small.index
                # record the old numbers, delete the old text
                _cur_nbrs = self._text_matrix[self._cur_idx[0]][self._cur_idx[1]]['possible_numbers']
                _cur_key = self._text_matrix[self._cur_idx[0]][self._cur_idx[1]]['key']
                self._graph.delete_figure(_cur_key)
                self._text_matrix[self._cur_idx[0]][self._cur_idx[1]] = {'small': None,
                                                                         'possible_numbers': [],
                                                                         'key': None}
            if _selected_nbr in _cur_nbrs:
                # if the selected number is already in the list, delete it
                _cur_nbrs.remove(_selected_nbr)
            else:
                # otherwise, write the new small number in the cell
                _cur_nbrs.append(_selected_nbr)
                _cur_nbrs.sort()
            _small_nbrs_pos = (self._cur_pt_center[0] - self._graph_cell_size * 0.4,
                               self._cur_pt_center[1] + self._graph_cell_size * 0.3)
            # write all small numbers in the cell
            _nbrs_str = ''.join(map(str, _cur_nbrs))
            self._text_matrix[self._cur_idx[0]][self._cur_idx[1]] = {'small': True,
                                                                     'possible_numbers': _cur_nbrs,
                                                                     'key': self._graph.draw_text(
                                                                         _nbrs_str,
                                                                         _small_nbrs_pos,
                                                                         font=('sans-serif', 8),
                                                                         text_location=sg.TEXT_LOCATION_LEFT)}
        else:  # big number mode
            if _exists_small is not None and not _exists_small:  # if the current cell has big number
                # remove the old number from the df and the graph
                _cur_nbr = self._text_matrix[self._cur_idx[0]][self._cur_idx[1]]['possible_numbers'][0]
                _cur_key = self._text_matrix[self._cur_idx[0]][self._cur_idx[1]]['key']
                self._graph.delete_figure(_cur_key)
                self._text_matrix[self._cur_idx[0]][self._cur_idx[1]] = {'small': None,
                                                                         'possible_numbers': [],
                                                                         'key': None}
                if _selected_nbr == _cur_nbr:
                    # if the old big number is the selected number
                    return
            # write the new big number in the cell
            self._text_matrix[self._cur_idx[0]][self._cur_idx[1]] = {'small': False,
                                                                     'possible_numbers': [_selected_nbr],
                                                                     'key': self._graph.draw_text(
                                                                         str(_selected_nbr),
                                                                         self._cur_pt_center,
                                                                         font=('sans-serif', 24),
                                                                         text_location=sg.TEXT_LOCATION_CENTER)}

    def open_from_file(self):
        """
        Open a file (or load progress) from a file

        :return: None
        """
        _open_window = sg.Window(self._configs["lang_dict"]["_Open_Title_"],
                                 [[sg.Text(self._configs["lang_dict"]["_Open_Filename_"]),
                                   sg.Input(key='_Open_Input_'),
                                   sg.FileBrowse(self._configs["lang_dict"]["_Open_Browse_"],
                                                 target='_Open_Input_',
                                                 file_types=(('Text File', '*.json'),))],
                                  [sg.Button(self._configs["lang_dict"]["_Open_Open_"], key='_Open_Open_'),
                                   sg.Button(self._configs["lang_dict"]["_Open_Load_"], key='_Open_Load_'),
                                   sg.Button(self._configs["lang_dict"]["_Open_Cancel_"], key='_Open_Cancel_')]],
                                 modal=True)
        event, values = _open_window.read()
        if event in (sg.WIN_CLOSED, '_Open_Cancel_'):
            _open_window.close()
            return
        else:
            if values['_Open_Input_'] == '':
                _open_window.close()
                return

            try:
                _status, self._json_data = open_ks_file(values['_Open_Input_'])
            except ValueError:
                sg.popup_error(self._configs["lang_dict"]["_Error_Data_"])
                return

            if event == '_Open_Open_':
                if _status:
                    draw_file(self._grid_parameters, self._json_data, self._graph_size, self._graph, self._title)
                    self.reset_all()

            elif event == '_Open_Load_':
                for _cell in self._json_data['known_numbers']:
                    self._cur_idx = _cell['coord']
                    self._cur_pt_center = calc_center_coord(self._cur_idx, self._graph_boarders, self._graph_cell_size)
                    if not _cell['small']:
                        self.write_nbr(_cell['possible_numbers'][0], False)
                    else:
                        for _nbr in _cell['possible_numbers']:
                            self.write_nbr(_nbr, True)

            _open_window.close()

    def init_window(self):
        """
        Initialize the GUI window for the Killer Player

        """
        window = sg.Window('Player',
                           self.layout,
                           return_keyboard_events=True)
        window.Finalize()

        self._title = window.Element('_Play_Title_')
        self._graph = window.Element('_Player_')
        self._timer = window.Element('_Play_Timer_')
        _input = window.Element('_Play_Input_')

        if self._json_data is not None:
            draw_file(self._grid_parameters, self._json_data, self._graph_size, self._graph, self._title)
        else:
            self.clear_player()

        while True:
            event, values = window.read(timeout=10)
            if self._timer_start:
                self._timer.update(time.strftime("%H:%M:%S",
                                                 time.gmtime(time.time() - self._timer_start)))

            if event in (sg.WIN_CLOSED, 'Exit'):
                break

            elif event == '_Player_':  # MOUSE_UP FINISHED
                self._graph.delete_figure(self._cur_selection_circle)

                x, y = values["_Player_"]
                self._cur_idx = select_idx(x, y, self._graph_boarders)
                self._cur_pt_center = calc_center_coord(self._cur_idx, self._graph_boarders, self._graph_cell_size)
                self._cur_selection_circle = self._graph.draw_circle(self._cur_pt_center,
                                                                     self._graph_cell_size / 2,
                                                                     fill_color='#ffcccc',
                                                                     line_width=0)
                self._graph.send_figure_to_back(self._cur_selection_circle)
                if self._comment_matrix[self._cur_idx[0]][self._cur_idx[1]]['key'] is not None:
                    _input.update(value=self._comment_matrix[self._cur_idx[0]][self._cur_idx[1]]['comment'])
                else:
                    _input.update(value='')

            elif event == '_Play_Input_':
                if self._input_mode:
                    self.write_comment(values['_Play_Input_'])

            elif event in self._button_keys.keys():  # press any number in _sel_window
                _select_nbr = self._button_keys[event]
                self.write_nbr(_select_nbr, self._small_nbr)

            elif event in self._keypress_lst:  # press number keys
                if not self._input_mode:
                    _select_nbr = int(event)
                    self.write_nbr(_select_nbr, self._small_nbr)

            elif event == '_Play_Small_':  # change to small mode
                self._small_nbr = values['_Play_Small_']

            elif event == '_Play_Comment_':  # change to comment mode
                self._input_mode = values['_Play_Comment_']
                _input.update(value='', disabled=(not self._input_mode))
                if self._comment_matrix[self._cur_idx[0]][self._cur_idx[1]]['key'] is not None:
                    _input.update(value=self._comment_matrix[self._cur_idx[0]][self._cur_idx[1]]['comment'])
                else:
                    _input.update(value='')

            elif event == 's':  # change to small mode by keypress
                if not self._input_mode:
                    _cur_sn = self._small_nbr
                    window['_Play_Small_'].update(value=(not _cur_sn))
                    self._small_nbr = not _cur_sn

            elif event == '_Play_Clear_':  # clear player
                self.clear_player()
                self.reset_all()
                self._json_data = {'sum_groups': [], 'known_numbers': []}

                self._title.hide_row()

            elif event == '_Play_Open_':  # open file
                self.open_from_file()

            elif event == '_Play_Challenge_':
                _json_data = challenge_window_json(self._configs)
                if not _json_data:
                    continue
                self._json_data = _json_data
                draw_file(self._grid_parameters, self._json_data, self._graph_size, self._graph, self._title)

                self.reset_all()

            elif event == '_Play_Save_':
                # put all numbers in _json_data
                _known_nbrs = []
                for i in range(9):
                    for j in range(9):
                        if self._text_matrix[i][j]['small'] is not None:
                            _known_nbrs.append({'coord': (i, j),
                                                'small': self._text_matrix[i][j]['small'],
                                                'possible_numbers': self._text_matrix[i][j]['possible_numbers']})
                self._json_data['known_numbers'] = _known_nbrs

                save_dialog(self._grid_parameters, self._json_data)

            elif event == '_Play_Solve_':
                if self._json_data is None:
                    continue
                if 'known_numbers' not in self._json_data or not self._json_data['known_numbers']:
                    _known_nbrs = []
                    for i in range(9):
                        for j in range(9):
                            if self._text_matrix[i][j]['small'] is not None:
                                _known_nbrs.append({'coord': (i, j),
                                                    'small': self._text_matrix[i][j]['small'],
                                                    'possible_numbers': self._text_matrix[i][j]['possible_numbers']})
                    self._json_data['known_numbers'] = _known_nbrs
                try:
                    self._json_data['known_numbers'] = sudoku_solve(self._json_data, self._configs["solver"].copy())
                    draw_file(self._grid_parameters, self._json_data, self._graph_size, self._graph, self._title)
                except Exception as e:
                    print(e)
                    sg.popup_error(self._configs["lang_dict"]["_Error_Solver_"])

            elif event == '_Play_Design_':  # go to designer
                if sg.popup_ok_cancel(self._configs["lang_dict"]["_Exit_Popup_"]) == 'OK':
                    from KillerMaker import KillerMaker

                    window.close()
                    km = KillerMaker(self._configs)
                    km.init_window()

        window.close()
