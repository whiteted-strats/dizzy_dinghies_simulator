

DINGHY_NORMAL_TYPE = 1
DINGHY_NONSLIP_TYPE = 0
DINGHY_SPEED_TYPE = 2

class DinghyType:
    def __init__(self, dhy_type):
        """
        On the differences note that:
          - MaxSpeeds are obviously significant, and are the max value for the 'speed cap'
          - Jerk determines:
            * the initial acceleration
            * the rate at which we recover turning ability following Rapid Fire Drifting
            * how irregularly we need to press A during RFD
          - MaxSpeedDecay is applied to the 'speed cap' each frame that you don't hold A,
              so is only relevant during Rapid Fire Drifting

          - The bump factors are incredibly similar, and it's likely that large bumps are never useful
              Even small bumps may not feature in any of the optimal lines.
        """

        if dhy_type == DINGHY_NORMAL_TYPE:
            self.MaxSpeed = 85.0
            self.Jerk = 1.025
            self.MaxSpeedDecay = 0.97
            self.SmallBumpFactor = 0.92
            self.LargeBumpFactor = 0.76
            
        elif dhy_type == DINGHY_NONSLIP_TYPE:
            self.MaxSpeed = 80.0
            self.Jerk = 1.10
            self.MaxSpeedDecay = 0.975
            self.SmallBumpFactor = 0.925
            self.LargeBumpFactor = 0.775

        elif dhy_type == DINGHY_SPEED_TYPE:
            self.MaxSpeed = 90.0
            self.Jerk = 1.0125
            self.MaxSpeedDecay = 0.96
            self.SmallBumpFactor = 0.9125
            self.LargeBumpFactor = 0.75

        else:
            assert False, "Bad Dinghy Type"


    def dragRaceInitialTimeloss(self):
        """
        Gets the timeloss in a straight line vs an opponent who travels at this Dinghy's
          max speed from the outset
        This is determined by Jerk and, to a lesser extent, MaxSpeed

        Prelude to full model in engine.py
        """

        # 20 frame velocity buffer, though just speeds since we're going in a straight line
        velocity_buffer = [0] * 20
        buffer_i = 0

        speed_cap = 1
        accel_factor = 0.05
        t = 0       # 30fps
        d = 0

        while any(v != self.MaxSpeed for v in velocity_buffer):

            # Update the two values (first)
            speed_cap *= 1.08
            if speed_cap > self.MaxSpeed:
                speed_cap = self.MaxSpeed

            accel_factor *= self.Jerk
            if accel_factor > 1:
                accel_factor = 1

            # Multiply to give the frame's acceleration,
            #   then apply and insert into the buffer
            frame_acceleration = speed_cap * accel_factor

            frame_speed = sum(velocity_buffer) / 20
            frame_speed += frame_acceleration
            if frame_speed > speed_cap:
                frame_speed = speed_cap

            velocity_buffer[buffer_i] = frame_speed
            buffer_i += 1
            buffer_i %= 20


            # Tick
            d += frame_speed
            t += 1
           
    
        opponent_t = d / self.MaxSpeed
        return (t - opponent_t) / 30


def main():
    # ~0.5s loss between each, so considering the max speeds
    #   the speed type will still win in a 10s drag race
    # But it's a benefit alongside better RFD
    for typ in range(3):
        dhy = DinghyType(typ)
        t = dhy.dragRaceInitialTimeloss()
        print(t)


if __name__ == "__main__":
    main()