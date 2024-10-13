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

    def _xy_serial_communicate(self, axis_addr: bytes, varcom: str):
        self._logger(self._xy_serial.readall().decode(errors='replace'))
        self._xy_serial.write(b'\\' + axis_addr + b'\r')
        self._xy_serial.flush()
        self._logger(self._xy_serial.readline().decode(errors='replace'))
        self._xy_serial.write(varcom.encode() + b'\r')
        self._xy_serial.flush()
        lines = [line.decode(errors='replace') for line in self._xy_serial.readlines()]
        self._logger('\r'.join(lines))
        for line in lines:
            idx = line.find('<')
            if idx != -1:
                return int(line[:idx])
        return None

    def _x_axis_execute(self, varcom: str):
        return self._xy_serial_communicate(b'1', varcom)

    def _y_axis_execute(self, varcom: str):
        return self._xy_serial_communicate(b'2', varcom)

    def enable(self):
        self._x_axis_execute('CLEARFAULTS')
        self._y_axis_execute('CLEARFAULTS')
        self._x_axis_execute('EN')
        self._y_axis_execute('EN')

    def isEnabled(self):
        return bool(self._x_axis_execute('ACTIVE') and self._y_axis_execute('ACTIVE'))

    def homeXY(self):
        self.moveIncrementX(5, 10)
        self.moveIncrementY(5, 10)
        self._x_axis_execute('HOMECMD')
        self._y_axis_execute('HOMECMD')

    def moveIncrementX(self, distance_mm, speed_mm_s):
        self._x_axis_execute(f'MOVEINC {self._XYmm2count(distance_mm)} {speed_mm_s}')

    def moveIncrementY(self, distance_mm, speed_mm_s):
        self._y_axis_execute(f'MOVEINC {self._XYmm2count(distance_mm)} {speed_mm_s}')

    @staticmethod
    def _XYmm2count(mm):
        return int(mm * 1000)
