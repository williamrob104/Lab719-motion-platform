import serial.tools.list_ports
import serial


class MotionPlatform:
    def __init__(self, log: bool=True):
        self._logger = print if log else lambda _: _

        name = 'Prolific USB-to-Serial Comm Port'
        port = next(serial.tools.list_ports.grep(name), None)
        if port:
            self._xy_serial = serial.Serial(port[0], 115200, timeout=0.01)
        else:
            raise RuntimeError(f"Cannot find port name '{name}'")

    def _x_axis_execute(self, varcom: str):
        self._logger(self._xy_serial.readall().decode())
        self._xy_serial.write(b'\\1\r')
        self._xy_serial.flush()
        self._logger(self._xy_serial.readline().decode())
        self._xy_serial.write(varcom.encode() + b'\r')
        self._xy_serial.flush()
        lines = [line.decode() for line in self._xy_serial.readlines()]
        self._logger('\r'.join(lines))
        for line in lines:
            idx = line.find('<')
            if idx != -1:
                return int(line[:idx])
        return None

    def _y_axis_execute(self, varcom: str):
        self._logger(self._xy_serial.readall().decode())
        self._xy_serial.write(b'\\2\r')
        self._xy_serial.flush()
        self._logger(self._xy_serial.readline().decode())
        self._xy_serial.write(varcom.encode() + b'\r')
        self._xy_serial.flush()
        lines = [line.decode() for line in self._xy_serial.readlines()]
        self._logger('\r'.join(lines))
        for line in lines:
            idx = line.find('<')
            if idx != -1:
                return int(line[:idx])
        return None

    def enable(self):
        self._x_axis_execute('EN')
        self._y_axis_execute('EN')

    def homeXY(self):
        self._x_axis_execute('HOMECMD')
        self._y_axis_execute('HOMECMD')

    def moveIncrementX(self, distance_mm, speed_mm_s):
        distance_count = self.convertXYmm2count(distance_mm)
        self._x_axis_execute(f'MOVEINC {distance_count} {speed_mm_s}')

    def moveIncrementY(self, distance_mm, speed_mm_s):
        distance_count = self.convertXYmm2count(distance_mm)
        self._y_axis_execute(f'MOVEINC {distance_count} {speed_mm_s}')

    @staticmethod
    def convertXYmm2count(mm):
        return int(mm * 1000)
