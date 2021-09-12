endzones = [
    [
        (-4000, 100, 7000),
        (-5000,100, 7000),
        (0, -500, 7000),
    ],
    [
        (-2000, 100, 5000),
        (-3000, 100, 5000),
        (0, -500, 5000),
    ],
    [   
        (-5800, 100, 4000),
        (-7200, 100, 4000),
        (0, -500, 4000),
    ]
]


# A little processing

import numpy as np

end_norms = []
for i in range(3):
    A,B,C = endzones[i]
    AB = np.subtract(B,A)
    AC = np.subtract(C,A)
    end_norms.append(np.cross(AB,AC))   # no need to normalise