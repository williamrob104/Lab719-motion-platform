import serial.tools.list_ports
import serial

class MotionPlatform:
    def __init__(self, log: bool=True):
        self._logger = print if log else lambda _: _

        name = 'Prolific USB-to-Serial Comm Port'
        ports = serial.tools.list_ports.grep(name)
        port = next(ports, None)
        if port:
            self._xy_serial = serial.Serial(port[0], 115200, timeout=0.1)
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

    @staticmethod
    def findPortByFriendlyName(friendly_name):
        found_port = ''
        for port, desc, hwid in serial.tools.list_ports.comports():
            port_friendly_name = desc.replace(f'({port})','').strip()
            if port_friendly_name == friendly_name:
                if not found_port:
                    found_port = port
                else:
                    raise RuntimeError(f"Multiple ports with name '{friendly_name}'")
        return found_port