import lib.dinghy_types
from data.start_positions import start_positions
from data.endzones import endzones, end_norms

import numpy as np
from math import sin, cos, sqrt, radians

def sgn(x):
    if x >= 0: return 1
    else: return -1

# Course 1 only atm (flat sides after all)


class Engine:
    def __init__(self, COURSE, dhyType, checkpoints = []):
        # Course-specific
        start_pos = start_positions[COURSE]
        self.endzone = endzones[COURSE]
        self.end_norm = end_norms[COURSE]
        assert self.end_norm[1] == 0

        self.checkpoints = checkpoints
        self.chkpnt_times = [None] * len(self.checkpoints)
        self.chkpnt_i = 0

        self.t = 0
        self.pos = start_pos[::2]
        self.height = None  # irrel on all courses
        self.finished = False
        self.dinghy = dhyType

        # 20 frame velocity (XZ) and turn [-60,60] buffers
        # Index derived from t
        self.velocity_buffer = [(0,0)] * 20
        self.turn_buffer = [0] * 20

        self.speed_cap = 0
        self.accel_factor = 0.05

        self.heading = 180

    def get_final_time(self):
        assert self.finished
        # The timer at 800EB914 starts a frame late, and explicitly counts back a frame at the end (in state 3)
        return (self.t-2) / 30

    def get_nose(self):
        # Note that this is fetched for collision detection
        #  AFTER position & heading update, so we'll be using the right values
        x,z = self.pos
        return (
            x - self.speed_cap * sin(radians(self.heading)),
            z + self.speed_cap * cos(radians(self.heading))
        )

    def do_checkpoints(self):
        if self.chkpnt_i >= len(self.checkpoints):
            return

        a,b,chkpnt_min_t = self.checkpoints[self.chkpnt_i]
        if self.t < chkpnt_min_t:
            return

        x = np.linalg.norm(np.subtract(a, self.pos))
        y = np.linalg.norm(np.subtract(b, self.pos))

        if x < y:
            return
        
        assert self.t != chkpnt_min_t, "checkpoint completed immediately"

        d = (x-y) / 2       # ~ distance past the middle
        assert d <= self.speed_cap
        chkpnt_t = self.t - (d / self.speed_cap)

        self.chkpnt_times[self.chkpnt_i] = chkpnt_t
        self.chkpnt_i += 1


            

    def tick(self, A_pressed, analogue_x):
        assert type(analogue_x) == int
        if analogue_x > -10 and analogue_x < 10:
            analogue_x = 0
        if analogue_x > 60:
            analogue_x = 60
        if analogue_x < -60:
            analogue_x = -60

        if not self.finished:
            self._tick(A_pressed, analogue_x)
            self.finished = self._is_finished()

        self.do_checkpoints()

        return self.finished
    
    def _is_finished(self):
        # End plane is vertical and the distance test is in XZ so we just ignore y
        X = self.pos
        A = self.endzone[0][::2]
        AX = np.subtract(X, A)
        if np.dot(AX, self.end_norm[::2]) < 0:
            return False
        
        return np.linalg.norm(AX) <= 1400

    def _update_two_values(self,A_pressed):
        # Update the speed_cap and accel_factor
        # speed_cap does a thing where it avoids (0,1)
        # Lifted out of Ghidra

        if (not A_pressed):
            self.speed_cap = self.speed_cap * self.dinghy.MaxSpeedDecay
            self.accel_factor = self.accel_factor * 0.90
            if self.speed_cap < 1.0:
                self.speed_cap = 0.0
        else:
            if self.speed_cap == 0.0:
                self.speed_cap = 1.0
            
            self.speed_cap = self.speed_cap * 1.08
            self.accel_factor = self.accel_factor * self.dinghy.Jerk
                

        if self.dinghy.MaxSpeed < self.speed_cap:
            self.speed_cap = self.dinghy.MaxSpeed
        
        if self.accel_factor < 0.05:
            self.accel_factor = 0.05
        
        if 1.0 < self.accel_factor:
            self.accel_factor = 1.0


    def _tick(self, A_pressed, analogue_x):
        buffer_i = self.t % 20
    
        # Process the A press
        self._update_two_values(A_pressed)

        # Process the turn and update that buffer
        # Round integer towards 0 - confirmed with testing!
        self.turn_buffer[buffer_i] = analogue_x
        s = sum(self.turn_buffer)
        frame_turn = sgn(s) * (abs(s) // 20)
        frame_turn /= 15
        
        # Produce the velocity
        C = self.speed_cap * self.accel_factor
        avg_vel = np.multiply(np.add.reduce(self.velocity_buffer), 1/20)
        frame_vel = [C*sin(radians(self.heading)), C*cos(radians(self.heading))]
        frame_vel = np.add(avg_vel, frame_vel)

        # Cap the velocity
        s = np.linalg.norm(frame_vel)
        if s > self.speed_cap:
            frame_vel = [w*self.speed_cap/s for w in frame_vel]
            s = self.speed_cap

        # ! ASSUMES NO COLLISION, otherwise for a start this frame velocity can exceed the speed cap
        self.velocity_buffer[buffer_i] = frame_vel

        # Update our position
        # x is flipped
        x,z = frame_vel
        self.frame_velocity = frame_vel
        self.frame_speed = s
        self.pos = np.add(self.pos, (-x, z))

        # Apply post-movement updates and Tick
        self.heading += frame_turn
        self.t += 1

           