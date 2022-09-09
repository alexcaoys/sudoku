import json
import os
import time

import PySimpleGUI as sg

from KillerSVG import KillerSVG


def open_ks_file(filepath: str = '') -> (bool, dict):
    """
    open and read killer sudoku cage groups from json

    :param filepath: the open file path
    :return: json dict containing cage groups and known numbers
    """
    json_data = {}
    if filepath == '':
        return False, json_data

    try:
        with open(filepath, 'r') as f:
            json_data = json.load(f)
    except Exception as e:
        print('json loading error:')
        print(e)
        raise ValueError("Invalid JSON file")

    if 'known_numbers' in json_data:
        num_of_known_numbers = len(json_data['known_numbers'])

        for i in range(num_of_known_numbers):
            json_data['known_numbers'][i]['coord'] = tuple(json_data['known_numbers'][i]['coord'])

    if 'sum_groups' in json_data:
        exist_coords = []
        all_sum = 0
        num_of_cage_groups = len(json_data['sum_groups'])

        for i in range(num_of_cage_groups):
            num_of_cells = len(json_data['sum_groups'][i]['coords'])
            for j in range(num_of_cells):
                coord = json_data['sum_groups'][i]['coords'][j]
                if coord[0] not in range(9) or coord[1] not in range(9):
                    raise ValueError("coord not in range")

                if coord in exist_coords:
                    raise ValueError("Duplicate coords")

                json_data['sum_groups'][i]['coords'][j] = tuple(coord)
                exist_coords.append(coord)
            all_sum += json_data['sum_groups'][i]['sum']

        if all_sum != 405:
            print("WARNING: Total Sum is not 405!")
            return False, json_data
        elif len(exist_coords) != 81:
            print("WARNING: Not all cells included")
            return False, json_data

    if json_data:
        return True, json_data
    else:
        return False, json_data


def save_ks_file(json_data: dict, filepath: str = "example.json"):
    """
    save killer sudoku to file

    :param json_data: json dict containing all sum groups and known numbers
    :param filepath: the path of save file
    """

    if 'sum_groups' in json_data:
        for i in range(len(json_data['sum_groups'])):
            for j in range(len(json_data['sum_groups'][i]['coords'])):
                json_data['sum_groups'][i]['coords'][j] = list(json_data['sum_groups'][i]['coords'][j])

    if 'known_numbers' in json_data:
        for i in range(len(json_data['known_numbers'])):
            json_data['known_numbers'][i]['coord'] = list(json_data['known_numbers'][i]['coord'])

    with open(filepath, 'w') as f:
        json.dump(json_data, f)


def save_dialog(_configs: dict, json_data: dict):
    """
    Open a window for user to specify the output files to save and save the files

    :param _configs: dict of configs
    :param json_data: json dictionary containing sum groups and known numbers
    :return: None
    """
    save_window = sg.Window(_configs["lang_dict"]["_Save_Title_"],
                            [[sg.Text(_configs["lang_dict"]["_Save_Input_"]), sg.Input(size=(10, None), key='_Save_Input_')],
                             [sg.Checkbox(_configs["lang_dict"]["_Save_json_"], key='_Save_json_')],
                             [sg.Checkbox(_configs["lang_dict"]["_Save_svg_"], key='_Save_svg_')],
                             [sg.Checkbox(_configs["lang_dict"]["_Save_png_"], key='_Save_png_')],
                             [sg.Button(_configs["lang_dict"]["_Save_OK_"], key='_Save_OK_'),
                              sg.Button(_configs["lang_dict"]["_Save_Cancel_"], key='_Save_Cancel_')]],
                            background_color='white',
                            modal=True)
    event, values = save_window.read()
    if event in (sg.WIN_CLOSED, '_Save_Cancel_'):
        return
    elif event == '_Save_OK_':
        tic = time.time()
        if not (values['_Save_json_'] or values['_Save_svg_'] or values['_Save_png_']):
            return
        save_name = values['_Save_Input_']
        if save_name == '':
            save_name = time.strftime("%Y%m%d-%H%M%S")
        _file_folder = os.path.join(os.getcwd(), 'saved_puzzles')
        if not os.path.exists(_file_folder):
            os.mkdir(_file_folder)
        
        if values['_Save_json_']:
            save_ks_file(json_data, os.path.join(_file_folder, save_name + ".json"))
        if values['_Save_svg_'] or values['_Save_png_']:
            ksvg = KillerSVG(_configs["grid_parameters"])
            png_size = 2000
            svg_bs, img_bs = ksvg.draw(json_data, values['_Save_png_'], png_size)
            if values['_Save_png_']:
                with open(os.path.join(_file_folder, save_name + ".png"), 'wb') as f:
                    f.write(img_bs)
            if values['_Save_svg_']:
                with open(os.path.join(_file_folder, save_name + ".svg"), 'wb') as f:
                    f.write(svg_bs)
        print('Save time: ' + str(time.time() - tic))
    save_window.close()


def draw_file(grid_parameters: dict, json_data: dict,
              size: int, graph, title):
    """
    Draw json_data to the graph

    :param grid_parameters: dict of drawing parameters
    :param json_data: json dictionary containing sum groups and known numbers
    :param size: The size of the graph element
    :param graph: the Graph Element we need to draw the puzzle on
    :param title: the Graph Element we need to draw the title on
    """
    tic = time.time()

    ksvg = KillerSVG(grid_parameters)
    svg_bs, img_bs = ksvg.draw(json_data, True, size)

    graph.erase()
    graph.draw_image(data=img_bs, location=(0, 0))

    title.erase()
    if 'ks_info' in json_data:
        title.unhide_row()
        title.update(visible=True)
        title.draw_text(json_data['ks_info']['number'],
                        (0, 0), font=('sans-serif', 16),
                        text_location=sg.TEXT_LOCATION_TOP_LEFT)
        title.draw_text(json_data['ks_info']['difficulty'],
                        (size, 0), font=('sans-serif', 16),
                        text_location=sg.TEXT_LOCATION_TOP_RIGHT)
    else:
        title.hide_row()
        title.update(visible=False)

    print('Drawing time: ' + str(time.time() - tic))
