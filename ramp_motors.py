import logging
import time
from motion_platform import MotionPlatform

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    platform = MotionPlatform()
    platform.enable()
    time.sleep(5)
    platform.homeXY()
    platform.homeZ()
    while not (platform.isMoveCompletedX() and platform.isMoveCompletedY() and platform.isMoveCompletedZ()):
        time.sleep(0.1)

    x_distance = 500
    y_distance = 500
    z_position = 0

    while True:
        if platform.isMoveCompletedX():
            platform.moveIncrementX(x_distance, platform.maxSpeedX)
            x_distance *= -1

        if platform.isMoveCompletedY():
            platform.moveIncrementY(y_distance, platform.maxSpeedY)
            y_distance *= -1

        if platform.isMoveCompletedZ():
            if z_position == 0:
                z_position = 200
                platform.moveAbsoluteZ(z_position, 100)
            else:
                z_position = 0
                platform.moveAbsoluteZ(z_position, 100)
        time.sleep(0.1)