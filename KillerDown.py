import time
from datetime import date

import PySimpleGUI as sg
import fitz  # https://pymupdf.readthedocs.io/
import requests  # https://requests.readthedocs.io/
from bs4 import BeautifulSoup  # https://www.crummy.com/software/BeautifulSoup/bs4/doc/

from GridHelper import select_idx, create_sum_group


def try_requests(url: str, retries: int) -> requests.Response:
    """
    try several times accessing the url, otherwise, raise ReadTimeout.

    :param url: the url we need to access
    :param retries: the number of retries we want to try before raise Error
    :return:
    """
    if retries == 0:
        raise requests.ReadTimeout
    try:
        return requests.get(url, timeout=50)
    except (requests.ConnectionError, requests.ReadTimeout):
        return try_requests(url, retries - 1)


def extract_cages(dashed_lines: list, x_boarders: list, y_boarders: list) -> list:
    """
    Extract all cages from the pdf using dashed line in pdf.

    :param dashed_lines: all dashed line info in the pdf
    :param x_boarders: the boarders for x-axis on the pdf
    :param y_boarders: the boarders for y-axis on the pdf
    :return: the grid record the group of each cell
    """
    cell_cages = [[{} for _ in range(9)] for _ in range(9)]
    cur_cage_id = 0

    for b in dashed_lines:
        cell1 = select_idx(b.x0, b.y0, x_boarders, y_boarders)
        cell2 = select_idx(b.x1, b.y1, x_boarders, y_boarders)
        cells_changed = []
        cage_id = -1
        if cell1 == cell2 and cell_cages[cell1[0]][cell1[1]]:
            continue
        elif cell1 == cell2:
            cells_changed.append(cell1)
        elif cell1[0] == cell2[0]:
            for i in range(min(cell1[1], cell2[1]), max(cell1[1], cell2[1]) + 1):
                if cell_cages[cell1[0]][i]:
                    cage_id = cell_cages[cell1[0]][i]['group']
                else:
                    cells_changed.append((cell1[0], i))
        elif cell1[1] == cell2[1]:
            for i in range(min(cell1[0], cell2[0]), max(cell1[0], cell2[0]) + 1):
                if cell_cages[i][cell1[1]]:
                    cage_id = cell_cages[i][cell1[1]]['group']
                else:
                    cells_changed.append((i, cell1[1]))
        else:
            raise ValueError
        if cage_id == -1:
            cage_id = cur_cage_id
            cur_cage_id += 1
        for cell in set(cells_changed):
            cell_cages[cell[0]][cell[1]]['group'] = cage_id

    return cell_cages


def extract_cage_sums(text_blocks_dicts: list, cell_cages: list, x_boarders: list, y_boarders: list) -> (dict, list):
    """
    Get sums for each cage from the pdf text blocks dictionaries.

    :param text_blocks_dicts: pdf text blocks dictionaries
    :param cell_cages: the list record the group of each cell
    :param x_boarders: the boarders for x-axis on the pdf
    :param y_boarders: the boarders for y-axis on the pdf
    :return: ks_info is the killer sudoku information, _cell_cages is the original list with extra sum infos
    """
    ks_info_lines = text_blocks_dicts[1]['lines']
    ks_info = {'number': ks_info_lines[0]['spans'][0]['text'],
               'difficulty': ks_info_lines[1]['spans'][0]['text']}

    for i in range(2, len(text_blocks_dicts)):
        text_block = text_blocks_dicts[i]
        cur_row = [i for i in range(len(y_boarders) - 1)
                   if y_boarders[i] < text_block['bbox'][3] < y_boarders[i + 1]][0]
        for line in text_block['lines']:
            cur_col = [i for i in range(len(x_boarders) - 1)
                       if x_boarders[i] < line['bbox'][2] < x_boarders[i + 1]][0]
            cell_cages[cur_row][cur_col]['sum'] = int(line['spans'][0]['text'])
    return ks_info, cell_cages


