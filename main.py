import json

import PySimpleGUI as sg

from KillerMaker import KillerMaker
from KillerPlayer import KillerPlayer

def main():
    with open("config.json") as f:
        configs = json.load(f)
    with open(f"lang/{configs['language']}.json") as f:
        lang_cfg = json.load(f)
    configs["lang_dict"] = lang_cfg

    sg.theme('Material2')
    _sel_layout = [[sg.Button(configs["lang_dict"]["_Main_Solve_"], key='_Main_Solve_'),
                    sg.Button(configs["lang_dict"]["_Main_Design_"], key='_Main_Design_')]]

    _sel_window = sg.Window('', _sel_layout)

    event, values = _sel_window.read()
    _sel_window.close()
    if event == '_Main_Solve_':
        k = KillerPlayer(configs)
        k.init_window()
    elif event == '_Main_Design_':
        k = KillerMaker(configs)
        k.init_window()

if __name__ == "__main__":
    main()