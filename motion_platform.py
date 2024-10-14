import logging
import serial.tools.list_ports
import serial

logger = logging.getLogger('serial_port')


class MotionPlatform:
    def __init__(self):
        port = self._findPortByName('Prolific USB-to-Serial Comm Port')
        self._xy_serial = serial.Serial(port, 115200, timeout=0.01)

        port = self._findPortByName('USB Serial Port')
        self._z_serial = serial.Serial(port, 19200, timeout=0.1)

    def _xy_serial_communicate(self, axis_addr: int, varcom: str):
        self._xy_serial.readall() # clear input buffer

        payload = f'\\{axis_addr}\r\n'
        self._xy_serial.write(payload.encode())
        self._xy_serial.flush()
        logger.info('xy send ' + repr(payload))

        response = self._xy_serial.readline().decode(errors='replace')
        logger.info('xy read ' + repr(response))

        payload = varcom + '\r\n'
        self._xy_serial.write(payload.encode())
        self._xy_serial.flush()
        logger.info('xy send ' + repr(payload))

        response = [line.decode(errors='replace') for line in self._xy_serial.readlines()]
        logger.info('xy read ' + repr(''.join(response)))

        for line in response:
            idx = line.find('<')
            if idx != -1:
                return int(line[:idx])
        return None

    def _z_serial_communicate(self, station: bytes, cmd: bytes):
        self._z_serial.readall() # clear input buffer

        data = station + cmd
        lrc = self._calculateLRC(data)
        payload = ':' + (data + lrc).hex().upper() + '\r\n'
        self._z_serial.write(payload.encode())
        self._z_serial.flush()
        logger.info('z  send ' + repr(payload))

        response = self._z_serial.readline().decode(errors='replace')
        logger.info('z  read ' + repr(response))
        return None

    def _x_axis_execute(self, varcom: str):
        return self._xy_serial_communicate(1, varcom)

    def _y_axis_execute(self, varcom: str):
        return self._xy_serial_communicate(2, varcom)

    def _z_axis_execute(self, cmd: bytes):
        return self._z_serial_communicate(b'\x01', cmd)

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

    def homeZ(self):
        self._z_axis_execute(b'\x06\x20\x1E\x00\x03')

    def moveIncrementX(self, distance_mm, speed_mm_s):
        self._x_axis_execute(f'MOVEINC {self._XYmm2count(distance_mm)} {speed_mm_s}')

    def moveIncrementY(self, distance_mm, speed_mm_s):
        self._y_axis_execute(f'MOVEINC {self._XYmm2count(distance_mm)} {speed_mm_s}')

    def moveAbsoluteZ(self, position_mm, speed_percentage):
        speed_percentage = int(speed_percentage)
        if not 0 <= speed_percentage <= 100:
            raise ValueError(f'speed_percentage={speed_percentage} exceeds limits')
        self._z_axis_execute(b'\x06\x20\x14\x00' + speed_percentage.to_bytes())

        position_mm_times_100 = max(int(position_mm * 100), 0)
        self._z_axis_execute(b'\x10\x20\x02\x00\x02\x04' + position_mm_times_100.to_bytes(4))

        self._z_axis_execute(b'\x06\x20\x1E\x00\x01')

    @staticmethod
    def _XYmm2count(mm):
        return int(mm * 1000)

    @staticmethod
    def _findPortByName(name):
        port = ''
        for port_i, desc_i, _ in serial.tools.list_ports.comports():
            name_i = desc_i.replace(f'({port_i})','').strip()
            if name == name_i:
                if not port:
                    port = port_i
                else:
                    raise RuntimeError(f"Multiple ports with name '{name}'")
        return port

    @staticmethod
    def _calculateLRC(byte_array: bytes):
        lrc = 0
        for byte in byte_array:
            lrc = (lrc + byte) & 0xFF  # Add byte and apply mask for &HFF
        lrc = ((~lrc + 1) & 0xFF)  # Two's complement and apply mask for &HFF
        return lrc.to_bytes()