def get_challenge_json(weekly: bool = False, selected_date: date = date.today()) -> dict:
    """
    Retrive the PDF of the weekly/daily challenge and convert them to json dict

    :param weekly: boolean indicates weekly or daily challenge
    :param selected_date: the date the player selected
    :return: json dictionary containing sum groups and killer sudoku infos
    """
    tic = time.time()
    if selected_date > date.today():
        selected_date = date.today()
    mo = selected_date.month
    da = selected_date.day
    ye = selected_date.year

    url_prefix = 'https://www.killersudokuonline.com'
    url = url_prefix + '/archives/' + str(ye) + '/' + str(mo) + '/' + str(da)

    r = try_requests(url, 5)
    soup = BeautifulSoup(r.text, 'html.parser')

    if weekly:
        ktag = soup.find('a', {"name": "kweekly"})
    else:
        ktag = soup.find('a', {"name": "kdaily"})

    if ktag is None:
        raise ValueError

    k_pdf = ktag.find('a', href=True)['href']
    k_pdf_link = url_prefix + k_pdf

    r_pdf = try_requests(k_pdf_link, 5)

    doc = fitz.Document(stream=r_pdf.content, filetype='pdf')
    page = doc[0]

    # page_w = page.rect.width
    # page_h = page.rect.height
    drawings = page.get_drawings()

    solid_lines = [d['rect'] for d in drawings if len(d['items']) == 1]
    dashed_lines = [d['rect'] for d in drawings if len(d['items']) > 1]

    x_boarders = sorted([r.x0 for r in solid_lines if r.y0 != r.y1])
    y_boarders = sorted([r.y0 for r in solid_lines if r.x0 != r.x1])

    cell_cages = extract_cages(dashed_lines, x_boarders, y_boarders)

    text_blocks_dicts = page.get_textpage().extractDICT()['blocks']

    ks_info, cell_cages = extract_cage_sums(text_blocks_dicts, cell_cages, x_boarders, y_boarders)
    sum_groups = create_sum_group(cell_cages)
    json_data = {'ks_info': ks_info, 'sum_groups': sum_groups, 'known_numbers': []}

    print('Loading time: ' + str(time.time() - tic))
    return json_data


def challenge_window_json(_configs: dict) -> dict:
    """
    shows a window to select the date and the challenge the player want to play
    then draw the puzzle and the title on the main game window
    
    :param _configs: dict of configs
    """

    weekly_layout = [[sg.Input(date.today(), size=(10, None), key='_Chall_Input_'),
                      sg.CalendarButton(_configs["lang_dict"]["_Chall_Date_"],
                                        target='_Chall_Input_',
                                        key='_Chall_Date_',
                                        format='%Y-%m-%d',
                                        month_names=_configs["lang_dict"]["_Chall_Months_"],
                                        day_abbreviations=_configs["lang_dict"]["_Chall_Days_"])],
                     [sg.Button(_configs["lang_dict"]["_Chall_Weekly_"], key='_Chall_Weekly_'),
                      sg.Button(_configs["lang_dict"]["_Chall_Daily_"], key='_Chall_Daily_')]]

    weekly_window = sg.Window('', weekly_layout, modal=True)
    try:
        while True:
            event, values = weekly_window.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == '_Chall_Weekly_':
                weekly_window.close()
                return get_challenge_json(True, date.fromisoformat(values['_Chall_Input_']))
            elif event == '_Chall_Daily_':
                weekly_window.close()
                return get_challenge_json(False, date.fromisoformat(values['_Chall_Input_']))
        weekly_window.close()
    except ValueError:
        sg.popup_error(_configs["lang_dict"]["_Error_Date_"])
        return {}
    except requests.ReadTimeout:
        sg.popup_error(_configs["lang_dict"]["_Error_Conn_"])
        return {}


# def sudoku_com_puzzle():
#     headers = {
#         "accept": "*/*",
#         "accept-language": "en-US,en;q=0.9",
#         "x-requested-with": "XMLHttpRequest"
#     }
#     r = requests.get('https://sudoku.com/api/level/easy', headers=headers)
#     return r
