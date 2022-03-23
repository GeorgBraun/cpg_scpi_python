"""CPG SCPI

Educational client library to use Adafruit Circuit Playground via SCPI protocol in Python3.
"""

__version__ = '0.0.1'
__author__ = 'Georg Braun'

import serial.tools.list_ports
import sys

class CircuitPlayground:

    def __init__(self, comport = None, baudrate = 115200) -> None:
        self.comPortObj = None
        self.comPort = comport
        self.baudrate = baudrate
        self._findAndConnectComPort()
        if self.is_open:
            print(self.idn())
            print(self.config())

    def close(self):
        if self.is_open:
            self.comPortObj.close()
    
    @property
    def is_open(self):
        return self.comPortObj.is_open

    def idn(self) -> str:
        return self._query('*IDN?', 6)

    def config(self) -> str:
        return self._query('SYST:CON?', 9)

    # MEAS:BUTTON?
    # MEAS:BUTTON:RIGHT?
    # MEAS:BUTTON:LEFT?
    # MEAS:SWITCH?
    # MEAS:TEMP?
    # MEAS:ACC?
    # MEAS:LIGHT? // only RAW values
    # MEAS:SOUND? // only RAW values
    # MEAS:CAP:SENSE? // Individual values from 8 cap sensors
    # MEAS:CAP:TAP?   // Single int value with one bit per cap sensor
    #                 // 0-1-threshold is defined via SYST:CON:LED:CAPLIM
    # MEAS:TIME?

    def buttonAny(self) -> str:
        return self._query('MEAS:BUTTON?', 1)

    def buttonLeft(self) -> str:
        return self._query('MEAS:BUTTON:LEFT?', 1)

    def buttonRight(self) -> str:
        return self._query('MEAS:BUTTON:RIGHT?', 1)

    def switch(self) -> str:
        return self._query('MEAS:SWITCH?', 1)

    def temp(self) -> str:
        return self._query('MEAS:TEMP?', 1)

    def acc(self) -> str:
        return self._query('MEAS:ACC?', 1)

    def light(self) -> str:
        return self._query('MEAS:LIGHT?', 1)

    def sound(self) -> str:
        return self._query('MEAS:SOUND?', 1)

    def capSense(self) -> str:
        return self._query('MEAS:CAP:SENSE?', 1)

    def capTap(self) -> str:
        return self._query('MEAS:CAP:TAP?', 1)

    def time(self) -> str:
        return self._query('MEAS:TIME?', 1)


    def _query(self, cmd: str, expectedLines: int):
        self.comPortObj.write((cmd+'\n').encode('utf-8'))
        response = ''
        for i in range(expectedLines):
          response = response + self.comPortObj.readline().decode('utf-8')
        return response.strip() # remove leading and trailing whitespace

    def _findAndConnectComPort(self):
        if self.comPort is None: self._findComPort()

        self.comPortObj = serial.Serial(self.comPort, self.baudrate, timeout=10) # timeout is for reads
        print(f'{self.comPortObj.name=}')
    
    def _findComPort(self) -> str:
        x=list(serial.tools.list_ports.grep("adafruit"))
        if len(x)==0:
            print('=====================================================')
            print('ERROR in cpg_scpi: Could not find any serial port for')
            print('                   Adafruit Circuit Playground.')
            print()
            print('Will terminate program.')
            print('=====================================================')
            self.comPort = None
            sys.exit(1)
        elif len(x)>1:
            self.comPort = x[0].device
            print( '=====================================================')
            print(f'WARNING in cpg_scpi: Found {len(x)} Circuit Playgrounds.')
            print(f'                     Will take the one on {self.comPort}.')
            print( '=====================================================')
        else: # len(x)==1
            self.comPort = x[0].device
            print( '============================================================')
            print(f'INFO in cpg_scpi: Found Circuit Playgrounds on {self.comPort}')
            print( '============================================================')



    # x=serial.tools.list_ports.grep("adafruit*")
    # y=next(x)

    # print(f'{x[0].device=}')        # 'COM9' (docu: Full device name/path, e.g. /dev/ttyUSB0.)
    # print(f'{x[0].name=}')          # 'COM9' (docu: Short device name, e.g. ttyUSB0.)
    # print(f'{x[0].description=}')   # 'Adafruit Circuit Playground (COM9)'
    # print(f'{x[0].hwid=}')          # 'USB VID:PID=239A:8011 SER=6&3A757EEC&0&2 LOCATION=1-1.2:x.0'
    # print(f'{x[0].vid=}')           # 9114 (docu: USB Vendor ID (integer, 0. . . 65535).)
    # print(f'{x[0].pid=}')           # 32785 (docu: USB product ID (integer, 0. . . 65535).)
    # print(f'{x[0].serial_number=}') # '6&3A757EEC&0&2' (docu: USB serial number as a string.)
    # print(f'{x[0].location=}')      # '1-1.2:x.0' (docu: USB device location string (“<bus>-<port>[-<port>]. . . ”))
    # print(f'{x[0].manufacturer=}')  # 'Adafruit Industries LLC' (docu: USB manufacturer string, as reported by device.)
    # print(f'{x[0].product=}')       # None (docu: USB product string, as reported by device.)
    # print(f'{x[0].interface=}')     # None (docu: Interface specific description, e.g. used in compound USB devices.)

    # ser = serial.Serial('/dev/ttyS1', 19200, timeout=1)

