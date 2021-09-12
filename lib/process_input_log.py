# Bizhawk input file -> Python input

import re

def readInputs(fn):
    with open(fn, "r") as fs:
        lns = list(fs)

    assert lns[0] == "[Input]\n"
    assert lns[-1] == "[/Input]\n"

    logkey = lns[1].split("|")
    logkey[0] = logkey[0][7:]
    del logkey[-1]

    inputs = []

    for ln in lns[2:-1]:
        values = []
        i = 0
        while i < len(ln):
            ch = ln[i]
            if ch == "\n":
                break

            if ch == "|":
                i += 1
                continue

            if ch == " ":
                while ln[i] == " ":
                    i += 1
                s = i
                while ln[i] != ",":
                    i += 1
                analogue = int(ln[s:i])
                values.append(analogue)
                i += 1

            else:
                values.append(ch != '.')
                i += 1

        assert len(values) == len(logkey)
        inp = dict(zip(logkey, values))

        inputs.append(inp)

    return inputs


def readDinghyInputs(fn):
    inputs = readInputs(fn)
    inputs = [(inp['P1 A'], inp['#P1 X Axis']) for inp in inputs]
    return inputs
