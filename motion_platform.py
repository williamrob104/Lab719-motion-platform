import logging
import serial.tools.list_ports
import serial

logger = logging.getLogger('serial_port')


class MotionPlatform:
    def __init__(self):
        port = self._findPortByName('Prolific USB-to-Serial Comm Port')
        self.cdhd_drive = CDHDDrive(port, baudrate=115200, timeout=0.01)
        self._xAxisExecute('OPMODE 8')
        self._yAxisExecute('OPMODE 8')

        port = self._findPortByName('USB Serial Port')
        self.tc100_drive = TC100Drive(port, baudrate=19200, timeout=0.1)

    def _xAxisExecute(self, varcom: str):
        return self.cdhd_drive.communicate(1, varcom)

    def _yAxisExecute(self, varcom: str):
        return self.cdhd_drive.communicate(2, varcom)

    def _zAxisExecute(self, cmd: bytes):
        return self.tc100_drive.communicate(b'\x01', cmd)

    def enable(self):
        self._xAxisExecute('CLEARFAULTS')
        self._yAxisExecute('CLEARFAULTS')
        self._xAxisExecute('EN')
        self._yAxisExecute('EN')
        self._zAxisExecute(b'\x06\x20\x11\x00\x01') # clear fault sequence 1
        self._zAxisExecute(b'\x06\x20\x1E\x00\x06') # clear fault sequence 2
        self._zAxisExecute(b'\x06\x20\x11\x00\x00') # power on

    def isEnabled(self):
        return self._xAxisExecute('ACTIVE') == 1 and \
               self._yAxisExecute('ACTIVE') == 1 and \
               self._zAxisExecute(b'\x03\x10\x20\x00\x01') == b'\x03\x02\x00\x0E'

    def homeXY(self):
        self.moveIncrementX(5, 10)
        self.moveIncrementY(5, 10)
        self._xAxisExecute('HOMECMD')
        self._yAxisExecute('HOMECMD')

    def moveAbsoluteX(self, position_mm, speed_mm_s):
        self._xAxisExecute(f'MOVEABS {self._XYmm2count(position_mm)} {speed_mm_s}')

    def moveAbsoluteY(self, position_mm, speed_mm_s):
        self._yAxisExecute(f'MOVEABS {self._XYmm2count(position_mm)} {speed_mm_s}')

    def moveIncrementX(self, distance_mm, speed_mm_s):
        self._xAxisExecute(f'MOVEINC {self._XYmm2count(distance_mm)} {speed_mm_s}')

    def moveIncrementY(self, distance_mm, speed_mm_s):
        self._yAxisExecute(f'MOVEINC {self._XYmm2count(distance_mm)} {speed_mm_s}')

    def isMoveCompletedX(self):
        return self._xAxisExecute('STOPPED') in [1, 2]

    def isMoveCompletedY(self):
        return self._yAxisExecute('STOPPED') in [1, 2]

    def homeZ(self):
        self._zAxisExecute(b'\x06\x20\x1E\x00\x03')

    def moveAbsoluteZ(self, position_mm, speed_percentage):
        speed_percentage = int(speed_percentage)
        if not 0 <= speed_percentage <= 100:
            raise ValueError(f'speed_percentage={speed_percentage} exceeds limits')
        self._zAxisExecute(b'\x06\x20\x14\x00' + speed_percentage.to_bytes())

        position_mm_times_100 = max(int(position_mm * 100), 0)
        self._zAxisExecute(b'\x10\x20\x02\x00\x02\x04' + position_mm_times_100.to_bytes(4))

        self._zAxisExecute(b'\x06\x20\x1E\x00\x01')

    @property
    def maxSpeedX(self):
        return 2500 # mm/s

    @property
    def maxSpeedY(self):
        return 2000 # mm/s

    @staticmethod
    def _XYmm2count(mm):
        return int(mm * 1000)

    @staticmethod
    def _findPortByName(name):
        port = None
        for port_i, desc_i, _ in serial.tools.list_ports.comports():
            name_i = desc_i.replace(f'({port_i})','').strip()
            if name == name_i:
                if port is None:
                    port = port_i
                else:
                    raise RuntimeError(f"Multiple ports with name '{name}'")
        if port is None:
            raise RuntimeError(f"Cannot find port with name '{name}'")
        return port


class CDHDDrive:
    def __init__(self, port, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 1
        self.ser = serial.Serial(port, **kwargs)

    def communicate(self, axis_addr: int, varcom: str):
        self.ser.readall() # clear input buffer

        payload = f'\\{axis_addr}\r\n'
        self.ser.write(payload.encode())
        self.ser.flush()
        logger.info('CDHD  send ' + repr(payload))

        response = self.ser.readline().decode(errors='replace')
        logger.info('CDHD  read ' + repr(response))

        payload = varcom + '\r\n'
        self.ser.write(payload.encode())
        self.ser.flush()
        logger.info('CDHD  send ' + repr(payload))

        response = [line.decode(errors='replace') for line in self.ser.readlines()]
        logger.info('CDHD  read ' + repr(''.join(response)))

        for line in response:
            idx = line.find('<')
            if idx != -1:
                return int(line[:idx])
        return None


class TC100Drive:
    def __init__(self, port, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 1
        self.ser = serial.Serial(port, **kwargs)

    def communicate(self, station: bytes, cmd: bytes):
        self.ser.readall() # clear input buffer

        data = station + cmd
        lrc = self._calculateLRC(data)
        payload = ':' + (data + lrc).hex().upper() + '\r\n'
        self.ser.write(payload.encode())
        self.ser.flush()
        logger.info('TC100 send ' + repr(payload))

        response = self.ser.readline().decode(errors='replace')
        logger.info('TC100 read ' + repr(response))
        return bytes.fromhex(response.strip()[3:-2])

    @staticmethod
    def _calculateLRC(byte_array: bytes):
        lrc = 0
        for byte in byte_array:
            lrc = (lrc + byte) & 0xFF  # Add byte and apply 0xFF mask
        lrc = ((~lrc + 1) & 0xFF)  # Two's complement and apply 0xFF mask
        return lrc.to_bytes()