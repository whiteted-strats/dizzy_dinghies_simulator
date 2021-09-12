# Python input -> Lua input

def luaiseInput(inputs):
    lns = ["inputs = {"]
    for A_pressed, analogue_x in inputs:
        A_pressed = "true" if A_pressed else "false"
        lns.append("  {" + A_pressed + ", " + str(analogue_x) + "},")
    lns.append("}")
    return "\n".join(lns)