from lib.dinghy_types import *
from lib.process_input_log import readDinghyInputs
from lib.luaise_data import luaiseInput
from lib.collision import locusCollision
from engine import Engine

from data.endzones import endzones, end_norms
from data.start_positions import start_positions
from data.stage_1_polys import stage_1_polys
from data.stage_2_polys import stage_2_polys
from data.stage_3_polys import stage_3_polys
course_polys = [stage_1_polys, stage_2_polys, stage_3_polys]

import matplotlib.pyplot as plt
import numpy as np

# Course & data
from inputs.new_input import new_input
COURSE = 1
checkpoints = []    

# Course 2
##checkpoints = [((3386.41666667, -4093.75), (3565.58333333, -1008.33333333), 5*30)]

# --------------------------

COURSE -= 1
endzone = endzones[COURSE]
polys = course_polys[COURSE]
end_norm = end_norms[COURSE]
start_pos = start_positions[COURSE]

def drawPlot(positions, noses, rfd_factors, text, numberEllipses=False):
        
    # Init global plot
    fig, axs = plt.subplots()
    axs.set_aspect('equal', 'datalim')

    # End
    xs,ys,zs = zip(*endzone)
    zs = [-z for z in zs]
    plt.plot(xs,zs, linewidth=1, color='g')

    # Collision
    ellipseCentres = locusCollision(plt, axs, polys)

    # Checkpoint helper
    if numberEllipses:
        for i,p in enumerate(ellipseCentres):
            x,z = p
            plt.text(x,-z,i)

    # Positions and noses :)
    xs, zs = zip(*positions)
    zs = [-z for z in zs]
    plt.plot(xs,zs, linewidth=0.5, color='b')

    xs, zs = zip(*noses)
    zs = [-z for z in zs]
    plt.plot(xs,zs, linewidth=0.5, color='m')


    for p,n,f,t in zip(positions, noses, rfd_factors, text):
        x,z = p

        if t is not None:
            plt.text(x,-z,t)


        axs.add_artist(plt.Circle((x, -z), 5, color='b', linewidth=0.5, fill=False))

        x,z = n
        axs.add_artist(plt.Circle((x, -z), 5, color='m', linewidth=0.5, fill=False))
        axs.add_artist(plt.Circle((x, -z), 0.2, color='m', linewidth=0.5, fill=False))
        axs.add_artist(plt.Circle((x, -z), 0.01, color='m', linewidth=0.5, fill=False))

        # And draw a line between the two
        xs, zs = zip(p,n)
        zs = [-z for z in zs]
        plt.plot(xs,zs, linewidth=0.5, color='k')

    plt.show()



dhyType = DinghyType(DINGHY_SPEED_TYPE)
engine = Engine(COURSE, dhyType, checkpoints)


positions = []
text = []
noses = []
rfd_factors = []

finished = False



for i, inp in enumerate(new_input):
    A_pressed, analogue_x = inp[:2]

    txt = inp[2] if len(inp) > 2 else None
    text.append(txt)

    if txt:
        print(txt)

    # Position is added before the tick, so the text will line up with when the input was delivered
    positions.append(engine.pos)
    noses.append(engine.get_nose())
    finished = engine.tick(A_pressed, analogue_x)

    if not A_pressed:
        rfd_factors.append(engine.accel_factor)
    else:
        rfd_factors.append(None)

    if engine.t > 30*4:

        if engine.speed_cap < engine.dinghy.MaxSpeed:
            print(f"[~] {engine.t / 30:.2f} : Cap is {100*engine.speed_cap / engine.dinghy.MaxSpeed:.2f}% of max speed")

        if engine.frame_speed < engine.speed_cap:
            print(f"[-] {engine.t / 30:.2f} : {100*engine.frame_speed / engine.dinghy.MaxSpeed:.2f}% speed, < cap")

        ##if engine.accel_factor < 1 and engine.t > 30*8:
        ##    print(f"[ ] {engine.t / 30:.2f} : Accel factor = {100*engine.accel_factor:.2f}%")

    if finished:
        print(f"Dropped {len(new_input) - i - 1} inputs")
        break

positions.append(engine.pos)
noses.append(engine.get_nose())
rfd_factors.append(None)

print(f"Final heading: {engine.heading}")

print("\nCheckpoints:")
for i,t in enumerate(engine.chkpnt_times):
    if t is None:
        break
    print(f"{i} : {t / 30}")

if finished:
    t = engine.get_final_time()
    print(f"End time: {t}")


    # Find the effective exact finishing time
    assert end_norm[1] == 0
    v = np.subtract(positions[-1], positions[-2])
    a = np.dot(v, end_norm[::2])
    w = np.subtract(endzone[0][::2], positions[-2])
    b = np.dot(w, end_norm[::2])
    k = b / a
    print(f"Last step {(1-k)*100:.2f}% overshot")
    t -= (1-k) / 30
    print(f"Effective time = {t}")

drawPlot(positions, noses, rfd_factors, text)   # , numberEllipses=True)

with open("inputs\\lua_input.lua", "w") as fs:
    fs.write(luaiseInput([inp[:2] for inp in new_input]))
    print("Converted for lua")