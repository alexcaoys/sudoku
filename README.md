# sudoku

Nothing interesting here. A simple **Python** (Yes, it's Python, so it's slow) Sudoku and Killer Sudoku Designer and Player.

It's actually made in 2021. Always want to upload it to Github, just lazy...

Please try it out and it's straightforward I guess?

## What you need?

I know I should make it as a package but yeah, maybe later.

You can check every line in these files, but I believe what you need is:

- Python (of course)

`pip install` the following (Not sure about version, but 99% sure latest will work)
- [requests](https://requests.readthedocs.io/)
- [PySimpleGUI](https://www.pysimplegui.org/en/latest/)
- [pycairo](https://pycairo.readthedocs.io/)
- [pymupdf](https://pymupdf.readthedocs.io/)
- [BeautifulSoup (bs4)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [pulp](https://coin-or.github.io/pulp/)

Here is one line for all the lazies like me.
```
pip install requests PySimpleGUI pycairo PyMuPDF beautifulsoup4 pulp
```

and install one of these on your system if you want it solve puzzles for you (Hooray)
- [Gurobi](https://www.gurobi.com/) (Yes, it's fast. But it's not open source and not cheap)
- [SCIP](https://www.scipopt.org/) (After some tests, this is actually decent and open source)
- Something else (Please check [pulp Solver docs](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html))

## What can it do?

Well, you will have 
- Designer, which you can **design** your (Killer) Sudoku puzzles.
- Player, which you can **play** them.
- (JSON, SVG, PNG), for these puzzles you designed. Personally I think it can generate **very pretty** puzzle images.
- a **Challenge** feature, which extract the Daily/Weekly Killer Sudoku Challenge Puzzle from *https://www.killersudokuonline.com*. I believe that's legal?
- And! (Claps here!) **Solver!!!** I know those challenges are very hard. So I thought, why not? I didn't find anything like this online(especially since it's for Killer Sudoku). The logic behind it is pretty simple (for a math student). You can check it out.

#

**Anyway, I just lost interests on writing this README, so enjoy and let me know if anything can be improved.**

P.S. I know, some data structures are not pretty. I am lazy. So maybe you can suggest and maybe I will take a look.

P.P.S. I know, package! and PyPI! Later! 