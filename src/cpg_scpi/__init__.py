"""CPG SCPI

Educational client library to use Adafruit Circuit Playground (CPG) via SCPI protocol in Python3.

The Circuit Playground (CPG) needs to be connected via a USB data cable (a charging cable is not sufficient)
and needs to run the SCPI firmware from https://github.com/GeorgBraun/SCPI-for-Adafruit-Circuit-Playground
"""

__version__ = '0.3.0'
__author__ = 'Georg Braun'

import serial    # Docu at https://pythonhosted.org/pyserial/
import serial.tools.list_ports
import sys
import time
import inspect as _inspect
from typing import Tuple
# import math

class CircuitPlayground:
    '''Class to communicate with an Adafruit Circuit Playground via a serial com port and the SCPI protocol'''

    def __init__(self, comport = 'auto', baudrate = 115200) -> None:
        '''Create a CircuitPlayground object and connect to CircuitPlayground via serial com port.'''
        self.emuMode = False
        self.comPortObj = None
        self.comPort = comport
        self.baudrate = baudrate
        self._findAndConnectComPort()
        if self.is_open:
            print(self.idn())
            print(self.config())

    def __del__(self) -> None:
        '''Destructor'''
        self.close()

    def close(self) -> None:
        '''Close com port connection.'''
        if self.is_open:
            print(f'Closing {self.comPortObj.name}')
            self.comPortObj.close()
    
    @property
    def is_open(self) -> bool:
        '''Return True or False depending on if serial com port is connected.'''
        return (self.comPortObj is not None) and (self.comPortObj.is_open)

    def idn(self) -> str:
        '''Identify connected CircuitPlayground.'''
        return self._query('*IDN?', 6)

    def config(self) -> str:
        '''Query configuration parameters of CircuitPlayground.'''
        return self._query('SYST:CON?', 9)

    # Overview of available SCPI commands on the CPG.
    # Query commands to have a trailing ? and provide a response,
    # settings commands to not have a trailing ?. They usually do not provide a response,
    # except in case of errors.
    #
    # *IDN?
    # *RST
    # SYST:CON?
    #
    # OUT:LED:RED <1/0>
    # OUT:LED <VALUE>
    # OUT:DEMO:LED
    #
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
    # MEAS:TIME?      // CPG uptime in ms since power-on
    #
    # Currently not used: Setting commands to change the CPG configuration:
    # SYST:CON:TIMESTAMP <OFF/MS>
    # SYST:CON:MEAS:TINT <VALUE>
    # SYST:CON:MEAS:COUNT <-1..VALUE>
    # SYST:CON:MEAS:TYPE <SI/RAW>
    # SYST:CON:MEAS:CAPLIM <VALUE>
    # SYST:CON:LED:COL <VALUE>
    #
    # MEAS:STOP


    # Left or right button:

    def buttonAny(self) -> bool:
        '''Test if left or right button is pressed, or both. If so, return True otherwise False.'''
        # SI responses from CPG:
        # '16105 0' -> no button is pressed
        # '16105 1' -> left or right button is pressed, or both
        return self._parseBoolAfterTimestamp1( self._query('MEAS:BUTTON?', 1) )

    def buttonAny_wts(self) -> Tuple[float, bool]:
        '''Test if left or right button is pressed, or both. Return True or False with timestamp in seconds as a tuple (timestamp, pressed).'''
        # SI responses from CPG:
        # '16105 0' -> no button is pressed
        # '16105 1' -> left or right button is pressed, or both
        return self._parseBoolWithTimestamp1( self._query('MEAS:BUTTON?', 1) )

    # Left button:
    
    def buttonLeft(self) -> bool:
        '''Test if left button is pressed. If so, return True otherwise False.'''
        # SI responses from CPG:
        # '16105 0' -> left button is not pressed
        # '16105 1' -> left is pressed
        return self._parseBoolAfterTimestamp1( self._query('MEAS:BUTTON:LEFT?', 1) )

    def buttonLeft_wts(self) -> Tuple[float, bool]:
        '''Test if left button is pressed. Return True or False with timestamp in seconds as a tuple (timestamp, pressed).'''
        # SI responses from CPG:
        # '16105 0' -> left button is not pressed
        # '16105 1' -> left is pressed
        return self._parseBoolWithTimestamp1( self._query('MEAS:BUTTON:LEFT?', 1) )

    # Right button:

    def buttonRight(self) -> bool:
        '''Test if right button is pressed. If so, return True otherwise False.'''
        # SI responses from CPG:
        # '16105 0' -> right button is not pressed
        # '16105 1' -> right is pressed
        return self._parseBoolAfterTimestamp1( self._query('MEAS:BUTTON:RIGHT?', 1) )

    def buttonRight_wts(self) -> Tuple[float, bool]:
        '''Test if right button is pressed. Return True or False with timestamp in seconds as a tuple (timestamp, pressed).'''
        # SI responses from CPG:
        # '16105 0' -> right button is not pressed
        # '16105 1' -> right is pressed
        return self._parseBoolWithTimestamp1( self._query('MEAS:BUTTON:RIGHT?', 1) )

    # Switch:

    def switch(self) -> bool:
        '''Test if switch is in on position. If so, return True otherwise False.'''
        # SI responses from CPG:
        # '16105 0' -> switch in off position
        # '16105 1' -> switch in on position
        return self._parseBoolAfterTimestamp1( self._query('MEAS:SWITCH?', 1) )

    def switch_wts(self) -> Tuple[float, bool]:
        '''Test if switch is in on position. Return True or False with timestamp in seconds as a tuple (timestamp, on).'''
        # SI responses from CPG:
        # '16105 0' -> switch in off position
        # '16105 1' -> switch in on position
        return self._parseBoolWithTimestamp1( self._query('MEAS:SWITCH?', 1) )

    # Temperature sensor:

    def temp(self) -> float:
        '''Measure temperature in °C and return it as a single float value.'''
        # SI response from CPG:
        # '16105 23.41' -> 23.41 °C
        return self._parseFloatAfterTimestamp1( self._query('MEAS:TEMP?', 1) )

    def temp_wts(self) -> Tuple[float, float]:
        '''Measure temperature in °C and return it with timestamp in seconds as a tuple with 2 float values (timestamp, temp).'''
        # SI response from CPG:
        # '16105 23.41' -> 23.41 °C
        return self._parseFloatWithTimestamp1( self._query('MEAS:TEMP?', 1) )

    # Accelerometer:

    def acc(self) -> Tuple[float, float, float]:
        '''Measure acceleration in m/s^2 and return it as tuple with 3 float values (x, y, z)'''
        # SI response from CPG:
        # '16105 -0.30 -0.68 9.59' -> x=-0.30 m/s^2, y=-0.68 m/s^2, z=9.59 m/s^2
        return self._parseFloatAfterTimestamp3( self._query('MEAS:ACC?', 1) )

    def acc_wts(self) -> Tuple[float, float, float, float]:
        '''Measure acceleration in m/s^2 and return it with timestamp in seconds as tuple with 4 float values (timestamp, x, y, z)'''
        # SI response from CPG:
        # '16105 -0.30 -0.68 9.59' -> x=-0.30 m/s^2, y=-0.68 m/s^2, z=9.59 m/s^2
        return self._parseFloatWithTimestamp3( self._query('MEAS:ACC?', 1) )

    # Light sensor:

    def light(self) -> int:
        '''Measure light intensity and return it as a single int value between 0 and 1023 with 680 corresponding to approx. 1000 lx (lux).'''
        # SI response from CPG:
        # '16105 197' 
        return self._parseIntAfterTimestamp1( self._query('MEAS:LIGHT?', 1) )

    def light_wts(self) -> Tuple[float, int]:
        '''Measure light intensity and return it with timestamp in seconds as a tuple with float and int (timestamp, light)'''
        # SI response from CPG:
        # '16105 197' 
        return self._parseIntWithTimestamp1( self._query('MEAS:LIGHT?', 1) )

    # Microphone:

    # def microphone(self) -> int:
    #     '''Measure microphone value and return it as a single int value between 0 and 1023 with approx. 330 corresponding to silence.'''
    #     # SI response from CPG:
    #     # '16105 330'
    #     return self._parseIntAfterTimestamp1( self._query('MEAS:SOUND?', 1) )

    # def microphone_wts(self) -> Tuple[float, int]:
    #     '''Measure microphone value and return it with timestamp in seconds as a tuple with float and int (timestamp, sound).'''
    #     # SI response from CPG:
    #     # '16105 330'
    #     return self._parseIntWithTimestamp1( self._query('MEAS:SOUND?', 1) )

    # def capSense(self) -> str:
    #     # SI response from CPG:
    #     # '16105 0 0 0 0 206 146 0 0'
    #     return self._query('MEAS:CAP:SENSE?', 1)

    # Touch sensors:

    def touch(self) -> int:
        '''Test if cap sensors are touched and return a single int value between 0 and 255 with one bit for each sensor.'''
        # SI response from CPG:
        # '16105 0' -> no cap sensor is touched
        # '16105 255' -> all cap sensors are touched
        return self._parseIntAfterTimestamp1( self._query('MEAS:CAP:TAP?', 1) )

    def touch_wts(self) -> Tuple[float, int]:
        '''Test if cap sensors are touched and return the timestamp in seconds an int value between 0 and 255 with one bit for each sensor.'''
        # SI response from CPG:
        # '16105 0' -> no cap sensor is touched
        # '16105 255' -> all cap sensors are touched
        return self._parseIntWithTimestamp1( self._query('MEAS:CAP:TAP?', 1) )

    # Uptime of CPG:

    def uptime(self) -> float:
        '''Return current CPG uptime in seconds as a single float value.'''
        # SI response from CPG:
        # '16105' -> uptime in milli-seconds
        return self._parseFloatTimestamp( self._query('MEAS:TIME?', 1) )

    # LEDs:

    def led(self, value) -> None:
        '''Control the 10 neopixel LEDs with a value between 0 (all off) and 1023 (all on).'''
        print(f'LEDs {value:010b}')
        self._query(f'OUT:LED {int(value)}', 0)

    def ledDemo(self) -> None:
        '''Briefly flash all 10 neopixel LEDs with different colors.'''
        # print(f'LEDs {0:010b}')
        print(f'LEDs {1023:010b}')
        print(f'LEDs {0:010b}')
        self._query('OUT:DEMO:LED', 0)

    # Timing:

    def wait(self, seconds: float = 0):
        '''Waits for seconds, e.g. 0.1 for 100 milli-seconds'''
        time.sleep(seconds)

    def _query(self, cmd: str, expectedLines: int):
        '''Send command or query to CPG and receive response, if any. Also do some error detection.'''
        self.comPortObj.write((cmd+'\n').encode('utf-8'))
        response = ''
        unexptected = ''
        for i in range(expectedLines):
            received = self.comPortObj.readline().decode('utf-8')
            if received.startswith('ERROR'):
                raise Exception(f'CPG-ERROR in cpg_scpi.{_inspect.currentframe().f_code.co_name}(): "{received.strip()}"')
            response += received

        # Check if there is more response than expected:
        self.wait(0.005)
        while self.comPortObj.in_waiting>0:
            # There are still some characters in the input buffer, even if did not expect them
            received = self.comPortObj.readline().decode('utf-8')
            if received.startswith('ERROR'):
                raise Exception(f'CPG-ERROR in cpg_scpi.{_inspect.currentframe().f_code.co_name}(): "{received.strip()}"')
            unexptected += received
            self.wait(0.005)
        if len(unexptected)>0:
            raise Exception(f'ERROR in cpg_scpi.{_inspect.currentframe().f_code.co_name}(): UNEXPECTED RESPONSE: "{unexptected.strip()}"')
        
        return response.strip() # remove leading and trailing whitespace
    
    # Methods to parse response string

    def _parseFloatAfterTimestamp1(self, response: str) -> float:
        """"Parses the first value after the timestamp and returns it as single float value.
        Example:  _parseAfterTimestamp1('96372 -0.23 -0.34 9.53') -> -0.23
        """
        items = response.split()
        return float(items[1])

    def _parseFloatWithTimestamp1(self, response: str) -> Tuple[float, float]:
        """"Parses the timestamp in seconds and the following value and returns them as tuple with 2 float values.
        Example:  _parseWithTimestamp1('96372 -0.23 -0.34 9.53') -> (96.372, -0.23)
        """
        items = response.split()
        return float(items[0])/1000, float(items[1])

    def _parseFloatAfterTimestamp3(self, response: str) -> Tuple[float, float, float]:
        """"Parses the first three values after the timestamp and returns them as tuple with 3 float values.
        Example:  _parseAfterTimestamp3('96372 -0.23 -0.34 9.53') -> (-0.23, -0.34, 9.53)
        """
        items = response.split()
        return float(items[1]), float(items[2]), float(items[3])

    def _parseFloatWithTimestamp3(self, response: str) -> Tuple[float, float, float, float]:
        """"Parses the time stamp in seconds and the following three values and returns them as tuple with 4 float values.
        Example:  _parseWithTimestamp3('96372 -0.23 -0.34 9.53') -> (96.372, -0.23, -0.34, 9.53)
        """
        items = response.split()
        return float(items[0])/1000, float(items[1]), float(items[2]), float(items[3])


    def _parseIntAfterTimestamp1(self, response: str) -> int:
        """"Parses the first value after the timestamp and returns it as single int value.
        Example:  _parseIntAfterTimestamp1('96372 108') -> 108
        """
        items = response.split()
        return int(items[1])

    def _parseIntWithTimestamp1(self, response: str) -> Tuple[float, int]:
        """"Parses the timestamp in seconds and the following value and returns them as tuple with a float and an int value.
        Example:  _parseIntWithTimestamp1('96372 108') -> (96.372, 108)
        """
        items = response.split()
        return float(items[0])/1000, int(items[1])

    def _parseIntAfterTimestamp3(self, response: str) -> Tuple[float, int, int, int]:
        """"Parses the first three values after the timestamp and returns them as tuple with 3 int values.
        Example:  _parseIntAfterTimestamp3('96372 -236 348 9759') -> (-236, 348, 9759)
        """
        items = response.split()
        return int(items[1]), int(items[2]), int(items[3])

    def _parseIntWithTimestamp3(self, response: str) -> Tuple[float, int, int, int]:
        """"Parses the time stamp in seconds and the following three values and returns them as tuple with 1 float and 3 int values.
        Example:  _parseIntWithTimestamp3('96372 -236 348 9759') -> (96.372, -236, 348, 9759)
        """
        items = response.split()
        return float(items[0])/1000, int(items[1]), int(items[2]), int(items[3])

    def _parseIntTimestamp(self, response: str) -> int:
        """"Parses the time stamp in milli-seconds and returns it as singe int value.
        Example:  _parseIntTimestamp('96372') -> 96372
        Example:  _parseIntTimestamp('96372 -236 348 9759') -> 96372
        """
        items = response.split()
        return int(items[0])


    def _parseBoolAfterTimestamp1(self, response: str) -> bool:
        """"Parses the first value after the timestamp and returns it as single bool value.
        Example:  _parseBoolAfterTimestamp1('96372 0')  -> False
        Example:  _parseBoolAfterTimestamp1('96372 1')  -> True
        Example:  _parseBoolAfterTimestamp1('96372 42') -> True
        """
        items = response.split()
        return bool(int(items[1]))

    def _parseBoolWithTimestamp1(self, response: str) -> Tuple[float, bool]:
        """"Parses the timestamp in seconds and the following value and returns them as tuple with a float and a bool value.
        Example:  _parseBoolWithTimestamp1('96372 0')  -> (96.372, False)
        Example:  _parseBoolWithTimestamp1('96372 1')  -> (96.372, True)
        Example:  _parseBoolWithTimestamp1('96372 42') -> (96.372, True)
        """
        items = response.split()
        return float(items[0])/1000, bool(int(items[1]))



    def _parseFloatTimestamp(self, response: str) -> float:
        """"Parses the time stamp in seconds and returns it as singe float value.
        Example:  _parseFloatTimestamp('96372') -> 96.372
        Example:  _parseFloatTimestamp('96372 -236 348 9759') -> 96.372
        """
        items = response.split()
        return float(items[0])/1000


    # Methods for the serial port
    
    def _findAndConnectComPort(self):
        '''Opens serial connection to Adafruit Circuit Playground. Takes the first one found. Aborts the main program if none is found.'''
        if (self.comPort is None) or (self.comPort == '') or (self.comPort == 'auto'):
            self._findComPort()

        if self.emuMode == True:
            self._switchToEmulation()
        else:
            self.comPortObj = serial.Serial(self.comPort, self.baudrate, timeout=5) # timeout is for reads
            print(f'Connected to {self.comPortObj.name} with {self.comPortObj.baudrate} baud (bit/second).')
    
    def _findComPort(self) -> None:
        '''Searches COM ports for Adafruit Circuit Playground. Takes the first hit. Aborts the main program if none is found.'''
        print( '=============================================================')
        print(f'cpg_scpi v{__version__}')
        print( 'Searching for serial device with "adafruit" ...')
        x=list(serial.tools.list_ports.grep("adafruit")) # should work on Windows with Adafruit COM-Port driver
        # Try also other names if nothing found
        if len(x)==0:
            print('                            with "playground" ...')
            x=list(serial.tools.list_ports.grep("playground")) # should work on Linux
        if len(x)==0:
            print('                            with "circuit" ...')
            x=list(serial.tools.list_ports.grep("circuit")) # should also work on Linux
        if len(x)==0:
            print('                            with "239A:8011" as VID:PID ...')
            x=list(serial.tools.list_ports.grep("239A:8011")) # should generally work because of VID:PID=239A:8011

        # Now we hopefully have at least one hit.
        if len(x)==0:
            # If not, we switch to emulation mode.
            self.comPort = None
            self.emuMode = True
            print( 'WARNING in cpg_scpi: Could not find any serial port for')
            print( '                     Adafruit Circuit Playground.')
            print( '=============================================================')
            print()
            print( '=============================================================')
            print( 'WILL SWITCH TO EMULATION MODE.')
            self._printCountdown(3)
            print( '=============================================================')
            #sys.exit(1)
        elif len(x)>1:
            self.comPort = x[0].device
            self.emuMode = False
            print(f'WARNING in cpg_scpi: Found {len(x)} Circuit Playgrounds.')
            print(f'                     Will take the one on {self.comPort}.')
            print( '=============================================================')
        else: # len(x)==1
            self.comPort = x[0].device
            self.emuMode = False
            print(f'INFO in cpg_scpi: Found a Circuit Playground on {self.comPort}')
            print( '=============================================================')

    def _printCountdown(self, start: int = 3) -> None:
        for i in range(start, 0, -1):
            print(i, end=" ", flush=True)
            time.sleep(1)
        print('', flush=True)

    # Methods for emulation mode
    
    def _switchToEmulation(self) -> None:
        import random
        self.rndGen_temp  = random.Random(2)
        self.rndVal_temp  = 20.0
        self.rndGen_light = random.Random(3)
        self.rndVal_light = 100
        # self.rndGen_accX  = random.Random(4)
        # self.rndVal_accX  = 0.0
        # self.rndGen_accY  = random.Random(5)
        # self.rndVal_accY  = 0.0
        # self.rndGen_accZ  = random.Random(6)
        # self.rndVal_accZ  = 9.81
        self._accData = (
            (  -0.68,  -0.11,   9.60), (  -0.49,  -0.24,   9.62), (  -0.30,  -0.35,   9.69), (  -0.21,  -0.57,   9.18), (  -0.35,  -0.58,   9.47), (  -0.53,  -0.65,   9.95), (  -0.52,  -0.47,   9.37), (  -0.61,  -0.31,   9.65), (  -0.48,  -0.30,   9.50), (  -0.47,  -0.18,   9.59), (  -0.38,  -0.31,   9.68), (  -0.34,  -0.60,   9.60), (  -0.34,  -0.56,   9.39), (  -0.44,  -0.59,   9.77), (  -0.49,  -0.19,   9.46), (  -0.48,  -0.47,   9.47), (  -0.36,  -0.57,   9.77), (  -0.46,  -0.47,   9.46), (  -0.51,  -0.56,   9.76), (  -0.42,  -0.37,   9.49), (  -0.67,  -0.21,   9.47), (  -0.63,  -0.44,   9.52), (  -0.59,  -0.49,   9.80), (  -0.48,  -0.67,   9.97), (  -0.26,  -0.80,   9.48), (  -0.60,  -0.16,  10.08), (  -0.66,  -0.38,   9.58), (  -0.64,  -0.63,   8.96), (  -0.83,  -0.34,   9.51), (  -0.80,  -0.40,   9.53), (  -0.79,  -0.48,   8.94), (  -0.88,  -0.33,   9.45), (  -0.69,  -0.21,   9.87), (  -0.60,  -0.30,   9.45), (  -0.75,  -0.12,   9.97), (  -0.68,  -0.46,   8.99), (  -0.87,  -0.39,  10.00), (  -0.85,  -0.41,   9.37), (  -0.62,  -0.55,   9.68), (  -0.57,  -0.40,   9.73), (  -0.79,  -0.07,   9.50), (  -0.65,  -0.08,   9.45), (  -0.75,  -0.41,   9.58), (  -0.70,  -0.37,   9.37), (  -0.86,  -0.25,   9.39), (  -1.05,  -0.29,   9.64), (  -1.01,  -0.18,   9.70), (  -0.91,  -0.12,   9.47), (  -0.84,  -0.31,   9.64), (  -0.72,  -0.48,   9.38), (  -0.77,  -0.48,   9.92), (  -0.49,  -0.66,   9.57), (  -0.59,  -0.56,   9.58), (  -0.50,  -0.61,   9.40), (  -0.73,  -0.49,   9.32), (  -0.86,   0.00,   8.93), (  -0.92,  -0.27,   9.90), (  -0.71,  -0.43,   9.76), (  -0.60,  -0.64,   9.59), (  -0.80,  -0.38,   9.76), (  -0.75,  -0.36,   9.24), (  -0.70,  -0.43,   9.52), (  -0.69,  -0.46,   9.65), (  -0.67,  -0.41,   9.36), (  -0.83,  -0.70,   9.97), (  -0.82,  -0.28,   9.51), (  -0.86,  -0.40,  10.14), (  -0.77,  -0.30,   9.48), (  -0.80,  -0.42,   9.72), (  -0.77,  -0.39,   9.78), (  -0.89,   0.11,   9.58), (  -0.82,  -0.06,   9.52), (  -0.67,   0.34,   9.30), (  -0.85,   0.04,   9.63), (  -0.82,   0.51,   9.77), (  -0.97,   0.59,   9.79), (  -0.99,   0.57,   9.38), (  -0.67,   0.91,   9.54), (  -0.68,   1.08,   9.28), (  -0.86,   1.67,   9.45), (  -0.78,   1.84,   9.35), (  -0.67,   1.47,   9.53), (  -0.81,   2.01,   9.23), (  -0.54,   2.25,   9.00), (  -0.86,   2.55,   9.67), (  -0.80,   2.75,   8.72), (  -0.73,   2.68,   9.04), (  -0.86,   3.34,   9.05), (  -0.89,   3.28,   9.16), (  -0.75,   3.17,   8.62), (  -0.75,   2.99,   8.79), (  -0.72,   3.48,   8.77), (  -0.87,   3.82,   8.89), (  -0.73,   3.79,   8.54), (  -0.67,   4.31,   7.94), (  -0.70,   4.29,   8.17), (  -0.77,   4.68,   7.94), (  -0.68,   4.82,   8.29), (  -0.80,   5.21,   7.78), (  -0.72,   5.21,   7.59), (  -0.74,   5.44,   7.55), (  -0.78,   5.82,   7.41), (  -0.80,   5.81,   7.23), (  -0.71,   5.84,   7.11), (  -0.73,   5.98,   7.02), (  -0.72,   6.09,   6.72), (  -0.83,   6.56,   7.17), (  -0.76,   6.31,   6.96), (  -0.80,   6.64,   7.12), (  -0.83,   7.17,   7.37), (  -0.74,   7.18,   6.04), (  -0.79,   7.27,   5.98), (  -0.74,   7.11,   5.82), (  -0.74,   7.32,   5.61), (  -0.77,   7.68,   5.72), (  -0.79,   8.13,   5.64), (  -0.76,   8.23,   4.63), (  -0.65,   8.12,   4.65), (  -0.57,   7.90,   4.35), (  -0.83,   8.39,   4.20), (  -0.79,   8.56,   4.46), (  -0.79,   8.53,   3.96), (  -0.64,   8.95,   3.96), (  -0.68,   8.64,   3.74), (  -0.70,   8.92,   3.10), (  -0.68,   8.76,   2.98), (  -0.70,   9.14,   3.08), (  -0.61,   9.00,   2.83), (  -0.60,   8.68,   2.40), (  -0.71,   9.34,   2.40), (  -0.69,   9.32,   2.47), (  -0.58,   9.11,   1.86), (  -0.69,   9.49,   2.14), (  -0.57,   9.01,   1.45), (  -0.52,   9.16,   0.99), (  -0.57,   9.84,   1.13), (  -0.59,   9.08,   0.77), (  -0.38,   9.54,   0.81), (  -0.49,   9.77,   0.06), (  -0.45,   9.54,  -0.31), (  -0.43,   9.29,   0.17), (  -0.47,   9.27,  -0.53), (  -0.50,   9.34,  -0.43), (  -0.50,   8.91,  -0.43), (  -0.36,   9.79,  -0.60), (  -0.37,   9.91,  -0.44), (  -0.38,   9.63,  -0.55), (  -0.40,   9.21,  -0.71), (  -0.34,   8.80,  -1.03), (  -0.43,   9.51,  -1.65), (  -0.26,   8.86,  -1.54), (  -0.43,   9.90,  -1.31), (  -0.33,   9.39,  -1.69), (  -0.29,   9.24,  -1.41), (  -0.34,   9.42,  -2.05), (  -0.27,   9.03,  -1.52), (  -0.41,   9.17,  -2.15), (  -0.47,   9.50,  -2.33), (  -0.44,   8.70,  -1.96), (  -0.38,   9.35,  -2.16), (  -0.28,   9.20,  -2.48), (  -0.38,   9.84,  -2.32), (  -0.14,   9.21,  -2.51), (  -0.20,   9.22,  -2.21), (  -0.19,   8.99,  -2.57), (  -0.21,   9.22,  -2.45), (  -0.17,   8.99,  -2.32), (  -0.28,   9.71,  -2.83), (  -0.11,   9.17,  -2.45), (  -0.12,   8.56,  -2.03), (  -0.35,   9.56,  -3.03), (   0.01,   9.22,  -2.48), (  -0.15,   9.22,  -2.78), (  -0.06,   9.11,  -3.73), (  -0.04,   8.65,  -3.90), (  -0.08,   9.13,  -4.21), (   0.06,   8.17,  -4.44), (   0.23,   7.81,  -4.30), (   0.05,   8.79,  -4.62), (   0.16,   7.94,  -4.53), (   0.04,   8.13,  -4.90), (   0.26,   7.58,  -4.55), (   0.11,   8.23,  -5.80), (   0.12,   7.99,  -5.44), (   0.17,   8.47,  -5.58), (   0.29,   7.48,  -5.68), (   0.11,   7.53,  -5.94), (   0.12,   8.03,  -5.87), (   0.27,   7.21,  -6.08), (   0.09,   6.85,  -6.78), (   0.27,   6.26,  -6.26), (   0.21,   7.24,  -6.39), (   0.12,   8.23,  -6.54), (   0.27,   6.87,  -6.84), (   0.49,   6.06,  -6.95), (   0.27,   6.62,  -7.16), (   0.22,   6.45,  -7.15), (   0.23,   6.78,  -7.24), (   0.46,   6.26,  -7.60), (   0.11,   5.66,  -7.84), (   0.73,   5.61,  -7.80), (   0.43,   5.87,  -7.90), (   0.36,   5.27,  -7.88), (   0.62,   5.08,  -8.32), (   0.59,   5.12,  -8.28), (   0.57,   4.45,  -8.35), (   0.53,   4.77,  -8.62), (   0.49,   4.66,  -8.37), (   0.65,   4.22,  -8.71), (   0.65,   4.33,  -8.83), (   0.67,   3.93,  -8.35), (   0.77,   3.63,  -9.35), (   0.62,   3.46,  -9.05), (   0.60,   3.48,  -9.01), (   0.36,   3.16,  -9.23), (   0.72,   2.53,  -9.18), (   0.85,   2.42,  -9.08), (   0.81,   2.37,  -9.61), (   0.63,   2.17,  -9.34), (   0.56,   1.92,  -9.32), (   0.47,   2.04,  -9.39), (   0.38,   1.89,  -9.57), (   0.45,   1.29,  -9.61), (   0.24,   1.64,  -9.92), (   0.18,   1.19,  -9.48), (   0.35,   1.02,  -9.93), (   0.14,   0.77,  -9.74), (   0.13,   0.77,  -9.68), (   0.21,   0.10,  -9.90), (   0.11,   0.33,  -9.70), (   0.11,   0.40,  -9.90), (   0.05,   0.02,  -9.78), (   0.05,   0.31,  -9.61), (   0.11,  -0.05, -10.03), (   0.03,   0.10,  -9.85), (   0.11,   0.00,  -9.85), (   0.09,  -0.11,  -9.47), (  -0.02,  -0.06,  -9.92), (  -0.10,   0.08,  -9.58), (   0.07,  -0.25,  -9.78), (  -0.03,   0.24,  -9.86), (   0.00,  -0.15,  -9.90), (   0.06,  -0.37, -10.00), (   0.04,   0.36,  -9.80), (  -0.11,   0.13,  -9.48), (   0.01,   0.10,  -9.63), (  -0.11,   0.14, -10.08), (  -0.02,   0.14,  -9.81), (  -0.08,   0.15,  -9.85), (  -0.04,   0.06,  -9.60), (   0.07,   0.48,  -9.56), (   0.08,   0.39,  -9.77), (   0.01,   0.34,  -9.97), (   0.12,   0.38,  -9.74), (   0.04,   0.53,  -9.83), (   0.02,   0.15,  -9.64), (   0.07,   0.43,  -9.67), (   0.02,   0.42,  -9.91), (   0.06,   0.33,  -9.58), (   0.14,   0.13,  -9.91), (   0.10,   0.07,  -9.92), (  -0.03,  -0.18,  -9.52), (   0.11,  -0.57,  -9.80), (   0.15,  -0.50,  -9.72), (   0.18,  -1.09,  -9.61), (   0.15,  -1.78,  -9.30), (   0.16,  -1.66,  -9.90), (   0.16,  -1.97,  -9.76), (   0.23,  -1.99,  -9.52), (   0.15,  -2.36,  -9.30), (   0.15,  -2.62,  -9.44), (   0.15,  -2.61,  -9.23), (   0.18,  -3.01,  -9.39), (   0.19,  -2.99,  -8.92), (   0.29,  -3.28,  -9.14), (   0.20,  -3.44,  -9.32), (   0.16,  -3.98,  -9.07), (   0.18,  -4.26,  -8.77), (   0.26,  -4.42,  -8.86), (   0.18,  -4.83,  -8.34), (   0.37,  -4.84,  -8.14), (   0.37,  -5.08,  -8.22), (   0.45,  -5.04,  -8.14), (   0.50,  -5.17,  -8.20), (   0.43,  -5.59,  -8.11), (   0.51,  -5.58,  -7.99), (   0.47,  -5.68,  -7.93), (   0.52,  -5.71,  -7.61), (   0.56,  -6.14,  -7.62), (   0.34,  -6.42,  -7.42), (   0.50,  -6.19,  -7.60), (   0.57,  -6.25,  -7.73), (   0.32,  -6.44,  -6.85), (   0.43,  -6.63,  -6.89), (   0.34,  -7.46,  -7.31), (   0.25,  -7.40,  -6.44), (   0.42,  -7.28,  -6.52), (   0.24,  -7.69,  -6.21), (   0.34,  -7.48,  -5.75), (   0.38,  -7.27,  -5.23), (   0.19,  -7.97,  -5.02), (   0.00,  -8.95,  -4.87), (   0.03,  -8.86,  -4.26), (   0.10,  -8.96,  -3.65), (   0.11,  -8.89,  -3.14), (   0.03,  -9.36,  -3.30), (   0.03,  -9.13,  -3.32), (   0.13,  -9.02,  -2.28), (   0.00,  -9.56,  -2.18), (   0.05,  -9.27,  -1.71), (   0.01,  -9.73,  -1.70), (   0.15,  -9.31,  -1.64), (   0.08,  -9.53,  -1.11), (   0.06,  -9.77,  -0.93), (   0.12,  -9.85,  -1.27), (  -0.02, -10.17,  -1.02), (   0.21,  -9.34,  -0.53), (   0.08, -10.28,  -0.69), (   0.14,  -9.65,  -0.26), (   0.22,  -9.61,  -0.51), (   0.09, -10.12,  -0.47), (   0.18,  -9.38,  -0.62), (   0.11,  -9.46,  -0.09), (   0.14,  -9.34,  -0.20), (   0.20,  -9.31,  -0.31), (   0.12,  -9.89,  -0.13), (   0.14, -10.44,   0.60), (   0.11,  -9.53,   0.03), (   0.10,  -9.50,   0.05), (   0.40,  -9.57,  -0.30), (   0.25,  -9.77,  -0.01), (  -0.01,  -9.87,   0.15), (   0.12,  -9.32,  -0.11), (   0.14,  -9.59,  -0.23), (  -0.01,  -9.55,  -0.01), (   0.00,  -9.67,  -0.16), (   0.01,  -9.50,  -0.38), (   0.02,  -9.50,  -0.25), (  -0.01,  -9.39,  -0.14), (  -0.20,  -9.83,  -0.27), (  -0.18,  -9.55,  -0.24), (  -0.13,  -9.45,  -0.30), (  -0.04,  -9.48,  -0.21), (  -0.11,  -9.65,  -0.25), (  -0.14,  -9.50,  -0.14), (  -0.11,  -9.75,  -0.30), (  -0.16,  -9.67,  -0.31), (  -0.01,  -9.44,  -0.19), (  -0.10,  -9.54,  -0.23), (  -0.26,  -9.56,  -0.34), (  -0.23,  -9.62,  -0.24), (  -0.23,  -9.66,  -0.29), (  -0.15,  -9.45,  -0.20), (  -0.25,  -9.76,   0.04), (  -0.18,  -9.78,   0.10), (  -0.29,  -9.64,   0.22), (  -0.20,  -9.42,   0.30), (  -0.40,  -9.94,   0.57), (  -0.34,  -9.71,   0.96), (  -0.09,  -9.42,   0.98), (  -0.16,  -9.12,   1.35), (   0.06,  -9.66,   1.71), (  -0.40,  -9.74,   2.04), (  -0.33,  -9.13,   1.69), (  -0.34,  -9.52,   2.17), (  -0.03,  -9.00,   2.68), (   0.06,  -9.13,   3.26), (   0.39,  -8.50,   3.91), (  -0.03,  -9.17,   3.76), (  -0.14,  -8.48,   4.38), (   0.33,  -8.24,   4.49), (   0.26,  -8.34,   4.79), (   0.05,  -8.34,   5.03), (   0.12,  -7.88,   5.33), (   0.29,  -7.69,   5.51), (   0.20,  -7.37,   5.59), (   0.11,  -7.43,   6.03), (   0.23,  -7.12,   6.39), (   0.09,  -6.94,   6.80), (   0.16,  -6.01,   7.00), (   0.22,  -5.94,   8.20), (   0.29,  -5.05,   7.83), (   0.26,  -4.53,   8.38), (   0.42,  -4.57,   8.83), (   0.29,  -3.33,   8.66), (   0.28,  -3.80,   9.14), (   0.19,  -3.13,   9.01), (   0.11,  -3.15,   8.87), (   0.12,  -2.66,   9.22), (  -0.01,  -2.50,   8.84), (   0.11,  -2.35,   9.26), (   0.05,  -1.43,   9.32), (   0.04,  -1.77,   9.65), (   0.02,  -1.18,   9.72), (   0.09,  -1.34,   9.73), (  -0.15,  -0.59,   9.39), (   0.09,  -1.08,   9.52), (  -0.12,  -0.48,   9.61), (  -0.33,  -0.22,   9.63), (  -0.28,  -0.17,   9.95), (  -0.26,   0.05,   9.52), (  -0.34,  -0.23,   9.26), (  -0.54,   0.06,   9.47), (  -0.56,   0.29,   9.60), (  -0.51,   0.34,   9.41), (  -0.40,   0.28,   9.68), (  -0.55,   0.40,   9.35), (  -0.47,   0.68,   9.41), (  -0.37,   0.55,   9.45), (  -0.34,   0.53,   9.49), (  -0.39,   0.45,   9.42), (  -0.33,   0.47,   9.77), (  -0.32,   0.37,   9.60), (  -0.34,   0.26,   9.67), (  -0.32,   0.36,   9.40), (  -0.29,   0.41,   9.43), (  -0.58,   0.86,  10.27), (  -0.55,   0.13,   9.39), (  -0.53,   0.33,   9.62), (  -0.60,   0.22,   9.78), (  -0.58,   0.57,   9.16), (  -0.67,   0.56,   9.94), (  -0.50,   0.09,   9.36), (  -0.61,   0.38,   9.26), (  -0.72,   0.69,   9.66), (  -0.62,   0.45,   9.79), (  -0.61,   0.44,   9.59), (  -0.60,   0.45,   9.23), (  -0.77,   0.55,   9.58), (  -0.77,   0.54,   9.33), (  -0.76,   0.60,   9.52), (  -0.76,   0.54,   9.54), (  -0.76,   0.53,   9.59), (  -0.58,   0.34,   9.28), (  -0.66,   0.78,   9.02), (  -0.73,   0.71,   9.26), (  -0.62,   0.43,   9.31), (  -0.76,   0.45,   9.45), (  -0.71,   0.48,   9.49), (  -0.75,   0.81,   9.62), (  -0.64,   0.89,   9.29), (  -0.63,   0.68,   9.51), (  -0.62,   0.63,   9.30), (  -0.75,   0.79,   9.58), (  -0.72,   0.82,   9.59), (  -0.56,   0.43,   9.34), (  -0.63,   0.59,   9.51), (  -0.69,   0.70,   9.92), (  -0.67,   0.77,   9.52), (  -0.60,   0.49,   9.45), (  -0.66,   0.70,   9.42), (  -0.74,   0.94,   9.72), (  -0.71,   0.72,   9.64), (  -0.65,   0.80,   9.24), (  -0.63,   0.45,   9.22), (  -1.02,   1.02,   9.89), (  -0.98,   0.59,   9.21), (  -1.09,   0.88,   9.16), (  -1.19,   0.44,   9.82), (  -1.17,   0.66,   8.86), (  -1.32,   0.19,   9.52), (  -1.59,   0.50,  10.20), (  -1.59,   0.83,   8.99), (  -1.83,   0.75,   9.22), (  -2.23,   0.65,   9.86), (  -2.49,   0.75,   8.99), (  -2.84,   1.01,   8.97), (  -3.10,   0.57,   9.12), (  -3.19,   0.19,   8.99), (  -3.45,   0.24,   8.41), (  -3.91,   0.47,   8.19), (  -4.03,   0.23,   7.87), (  -4.72,   0.36,   8.70), (  -4.83,   0.32,   7.62), (  -5.18,   0.55,   7.65), (  -5.64,   0.40,   8.44), (  -5.71,   0.34,   7.25), (  -6.24,   0.82,   6.16), (  -6.74,   1.31,   6.40), (  -6.75,   1.12,   5.36), (  -7.11,   1.20,   5.93), (  -7.17,   0.99,   5.48), (  -7.53,   1.40,   5.72), (  -7.76,   1.01,   6.22), (  -7.97,   0.74,   5.58), (  -8.19,   0.34,   4.84), (  -8.31,   0.75,   3.48), (  -8.57,   0.57,   4.21), (  -8.54,   0.76,   2.98), (  -8.53,   0.18,   2.64), (  -8.93,   0.72,   3.30), (  -9.00,   0.69,   2.61), (  -9.02,   0.97,   2.90), (  -8.99,   0.50,   2.27), (  -9.03,   0.36,   1.72), (  -9.34,   0.80,   2.83), (  -9.33,   0.27,   2.47), (  -9.34,   0.32,   1.47), (  -9.54,   0.63,   1.40), (  -9.41,   0.19,   1.04), (  -9.28,   0.12,   1.51), (  -9.05,  -0.06,   0.84), (  -9.09,  -0.24,   0.69), (  -9.12,   0.11,   0.78), (  -9.40,   0.17,   0.64), (  -9.49,   0.11,   1.25), (  -9.32,   0.11,   0.06), (  -9.32,   0.55,   0.68), (  -9.42,   0.16,   0.89), (  -9.41,   0.18,  -0.18), (  -9.53,   0.44,  -0.35), (  -9.25,   0.01,  -0.67), (  -9.31,  -0.06,   0.30), (  -9.64,   0.63,   0.64), (  -9.26,   0.16,  -0.02), (  -9.71,   0.20,   0.77), (  -9.49,   0.07,   0.13), (  -9.25,  -0.64,   0.30), (  -9.78,   0.69,   0.72), (  -9.52,   0.00,   0.75), (  -9.28,  -0.09,   0.00), (  -9.41,   0.10,   0.20), (  -9.51,   0.10,   1.02), (  -9.47,   0.13,   0.31), (  -9.55,  -0.03,   0.18), (  -9.49,   0.11,   0.11), (  -9.66,   0.37,   0.73), (  -9.46,   0.22,   0.34), (  -9.43,   0.24,  -0.04), (  -9.49,   0.08,   0.52), (  -9.40,  -0.34,   0.80), (  -9.40,   0.01,   0.74), (  -9.50,   0.22,  -0.08), (  -9.57,   0.49,   0.17), (  -9.56,   0.32,   0.33), (  -9.49,   0.23,   0.14), (  -9.55,   0.11,   0.45), (  -9.43,   0.18,   0.20), (  -9.47,   0.10,   0.49), (  -9.42,   0.09,   0.30), (  -9.48,   0.29,   0.26), (  -9.69,   0.37,   0.39), (  -9.50,   0.15,   0.40), (  -9.50,   0.15,   0.54), (  -9.45,   0.27,   0.57), (  -9.38,   0.15,  -0.15), (  -9.53,   0.22,  -0.11), (  -9.65,  -0.34,   1.07), (  -9.51,   0.14,  -0.31), (  -9.39,  -0.07,   0.93), (  -9.73,  -0.30,   1.87), (  -9.59,  -0.29,   0.10), (  -9.54,  -0.94,   0.47), (  -9.77,   0.50,   1.02), (  -9.46,  -0.57,   0.32), (  -9.65,  -0.08,  -0.71), (  -9.33,  -0.54,   0.36), (  -9.79,   0.65,  -0.22), (  -9.29,   0.57,  -1.84), (  -9.59,   0.24,  -0.50), (  -9.47,  -0.24,  -0.99), (  -9.55,   1.05,  -1.25), (  -8.98,   0.11,  -2.33), (  -9.59,   0.68,  -0.25), (  -9.24,   0.79,  -2.96), (  -9.07,   0.11,  -1.91), (  -9.06,   0.94,  -2.89), (  -9.16,   0.21,  -2.04), (  -8.99,   0.23,  -2.56), (  -9.04,   1.06,  -3.06), (  -8.99,   0.05,  -3.56), (  -8.30,   1.27,  -5.14), (  -8.32,   0.76,  -3.65), (  -7.76,   1.53,  -4.53), (  -8.30,   2.12,  -5.07), (  -7.12,   0.94,  -6.61), (  -6.92,   1.23,  -6.28), (  -6.63,   1.29,  -6.70), (  -6.55,   0.49,  -7.67), (  -5.84,   0.81,  -6.73), (  -5.72,  -0.45,  -9.95), (  -5.40,   0.04,  -7.92), (  -4.95,   0.55,  -8.08), (  -4.59,  -0.58,  -9.52), (  -4.42,   0.21,  -7.75), (  -4.38,   0.38,  -9.60), (  -4.24,  -0.28,  -8.23), (  -3.21,  -1.26,  -9.44), (  -3.47,  -0.07,  -9.69), (  -2.50,  -0.68,  -9.37), (  -2.08,   0.23,  -8.74), (  -1.59,  -0.46,  -9.65), (  -1.34,  -0.92, -10.42), (  -0.99,  -1.01,  -9.62), (  -0.55,  -0.54, -10.18), (  -0.52,  -0.64, -10.66), (  -0.11,  -0.11,  -8.76), (   0.30,  -0.24,  -9.94), (   0.53,  -0.21,  -9.60), (   0.54,  -1.25, -11.06), (   0.58,   0.02, -11.12), (   0.75,  -0.51,  -9.65), (   0.80,  -0.27, -10.21), (   0.74,  -0.29,  -9.89), (   0.69,  -0.15,  -9.74), (   0.64,  -0.47,  -9.72), (   0.57,  -0.06,  -9.80), (   0.57,  -0.49,  -9.46), (   0.50,   0.11,  -9.77), (   0.50,  -0.73,  -9.67), (   0.52,  -0.09,  -9.98), (   0.47,  -0.57,  -9.49), (   0.45,  -0.39,  -9.57), (   0.49,  -0.22,  -9.51), (   0.49,  -0.34,  -9.75), (   0.53,  -0.57, -10.03), (   0.45,  -0.37,  -9.61), (   0.44,  -0.47,  -9.78), (   0.46,  -0.17,  -9.67), (   0.53,  -0.56,  -9.54), (   0.47,  -0.52,  -9.73), (   0.58,   0.05,  -9.52), (   0.58,  -0.21,  -9.79), (   0.60,  -0.69,  -9.79), (   0.54,  -0.37, -10.16), (   0.57,  -0.48,  -9.68), (   0.60,  -0.39,  -9.67), (   0.71,  -0.10,  -9.52), (   0.60,  -0.63,  -9.52), (   0.66,  -0.45,  -9.79), (   0.62,  -0.10,  -9.55), (   0.75,  -0.11,  -9.29), (   0.80,  -0.52,  -9.88), (   0.85,  -0.37,  -9.53), (   0.71,  -0.25,  -9.58), (   0.80,  -0.48, -10.26), (   0.75,  -0.80, -10.06), (   0.84,  -0.50, -10.12), (   0.86,  -0.57,  -9.66), (   0.94,   0.07,  -9.91), (   0.91,  -0.58,  -9.74), (   0.98,   0.21,  -9.57), (   1.05,  -0.32,  -9.21), (   1.06,  -0.26,  -9.45), (   1.21,  -0.08, -10.18), (   1.24,  -0.22,  -9.60), (   1.43,  -0.41,  -9.99), (   1.43,  -0.26, -10.14), (   1.49,  -0.05,  -9.50), (   1.67,  -0.30,  -9.51), (   1.80,  -0.14,  -9.42), (   1.94,  -0.30,  -9.46), (   2.13,  -0.04, -10.32), (   2.18,  -0.21,  -9.00), (   2.45,  -0.11,  -9.62), (   2.66,  -0.98,  -9.99), (   2.83,  -0.94,  -8.78), (   3.06,  -0.15,  -8.90), (   3.34,  -0.47,  -8.21), (   3.68,  -0.67,  -8.54), (   4.06,  -1.24, -10.02), (   4.05,  -1.03,  -8.27), (   4.30,  -0.49,  -8.42), (   4.64,  -1.27,  -8.09), (   4.86,  -1.48,  -9.12), (   4.85,  -0.87,  -7.92), (   5.62,  -1.35,  -7.90), (   5.91,  -1.55,  -7.34), (   6.35,  -0.92,  -8.00), (   6.62,  -1.44,  -7.42), (   6.85,  -1.32,  -6.99), (   7.15,  -2.29,  -7.17), (   7.39,  -0.57,  -6.40), (   7.48,  -2.04,  -6.11), (   7.77,  -1.80,  -6.71), (   7.92,  -1.02,  -5.07), (   8.39,  -2.00,  -6.14), (   8.52,  -2.33,  -4.90), (   8.72,  -1.60,  -4.90), (   8.91,  -1.65,  -4.75), (   9.11,  -2.71,  -4.76), (   9.20,  -2.31,  -4.16), (   9.22,  -1.77,  -4.31), (   9.12,  -2.06,  -2.38), (   9.49,  -1.79,  -3.65), (   9.53,  -2.08,  -3.72), (   9.51,  -2.38,  -2.12), (   9.71,  -1.37,  -3.40), (   9.63,  -1.84,  -3.53), (   9.45,  -2.14,  -2.33), (   9.77,  -1.29,  -1.68), (   9.94,  -1.81,  -2.78), (   9.74,  -1.25,  -1.24), (   9.76,  -2.05,  -1.67), (  10.00,  -1.83,  -1.74), (   9.95,  -1.91,  -0.77), (  10.15,  -1.86,  -1.98), (  10.05,  -1.11,  -0.99), (  10.08,  -1.70,  -1.16), (   9.72,  -1.64,  -0.35), (  10.06,  -0.96,  -0.48), (  10.06,  -2.11,  -0.94), (  10.09,  -1.63,  -0.88), (  10.11,  -1.15,  -0.35), (  10.07,  -1.80,  -0.06), (  10.27,  -0.62,   0.65), (  10.30,  -1.92,  -0.88), (  10.07,  -1.25,  -0.59), (  10.05,  -1.53,  -0.43), (   9.79,  -1.02,   0.71), (  10.16,  -1.48,   0.07), (  10.04,  -1.52,  -0.40), (  10.06,  -0.54,   0.81), (  10.13,  -0.97,   0.08), (  10.24,  -1.61,  -0.35), (   9.96,  -1.25,   0.09), (   9.90,  -1.27,   0.64), (  10.11,  -1.47,  -0.51), (  10.16,  -1.15,  -0.19), (  10.06,  -0.94,   0.04), (  10.03,  -1.09,   0.28), (   9.95,  -1.05,   0.55), (  10.14,  -1.52,   0.03), (  10.08,  -1.30,  -0.31), (  10.12,  -0.58,   0.56), (  10.11,  -0.81,   0.12), (  10.12,  -1.37,   0.16), (  10.25,  -1.65,  -0.12), (  10.11,  -1.23,   0.06), (  10.19,  -0.69,  -0.07), (  10.01,  -1.44,   0.00), (  10.03,  -0.65,   0.03), (  10.13,  -1.58,  -0.11), (  10.01,  -0.91,   0.29), (  10.06,  -1.50,  -0.23), (  10.04,  -1.45,   0.23), (  10.24,  -1.57,  -0.36), (   9.95,  -0.99,   0.28), (  10.02,  -1.10,  -0.43), (  10.14,  -1.05,  -0.23), (   9.98,  -1.69,  -0.07), (  10.16,  -1.02,  -0.11), (  10.01,  -1.42,   0.12), (   9.98,  -1.15,   0.03), (   9.99,  -0.98,   0.10), (  10.13,  -1.13,  -0.08), (  10.21,  -1.53,   0.44), (   9.99,  -1.13,   0.33), (   9.98,  -1.23,   0.97), (  10.05,  -1.35,   0.23), (   9.90,  -1.25,   0.18), (  10.13,  -1.36,   0.37), (   9.97,  -1.33,   0.65), (   9.97,  -1.37,   0.35), (  10.01,  -1.41,  -0.02), (  10.21,  -1.76,  -0.13), (  10.03,  -1.25,   0.79), (  10.06,  -1.90,  -0.12), (   9.92,  -1.36,   0.56), (  10.16,  -1.50,   0.19), (  10.12,  -1.27,   0.15), (  10.01,  -1.66,   0.29), (  10.06,  -1.28,   0.42), (   9.97,  -1.32,   1.01), (  10.02,  -1.86,  -0.05), (  10.11,  -1.27,   0.55), (  10.15,  -1.14,   0.29), (  10.38,  -2.06,   0.34), (  10.02,  -1.98,   0.57), (   9.95,  -2.15,   0.21), (   9.95,  -1.45,   1.02), (  10.05,  -1.26,   0.69), (   9.77,  -2.42,   0.50), (   9.90,  -2.16,   0.36), (  10.09,  -2.15,   0.59), (   9.64,  -1.71,   0.74), (   9.73,  -2.03,  -0.08), (   9.87,  -1.74,   0.45), (   9.65,  -2.39,   0.65), (  10.04,  -1.73,   0.62), (  10.01,  -2.78,   0.75), (  10.02,  -1.81,   0.32), (   9.63,  -2.29,   0.56), (  10.17,  -2.02,   1.24), (  10.01,  -2.11,   0.62), (   9.97,  -2.11,   1.56), (  10.13,  -1.83,   1.82), (   9.40,  -1.83,   0.87), (   9.54,  -1.17,   3.47), (   9.90,  -2.50,   2.35), (   9.88,  -2.19,   2.57), (  10.05,  -2.34,   3.67), (   8.35,  -1.86,   2.62), (   8.36,  -2.46,   3.74), (   8.87,  -3.15,   4.59), (   8.21,  -2.69,   4.99), (   8.07,  -1.65,   5.72), (   7.90,  -2.39,   6.18), (   7.26,  -0.92,   6.54), (   7.32,  -1.24,   6.75), (   6.39,  -1.19,   6.63), (   6.28,  -0.38,   7.67), (   6.22,  -0.89,   7.85), (   5.46,  -0.71,   7.85), (   5.48,  -0.90,   8.88), (   4.77,  -0.97,   8.14), (   4.75,  -0.12,   8.99), (   4.49,  -0.40,   8.69), (   3.53,  -1.12,   8.61), (   3.30,   0.43,   9.41), (   2.39,  -0.11,   8.90), (   2.36,  -0.67,   9.13), (   1.80,  -0.12,   9.02), (   1.51,  -0.26,   9.09), (   1.34,  -0.44,   9.57), (   1.00,   0.55,   9.31), (   1.02,  -0.18,   9.12), (   1.03,   0.18,  10.04), (   1.03,   0.37,   9.28), (  -0.12,   0.66,   9.04), (  -0.09,   0.19,   9.23), (   0.36,   0.20,  10.69), (  -0.22,   0.06,   9.30), (  -0.53,   0.12,   8.77), (  -0.25,   0.83,  10.97), (  -0.52,   0.16,   9.22), (  -0.45,   1.12,   9.61), (  -0.13,   0.46,   9.93), (  -0.66,   0.17,   8.79), (  -0.57,   1.23,   9.87), (  -0.68,   0.65,   9.04), (  -0.30,   0.28,   9.83), (  -0.43,   0.47,   9.35), (  -0.32,   0.66,   9.52), (  -0.23,   0.57,   9.73), (  -0.43,   0.56,   9.50), (  -0.62,   0.34,   9.48), (  -0.48,   0.30,   9.68), (  -0.59,   0.41,   9.48), (  -0.51,   0.42,   9.87), (  -0.63,  -0.08,   9.37), (  -0.97,   0.44,   9.00), (  -0.81,   0.72,   9.79), (  -0.77,   0.34,   9.07), (  -0.73,   0.33,   9.51), (  -1.05,   0.36,   9.46), (  -0.64,   0.07,   9.40), (  -0.80,   0.53,   9.44), (  -0.78,  -0.08,   9.15), (  -1.01,   0.47,   9.35), (  -0.93,   0.18,   9.13), (  -0.90,   0.30,   9.50), (  -0.87,   0.43,   9.50), (  -1.06,   0.18,   9.22), (  -0.91,   0.17,   9.51), (  -0.91,   0.46,   9.67), (  -0.70,  -0.07,   9.79), (  -1.13,   0.26,   9.50), (  -1.07,   0.40,   9.61), (  -1.00,  -0.11,   9.29), (  -1.12,   0.40,   9.38), (  -0.90,   0.07,   9.67), (  -1.07,  -0.13,   9.12), (  -1.04,   0.09,   9.49), (  -0.87,   0.17,   9.47), (  -0.94,   0.23,   9.67), (  -0.89,  -0.07,   9.82), (  -1.08,  -0.26,   9.22), (  -0.84,   0.01,   9.58), (  -1.14,  -0.02,   9.41), (  -0.97,  -0.18,   9.54), (  -1.09,   0.05,   9.38), (  -1.02,   0.27,   9.44), (  -0.93,   0.12,   9.90), (  -1.01,  -0.25,   9.22), (  -0.89,   0.11,   9.50), (  -1.03,   0.34,   9.65), (  -0.96,   0.09,   9.64), (  -1.01,   0.08,   9.58), (  -1.05,   0.02,   9.58), (  -1.13,   0.15,   9.41), (  -0.93,   0.20,   9.56), (  -1.02,  -0.11,   9.35), (  -1.11,   0.11,   9.55), (  -0.86,   0.19,   9.63), (  -0.77,   0.41,   9.24), (  -1.03,  -0.13,   9.73), (  -1.05,  -0.02,   9.46), (  -0.80,   0.12,   9.84), (  -0.83,  -0.01,   9.80), (  -0.75,  -0.52,   9.42), (  -1.22,   0.60,   9.39), (  -0.98,  -0.45,   9.61), (  -1.19,   0.05,   9.22), (  -0.85,   0.28,   9.64), (  -1.28,   0.11,   9.57), (  -1.24,  -0.38,   9.52), (  -0.93,  -0.11,   9.71), (  -1.15,  -0.17,   9.25), (  -1.28,  -0.39,   9.51), (  -1.14,  -0.18,   9.45), (  -1.31,  -0.34,   9.22), (  -1.27,  -0.28,   9.19), (  -0.87,  -0.46,  10.04), (  -1.22,  -0.32,   9.43), (  -1.23,  -0.26,   9.18), (  -1.38,  -0.32,   9.45), (  -1.27,  -0.22,   9.49), (  -1.11,  -0.34,   9.57), (  -1.04,  -0.18,   9.61), (  -1.21,  -0.12,   9.46), (  -1.26,  -0.34,   9.43), (  -1.08,  -0.04,   9.47), (  -1.08,  -0.09,   9.60), (  -1.21,  -0.11,   9.59), (  -1.10,   0.28,   9.27), (  -1.19,  -0.44,   9.51), (  -1.14,   0.11,   9.46), (  -1.26,  -0.26,   9.43), (  -1.18,  -0.30,   9.35), (  -1.09,  -0.31,   9.55), (  -1.14,  -0.10,   9.72), (  -1.20,  -0.11,   9.45), (  -1.12,  -0.19,   9.99), (  -1.38,  -0.34,   9.22), (  -1.20,  -0.12,   9.42), (  -1.33,  -0.38,   9.53), (  -1.37,  -0.30,   9.39), (  -1.16,  -0.24,   9.49), (  -1.05,  -0.16,   9.38), (  -1.16,  -0.39,   9.49), (  -1.14,  -0.22,   9.30), (  -1.20,  -0.33,   9.66), (  -1.03,  -0.10,   9.80), (  -1.25,  -0.35,   9.41), (  -0.97,  -0.13,   9.44), (  -1.08,  -0.30,   9.53), (  -1.03,  -0.15,   9.53), (  -0.94,  -0.50,   9.60), (  -0.94,  -0.27,   9.76), (  -0.77,   0.08,   9.40), (  -0.92,  -0.13,   9.32), (  -1.25,  -0.38,   8.81), (  -0.85,  -0.18,   9.60), (  -0.79,  -0.14,   9.65), (  -0.63,  -0.33,   9.74), (  -0.46,  -0.39,   9.70), (  -0.26,  -0.19,   9.55), (  -0.21,  -0.34,   9.97), (  -0.33,  -0.16,   9.56), (  -0.58,  -0.48,   9.48), (  -0.59,  -0.20,   9.38), (  -0.62,  -0.47,   9.97), (  -0.69,  -0.51,   9.66), (  -0.92,  -0.63,   9.28), (  -0.64,  -0.41,   9.51), (  -0.56,  -0.19,   9.44), (  -0.52,  -0.14,   9.23), (  -0.54,  -0.25,   8.96), (  -0.56,  -0.10,   9.35), (  -0.48,  -0.01,   9.25), (  -0.39,  -0.12,   9.77), (  -0.56,  -0.08,   9.28), (  -0.26,   0.20,   9.21), (  -0.06,   0.59,   8.89), (  -0.82,  -0.42,   8.91), (  -0.47,   0.56,   9.30), (  -0.91,   0.14,  10.01), (   0.27,   0.71,  11.42), (  -1.51,   0.44,   9.47), (  -1.29,  -0.01,  10.13), (  -1.48,   0.08,   8.94), (  -1.12,   0.19,   9.23), (  -0.61,   0.31,  10.20), (  -0.54,   0.59,   9.78), (  -0.34,   0.51,   9.75), (  -0.65,   0.38,   9.85), (  -0.79,   0.23,   9.13), (  -0.66,   0.03,   9.57), (  -0.45,   0.20,   9.64), (  -0.45,   0.34,   9.14), (  -0.53,  -0.11,   9.72), (  -0.34,  -0.04,   9.67), (  -0.49,  -0.08,   9.65), (  -0.62,  -0.34,   9.59), (  -0.95,  -0.48,   9.45), (  -0.80,  -0.52,  10.02), (  -0.83,  -0.15,   9.96), (  -1.01,  -0.40,   9.59), (  -0.94,   0.01,   9.06), (  -0.75,  -0.04,   9.94), (  -1.52,  -0.29,   8.88), (  -0.93,  -0.16,   9.64), (  -0.74,   0.36,   9.95), (  -1.11,  -0.08,   9.07), (  -1.08,  -0.22,   9.57), (  -1.30,   0.05,   9.21), (  -0.80,  -0.24,   9.70), (  -0.87,   0.22,   9.69), (  -1.10,   0.24,   9.49), 
            ( -0.15,   0.08,   9.62), ( -0.17,   0.06,   9.49), ( -0.18,   0.08,   9.57), ( -0.18,   0.03,   9.57), ( -0.19,   0.00,   9.67), ( -0.16,  -0.05,   9.57), ( -0.17,  -0.28,   9.65), ( -0.17,  -0.09,   9.55), ( -0.17,  -0.08,   9.58), ( -0.11,  -0.15,   9.66), ( -0.14,  -0.05,   9.77), ( -0.23,  -0.94,   9.63), ( -0.20,   0.08,   9.44), ( -0.11,   0.44,   9.54), ( -0.19,  -2.09,   9.50), ( -0.10,  -0.06,   9.61), (  0.14,  -2.09,  10.66), ( -0.02,  -0.13,   9.38), (  0.04,  -0.35,   9.79), (  0.12,  -0.39,   9.85), (  0.10,  -0.19,   9.72), (  0.13,   2.26,   7.90), ( -0.04,   0.05,   9.50), (  0.04,  -0.07,   9.75), (  0.03,  -0.07,   9.72), (  0.34,  -0.50,   9.40), (  0.06,  -0.08,   9.66), ( -0.01,  -0.08,   9.51), (  0.01,  -0.11,   9.77), (  0.05,  -0.09,   9.66), (  0.00,  -0.07,   9.63), (  0.01,  -0.10,   9.65), (  0.04,  -0.09,   9.64), (  0.06,  -0.10,   9.51), (  0.07,  -0.09,   9.75), (  0.09,  -0.08,   9.68), (  0.03,  -0.07,   9.44), (  0.05,  -0.14,   9.63), (  0.08,  -0.05,   9.64), (  0.06,  -0.08,   9.48), (  0.02,  -0.12,   9.55), (  0.03,  -0.05,   9.53), (  0.03,   0.04,   9.65), (  0.01,  -0.04,   9.62), (  0.05,  -0.07,   9.59), (  0.03,  -0.03,   9.69), ( -0.03,  -0.06,   9.66), (  0.01,  -0.04,   9.59), ( -0.02,  -0.02,   9.57), (  0.02,  -0.07,   9.57), ( -0.03,   0.03,   9.58), ( -0.04,  -0.14,   9.64), (  0.01,  -0.09,   9.53), ( -0.01,  -0.08,   9.48), (  0.03,  -0.05,   9.58), (  0.02,  -0.04,   9.59), (  0.00,   0.00,   9.69), (  0.01,  -0.04,   9.61), (  0.01,   0.07,   9.57), (  0.09,   0.02,   9.69), (  0.02,   0.06,   9.59), (  0.07,  -0.13,   9.61), (  0.07,  -0.05,   9.48), (  0.09,  -0.08,   9.65), (  0.08,  -0.03,   9.58), (  0.12,   0.01,   9.32), (  0.12,   0.11,   9.67), (  0.24,   0.16,   9.66), (  0.27,  -0.02,   9.56), ( -0.18,  -0.18,   9.55), (  0.09,   0.10,   9.62), (  0.20,   0.10,   9.65), (  0.07,   0.24,   9.49), ( -0.56,   0.21,   9.29), ( -1.07,  -0.06,   9.49), ( -1.31,  -0.11,   9.47), ( -0.95,  -0.29,   8.29), (  0.83,  -0.10,  10.76), (  1.90,   0.09,   9.65), (  1.61,   0.22,   9.44), (  0.92,   0.00,   9.65), (  1.39,   0.07,   9.46), (  2.94,   0.11,   9.77), (  1.79,  -0.12,   9.59), (  0.28,  -0.93,   9.41), ( -1.59,  -0.41,   7.91), ( -2.69,  -0.21,   8.95), ( -2.84,  -0.47,   9.01), ( -0.34,  -0.31,   9.11), ( -1.91,  -0.66,   9.32), ( -0.81,  -0.60,   8.51), ( -0.69,  -1.25,   9.90), (  0.85,  -0.80,   9.31), (  1.42,  -0.73,   9.54), (  1.14,  -0.20,   9.45), (  1.14,  -0.16,  10.03), (  2.43,  -0.51,  10.66), (  2.81,   0.40,   8.45), (  0.79,   0.34,  10.13), (  0.09,   0.40,   8.57), ( -1.69,  -0.21,   9.93), ( -1.58,   0.45,   9.93), ( -1.48,   0.30,   9.34), ( -2.39,   0.42,   9.66), ( -1.33,  -0.02,   9.81), ( -0.09,  -1.30,  12.06), (  2.62,  -0.46,   8.31), (  3.41,  -0.33,   9.24), (  1.62,  -0.09,   9.55), (  2.54,   0.08,   9.36), (  2.71,  -0.32,   9.71), (  2.53,   0.36,  10.31), (  0.76,   0.31,   7.94), ( -1.14,   0.02,   9.26), ( -1.89,  -0.04,   9.51), ( -2.08,   0.68,   9.22), ( -2.07,  -1.10,  10.62), ( -1.26,   0.23,   9.45), ( -1.14,   0.28,   9.85), ( -0.51,  -0.45,   8.70), (  1.88,  -0.25,   9.04), (  2.18,   0.20,   9.15), (  2.55,   0.05,   9.87), (  1.69,   0.63,   9.82), (  2.91,  -0.41,   9.17), (  1.46,  -0.04,   8.54), (  1.46,   0.53,   7.33), ( -1.27,  -0.02,   9.33), ( -2.24,  -0.01,   9.49), ( -2.90,   0.83,   9.77), ( -2.60,   0.68,   8.41), ( -2.33,   0.85,   9.21), ( -1.53,   0.34,   8.68), (  1.32,   0.08,   9.14), (  2.04,  -0.01,  10.62), (  2.04,  -0.41,   9.01), (  3.45,  -0.27,   9.56), (  2.84,   0.28,   9.42), (  2.83,  -0.39,  10.05), (  1.50,   0.18,  12.02), (  0.82,   0.30,   7.05), ( -0.61,   0.06,   7.40), ( -2.06,   0.47,   9.75), ( -2.72,   0.46,   9.43), ( -1.71,   0.17,   9.85), ( -1.95,   0.58,   7.75), ( -1.47,   0.42,   7.75), (  0.22,   0.11,   8.99), (  0.83,   0.05,   8.63), (  2.19,  -0.61,   9.22), (  4.09,  -0.05,   9.13), (  2.95,   0.17,   9.52), (  3.52,   0.28,   9.78), (  2.55,   0.17,  11.04), (  0.56,   0.26,   9.48), ( -1.22,  -0.02,   7.76), ( -1.96,   0.23,   9.95), ( -2.38,   0.41,   9.17), ( -1.74,   0.37,  10.05), ( -1.86,   0.30,   9.50), ( -1.62,   0.35,   8.60), ( -0.26,   0.26,   7.29), (  1.85,   0.03,   9.29), (  2.39,  -0.01,  10.03), (  3.53,  -0.48,   9.71), (  2.80,   0.53,   9.49), (  2.92,   0.32,   8.54), (  1.79,  -0.37,   7.54), (  1.88,  -0.26,   9.71), ( -0.72,   0.17,  10.42), ( -1.00,   0.16,  10.56), ( -2.37,   0.46,   8.74), ( -0.82,   0.16,   9.49), ( -2.39,   0.30,  10.07), ( -1.82,   0.65,   9.32), ( -1.04,   0.04,   7.81), (  2.39,  -0.68,   7.65), (  2.19,   0.61,   9.10), (  3.86,  -0.73,   9.43), (  3.49,   0.55,   9.58), (  2.82,   0.26,  10.59), (  1.63,  -0.40,   8.63), ( -0.15,  -0.01,   7.75), ( -2.07,   0.31,   8.41), ( -1.92,   0.70,   9.56), ( -2.25,   0.66,   9.51), ( -2.75,   0.18,   9.67), ( -1.57,   0.39,   8.81), ( -0.58,  -0.29,   8.81), (  0.81,   0.68,   8.24), (  0.81,   0.02,   8.72), (  3.31,  -0.39,  10.48), (  3.15,  -0.29,   9.61), (  3.15,  -0.11,   9.71), (  2.69,  -0.54,   9.72), (  0.55,   0.20,  12.78), ( -0.43,   0.34,   8.69), ( -1.23,   0.12,   9.21), ( -2.43,   0.33,  10.13), ( -1.12,   0.23,   9.56), (  0.28,   0.20,   9.57), ( -0.27,   0.17,   9.56), (  0.74,   0.11,   9.58), (  0.34,   0.03,   9.56), (  0.36,   0.11,   9.67), (  0.33,   0.09,   9.63), (  0.32,   0.03,   9.79), (  0.27,   0.36,   9.16), (  0.29,   0.23,   9.54), (  0.23,   0.13,   9.62), (  0.25,   0.03,   9.67), (  0.21,   0.36,   9.62), (  0.23,   0.07,   9.55), (  0.27,   0.17,   9.53), (  0.27,   0.13,   9.62), (  0.23,   0.17,   9.52), (  0.27,   0.10,   9.64), (  0.23,   0.04,   9.53), (  0.24,   0.21,   9.64), (  0.23,   0.36,   9.41), (  0.24,   0.30,   9.51), (  0.21,   0.12,   9.64), (  0.23,   0.14,   9.52), (  0.28,   0.09,   9.58), (  0.21,   0.42,   9.49), (  0.24,   0.07,   9.51), (  0.28,   0.17,   9.86), (  0.31,   0.04,   9.45), (  0.23,  -0.05,   9.54), (  0.30,   0.10,   9.62), (  0.29,   0.07,   9.62), (  0.29,   0.13,   9.56), (  0.34,   0.15,   9.58), (  0.31,   0.13,   9.61), (  0.32,   0.12,   9.65), (  0.30,   0.17,   9.59), (  0.31,   0.07,   9.61), (  0.33,   0.16,   9.56), (  0.27,   0.19,   9.62), (  0.29,   0.15,   9.59), (  0.30,   0.26,   9.54), (  0.32,   0.23,   9.56), (  0.14,  -0.81,   9.66), (  0.23,  -1.98,   9.95), (  0.12,  -1.99,   9.37), (  0.62,  -0.97,   9.51), (  0.55,   1.68,  10.32), (  0.38,   2.62,  11.03), (  0.44,   3.65,   9.57), (  1.92,   4.32,   9.18), (  0.54,   2.95,   7.28), (  0.04,   2.08,  10.32), ( -0.82,  -2.11,   9.75), (  0.86,  -4.24,   9.47), ( -0.02,  -0.33,   8.67), (  0.23,  -2.39,   9.99), (  0.43,  -1.63,   9.28), ( -0.16,  -0.45,  10.15), (  0.86,   0.05,   9.69), (  0.25,   3.14,   9.72), (  0.45,   3.86,   9.57), (  0.78,   0.78,   9.06), (  0.34,   3.42,  10.20), (  0.26,   3.27,   9.92), ( -0.38,   0.62,   8.97), (  0.27,  -1.04,   9.67), (  0.52,  -2.99,   9.51), (  0.50,  -3.12,   9.67), ( -0.61,  -2.97,   9.46), (  0.71,  -2.78,   9.46), (  0.27,  -2.27,   8.79), (  1.50,   1.19,   9.06), (  0.50,   4.07,   9.33), ( -0.44,   4.45,  10.63), ( -0.55,   3.14,   9.42), (  0.11,   3.30,   9.35), (  0.31,   2.93,   9.75), ( -0.17,   0.90,  10.15), (  0.73,  -3.00,  10.34), (  0.61,  -4.06,   9.72), ( -0.13,  -0.21,   9.63), (  0.63,  -4.70,   8.96), (  0.72,  -2.19,   9.82), ( -0.04,  -0.59,   9.12), (  1.04,   3.26,   9.60), ( -0.28,   4.30,   9.83), (  0.45,   4.09,   9.57), (  0.44,   2.85,  10.05), (  0.00,   1.90,   9.57), (  0.12,   0.65,   9.27), (  0.38,  -0.45,  10.15), (  0.74,  -4.74,   7.46), (  0.44,  -1.67,   9.74), (  0.27,  -2.73,   8.98), (  0.57,  -0.55,   8.76), ( -0.92,   0.34,  10.01), (  0.51,   1.18,   9.85), (  0.63,   3.42,   9.55), (  0.24,   3.97,  10.76), (  0.77,   4.48,   9.74), (  0.14,   2.20,   9.31), ( -0.02,   0.32,   9.33), (  0.77,   0.26,   9.26), (  0.03,  -3.15,   9.96), (  0.27,  -3.15,   9.83), ( -0.03,  -1.30,   9.35), (  0.42,  -3.14,   9.00), (  0.32,  -1.28,   8.82), ( -0.68,   0.63,  10.22), (  0.68,   0.97,   9.56), (  0.97,   2.71,   9.68), ( -0.22,   4.18,   8.96), (  0.68,   4.78,   9.19), (  0.22,   3.18,   9.68), ( -0.21,   2.24,  10.06), ( -0.09,  -1.25,   8.96), (  0.26,  -4.14,   9.65), (  0.47,  -1.04,   9.55), ( -0.39,  -0.34,   9.51), (  0.02,   0.86,   9.84), ( -0.21,   0.95,   9.58), (  0.12,   0.18,   9.52), (  0.14,   0.27,   9.58), (  0.13,   0.23,   9.63), (  0.16,   0.17,   9.59), (  0.15,   0.27,   9.55), (  0.12,   0.20,   9.59), (  0.17,   0.24,   9.58), (  0.17,   0.33,   9.60), (  0.17,   0.28,   9.54), (  0.18,   0.25,   9.65), (  0.21,   0.26,   9.59), (  0.20,   0.25,   9.58), (  0.17,   0.24,   9.57), (  0.19,   0.24,   9.57), (  0.22,   0.24,   9.55), (  0.15,   0.05,   9.57), (  0.25,   0.21,   9.59), (  0.21,   0.25,   9.57), (  0.22,   0.19,   9.58), (  0.51,   0.21,   9.39), (  0.39,   0.33,   9.74), ( -0.90,   1.75,  10.44), (  0.72,   0.83,   9.77), (  0.17,  -0.93,  11.17), ( -0.37,   1.17,  13.07), ( -0.53,   0.19,  12.06), (  0.21,   0.48,  12.22), ( -0.60,   0.48,  10.52), ( -0.77,  -0.20,   8.06), (  0.11,  -0.01,   3.97), ( -0.86,  -0.09,   3.12), (  0.02,  -0.34,   3.04), ( -0.17,   0.79,   6.18), (  0.34,   0.77,   9.57), (  0.20,  -0.12,  14.44), ( -0.36,   0.09,  17.11), ( -0.10,  -1.28,  15.21), (  0.71,   0.14,  11.49), ( -0.69,   1.02,  12.63), (  0.46,   0.93,   9.70), ( -0.58,  -0.08,   8.84), ( -0.18,   0.56,   6.87), (  0.32,   0.18,   3.52), ( -0.34,  -0.12,   3.89), (  0.25,  -0.50,   3.94), ( -0.15,   0.11,   7.41), ( -0.11,  -0.31,  11.49), ( -0.23,   1.26,  16.50), ( -0.50,   0.91,  16.52), ( -0.64,   0.32,  14.21), (  0.07,   0.54,  11.42), (  0.07,   1.02,  10.93), ( -0.94,   1.23,   9.90), ( -0.30,   0.11,   6.46), ( -0.69,  -0.07,   5.34), ( -0.71,  -0.09,   4.34), (  0.00,  -0.45,   3.94), ( -0.93,   1.64,   8.17), ( -0.23,   0.09,   7.58), (  0.21,   0.45,  10.38), ( -0.55,   1.86,  13.54), (  0.82,   0.17,  12.47), ( -0.31,   2.66,  17.46), (  0.32,   0.87,  13.38), (  0.34,   1.13,  10.54), ( -0.19,   1.83,   9.48), ( -0.64,   0.73,   7.56), ( -0.67,   0.11,   5.67), ( -0.74,  -0.57,   3.93), ( -0.66,  -0.68,   3.13), (  0.04,   0.65,   3.67), (  0.30,   0.10,   7.34), (  0.02,   1.98,  13.43), (  1.15,   1.04,  15.26), ( -0.06,   2.53,  17.70), (  0.41,   1.54,  13.93), (  0.77,   1.03,  10.24), ( -0.34,   1.83,  10.02), (  0.04,   0.78,   7.26), (  0.22,  -0.13,   6.01), ( -0.27,  -0.33,   5.41), ( -0.27,  -1.32,   5.41), ( -0.91,   1.96,   9.08), (  0.00,  -0.10,   8.67), (  0.76,   2.17,  12.45), (  0.71,   2.63,  15.18), (  1.08,   0.46,  13.96), (  0.95,   1.61,  12.33), (  0.39,   1.11,  10.51), (  0.27,   0.07,   7.77), (  0.24,  -0.30,   6.91), (  0.04,  -0.14,   4.32), (  0.29,  -0.87,   3.03), ( -0.66,   1.21,   6.76), (  0.17,   1.51,   7.94), (  2.97,  -0.59,   8.64), ( -0.01,   5.45,  16.39), (  1.47,   1.20,  11.77), (  0.76,   1.33,  11.32), (  1.11,   0.71,   9.51), (  1.28,   0.88,   8.72), (  0.98,   1.25,   9.17), (  0.84,   1.43,   9.45), (  0.94,   1.02,   9.45), (  1.04,   1.49,   9.45), (  0.76,   1.12,   9.42), (  1.01,   1.23,   9.22), (  0.72,   1.17,   9.33), (  1.04,   1.57,   9.35), (  1.06,   1.35,   9.62), (  0.88,   1.50,   9.70), (  0.94,   1.24,   9.36), (  0.80,   1.18,   9.65), (  1.15,   1.07,   9.01), (  0.68,   1.30,   9.67), (  0.74,   1.47,   9.50), (  0.90,   1.37,   9.41), (  0.93,   1.14,   9.71), (  1.10,   0.97,   9.40), (  1.15,   1.37,   9.38), (  0.84,   1.51,   9.90), (  0.85,   1.01,   9.48), (  0.85,   1.89,  10.07), (  1.02,   2.11,   9.38), (  0.65,   1.22,  10.00), (  0.80,   1.05,   8.89), (  0.39,   1.23,   9.55), (  1.08,   1.47,   8.64), (  0.53,   0.80,   9.68), (  0.67,   2.06,   9.60), (  0.57,   1.48,   8.30), (  0.89,   1.07,   8.81), (  0.82,   0.12,   9.71), (  0.91,   0.87,   9.16), (  1.44,   0.77,   9.16), (  1.49,   1.61,   9.38), (  1.73,   0.91,   9.31), (  2.00,   0.63,   9.17), (  2.04,   1.69,   9.37), (  1.48,   0.29,   9.46), (  1.63,   1.42,   9.59), (  1.56,   0.66,   9.49), (  2.40,   1.12,   8.52), (  1.49,   0.64,   9.50), (  2.22,   1.34,   8.53), (  1.14,   2.45,  11.21), (  2.43,   0.31,   8.86), (  2.33,   0.79,  12.62), (  2.50,   0.57,   9.80), (  2.81,   1.45,   9.22), (  2.16,   1.32,  10.73), (  2.42,   1.23,  11.47), (  2.56,   1.81,  10.56), (  2.02,   0.42,   9.96), (  2.16,   1.61,   7.14), (  2.41,   0.51,   8.46), (  2.55,   0.30,   8.41), (  2.48,   0.60,   9.29), (  3.54,   1.02,   8.94), (  3.73,   1.21,  11.19), (  4.57,   0.57,   8.42), (  4.44,   1.09,   8.39), (  4.64,   0.03,   7.92), (  4.67,  -0.30,   7.90), (  4.85,   0.87,   9.09), (  5.85,  -0.82,   6.53), (  5.93,  -2.82,   8.54), (  6.26,   0.18,   6.68), (  7.11,  -1.60,   7.73), (  8.09,  -0.66,   5.66), (  7.02,   1.74,   8.30), (  8.50,  -0.82,   5.82), (  7.37,   0.29,   6.25), (  8.39,  -2.38,   3.88), (  7.77,  -2.39,   6.78), (  9.08,  -1.79,   5.18), (  9.88,  -0.67,   3.73), (  8.57,  -0.76,   5.32), (  8.51,  -0.89,   5.00), (  9.42,   0.87,   3.76), (  9.16,   2.13,   2.44), ( 12.89,   1.00,   3.21), (  7.67,   0.73,   1.44), (  9.45,   0.58,   1.86), (  9.85,   1.35,   2.10), ( 10.17,   1.73,   2.16), (  9.88,   1.02,   1.88), (  9.70,   0.93,   1.98), (  9.33,   1.37,   2.16), ( 10.14,   1.17,   2.05), ( 10.36,   1.14,   2.18), (  8.65,   1.27,   1.80), (  9.72,   1.05,   1.94), (  9.07,   1.31,   1.71), ( 10.47,   1.29,   2.29), (  9.23,   1.24,   1.57), ( 10.90,   1.12,   2.03), ( 10.55,   1.40,   1.93), ( 10.52,   1.23,   1.72), ( 10.17,   1.07,   1.76), (  9.98,   1.15,   1.97), (  8.47,   1.25,   1.50), (  9.33,   1.16,   1.91), (  9.49,   1.30,   1.95), (  9.70,   1.29,   2.15), (  8.76,   1.13,   1.82), (  9.75,   0.92,   2.18), ( 10.07,   0.98,   2.15), ( 10.18,   1.40,   2.42), ( 10.94,   1.44,   2.31), ( 11.34,   1.14,   2.32), ( 10.83,   1.37,   2.17), (  9.48,   1.40,   1.71), (  9.71,   1.17,   1.80), (  9.81,   1.36,   1.83), (  9.29,   1.47,   1.58), (  9.04,   1.31,   1.59), (  9.06,   1.27,   1.70), (  8.89,   1.41,   1.65), (  9.74,   1.45,   1.91), (  9.63,   1.25,   1.78), (  9.92,   1.24,   2.04), (  9.99,   1.10,   2.04), (  9.71,   1.18,   1.94), ( 10.67,   1.12,   2.18), (  9.95,   1.23,   2.03), (  9.95,   1.11,   2.14), (  9.71,   0.98,   1.98), (  9.57,   1.00,   2.00), (  9.86,   1.02,   2.16), (  9.70,   1.03,   1.92), ( 10.29,   1.09,   2.19), (  9.90,   1.17,   1.90), ( 10.43,   1.27,   2.16), ( 10.38,   1.26,   2.04), ( 10.05,   1.37,   1.87), (  9.98,   1.37,   1.80), (  9.98,   1.38,   1.85), (  9.88,   1.36,   1.82), (  9.90,   1.44,   1.83), (  9.96,   1.50,   1.93), (  9.86,   1.44,   1.82), (  9.97,   1.33,   1.88), (  9.89,   1.35,   1.95), (  9.68,   1.33,   1.82), (  9.97,   1.26,   2.02), (  9.87,   1.21,   2.03), ( 10.10,   1.14,   2.04), ( 10.06,   1.14,   2.05), ( 10.05,   1.15,   2.13), (  9.89,   1.08,   2.05), (  9.90,   1.03,   2.09), (  9.90,   1.09,   2.13), (  9.93,   1.15,   2.10), (  9.88,   1.13,   2.05), (  9.71,   1.19,   1.92), (  9.72,   1.21,   2.02), (  9.73,   1.18,   1.92), (  9.82,   1.28,   1.92), (  9.90,   1.29,   1.95), ( 10.02,   1.27,   1.86), (  9.92,   1.22,   1.79), ( 10.00,   1.26,   1.93), (  9.88,   1.29,   1.82), (  9.87,   1.31,   1.80), (  9.76,   1.30,   1.79), (  9.83,   1.36,   1.91), (  9.86,   1.31,   1.84), (  9.60,   1.33,   1.85), (  9.65,   1.26,   1.91), (  9.52,   1.28,   1.87), (  9.86,   1.26,   1.97), (  9.85,   1.29,   1.93), ( 10.21,   1.27,   2.08), ( 10.16,   1.20,   2.02), (  9.90,   1.23,   2.10), (  9.90,   1.11,   2.05), (  9.53,   1.13,   1.76), (  9.52,   1.25,   2.15), (  9.46,   1.25,   1.81), (  9.90,   1.23,   1.94), (  9.63,   1.36,   2.06), ( 10.48,   1.01,   2.29), (  9.73,   0.84,   1.74), ( 10.11,   0.97,   1.90), ( 10.20,   1.04,   2.02), (  9.99,   0.98,   1.80), ( 10.09,   0.95,   1.99), (  9.95,   1.24,   1.82), ( 10.12,   1.24,   2.08), (  9.73,   1.15,   1.97), (  9.59,   1.28,   2.03), (  9.21,   1.35,   1.80), (  9.67,   1.40,   1.97), ( 10.06,   1.64,   2.05), (  9.91,   1.73,   1.96), ( 10.03,   1.67,   2.09), ( 10.12,   1.38,   2.06), ( 10.32,   1.40,   1.97), ( 10.69,   1.57,   2.19), ( 10.69,   1.27,   2.05), ( 10.54,   1.31,   2.13), ( 10.36,   1.21,   1.93), ( 10.35,   1.05,   2.07), (  9.57,   0.95,   1.81), (  9.31,   0.84,   1.77), (  9.73,   0.95,   2.12), (  9.86,   0.93,   2.05), (  9.53,   0.78,   1.75), (  9.45,   0.80,   2.05), ( 11.01,   1.17,   2.24), ( 11.70,   1.25,   2.21), ( 11.90,   1.46,   2.23), ( 11.60,   1.26,   2.22), ( 10.91,   1.35,   2.12), ( 10.88,   1.61,   2.24), ( 10.20,   1.58,   2.00), (  9.40,   1.61,   1.91), (  8.61,   1.56,   1.82), (  8.65,   1.54,   1.86), (  9.20,   1.59,   1.96), (  9.67,   1.88,   2.05), ( 10.51,   1.72,   2.22), ( 11.37,   1.39,   2.23), ( 11.95,   1.39,   2.27), ( 12.63,   1.30,   2.38), ( 12.36,   1.08,   2.19), ( 12.12,   0.98,   2.20), ( 11.01,   0.92,   2.01), ( 10.04,   0.80,   1.81), ( 10.00,   0.74,   1.70), (  8.59,   0.74,   1.62), (  8.70,   0.67,   1.71), (  8.75,   0.70,   1.74), (  9.72,   0.81,   1.97), ( 10.15,   0.90,   2.02), ( 11.51,   1.03,   2.40), ( 12.57,   1.33,   2.49), ( 13.48,   1.50,   2.60), ( 13.26,   1.53,   2.47), ( 11.99,   1.52,   2.29), ( 11.68,   1.48,   2.32), ( 10.41,   1.65,   2.00), (  9.71,   1.81,   2.00), (  8.72,   1.63,   1.73), (  8.02,   1.59,   1.83), (  8.31,   1.54,   1.83), (  8.93,   1.56,   1.95), ( 10.32,   1.54,   2.11), ( 11.13,   1.47,   2.23), ( 12.04,   1.41,   2.28), ( 12.15,   1.34,   2.60), ( 13.13,   1.10,   2.22), ( 12.77,   1.19,   2.30), ( 12.74,   0.96,   2.15), ( 10.18,   0.76,   1.79), (  9.34,   0.64,   1.85), (  9.28,   0.60,   1.72), (  8.39,   0.61,   1.65), (  8.43,   0.60,   1.65), (  9.25,   0.78,   1.97), ( 10.52,   0.96,   2.20), ( 11.96,   1.20,   2.37), ( 12.72,   1.35,   2.47), ( 13.35,   1.54,   2.64), ( 13.08,   1.57,   2.59), ( 11.81,   1.62,   2.27), ( 11.07,   1.60,   2.15), ( 10.13,   1.73,   2.00), (  9.09,   1.71,   1.89), (  8.37,   1.70,   1.71), (  8.28,   1.57,   1.69), (  8.86,   1.68,   1.87), (  9.81,   1.56,   2.04), ( 11.07,   1.48,   2.23), ( 12.00,   1.31,   2.31), ( 12.68,   1.36,   2.47), ( 12.98,   1.14,   2.49), ( 12.54,   1.00,   2.33), ( 12.20,   1.05,   2.29), ( 11.68,   0.96,   2.17), ( 10.71,   0.84,   1.98), (  9.67,   0.75,   1.86), (  8.74,   0.57,   1.74), (  8.27,   0.51,   1.62), (  8.26,   0.62,   1.62), (  9.44,   0.82,   1.98), ( 10.31,   1.10,   2.08), ( 11.65,   1.29,   2.39), ( 12.40,   1.29,   2.40), ( 12.80,   1.54,   2.48), ( 12.89,   1.49,   2.50), ( 12.61,   1.66,   2.48), ( 11.71,   1.70,   2.30), ( 10.02,   1.56,   1.83), (  9.72,   1.60,   2.09), (  9.23,   1.76,   2.00), (  8.24,   1.75,   1.68), (  8.51,   1.49,   1.71), (  9.06,   1.58,   2.08), ( 10.14,   1.57,   2.07), ( 11.64,   1.47,   2.34), ( 12.22,   1.45,   2.37), ( 12.27,   1.36,   2.59), ( 12.68,   1.11,   2.39), ( 12.27,   0.93,   2.33), ( 11.78,   0.95,   2.24), ( 11.21,   0.91,   2.15), ( 10.02,   0.80,   1.87), (  9.28,   0.65,   1.84), (  8.54,   0.57,   1.68), (  8.27,   0.63,   1.70), (  8.58,   0.57,   1.78), ( 10.00,   0.83,   2.04), ( 10.86,   1.05,   2.13), ( 12.40,   1.31,   2.57), ( 12.69,   1.48,   2.53), ( 12.72,   1.58,   2.45), ( 12.65,   1.52,   2.44), ( 11.83,   1.69,   2.28), ( 11.27,   1.79,   2.32), (  9.67,   1.74,   1.93), (  8.96,   1.58,   1.85), (  8.39,   1.61,   1.82), (  8.37,   1.64,   1.79), (  8.95,   1.61,   1.95), (  9.95,   1.47,   2.12), ( 11.06,   1.50,   2.23), ( 11.88,   1.35,   2.32), ( 12.71,   1.21,   2.48), ( 12.83,   1.23,   2.45), ( 12.70,   1.14,   2.42), ( 11.82,   1.07,   2.23), ( 10.22,   0.72,   1.90), (  9.29,   0.63,   1.89), (  8.58,   0.65,   1.67), (  8.35,   0.66,   1.57), (  8.66,   0.75,   1.73), (  9.54,   0.98,   1.87), ( 10.68,   1.18,   2.13), ( 12.09,   1.49,   2.45), ( 12.40,   1.58,   2.39), ( 12.26,   1.55,   2.42), ( 11.72,   1.57,   2.25), ( 11.11,   1.59,   2.18), ( 10.70,   1.71,   2.17), (  9.75,   1.77,   1.93), (  9.41,   1.64,   1.87), (  8.99,   1.71,   1.95), (  8.79,   1.59,   1.84), (  9.09,   1.50,   1.93), (  9.84,   1.42,   2.18), ( 10.19,   1.22,   2.13), ( 11.04,   1.24,   2.35), ( 11.29,   1.12,   2.28), ( 11.33,   1.09,   2.24), ( 11.23,   0.99,   2.21), ( 10.32,   0.88,   2.07), (  9.83,   0.75,   1.93), (  9.83,   0.74,   1.91), (  9.62,   0.79,   2.08), ( 10.03,   1.04,   2.15), ( 10.75,   1.27,   2.21), ( 10.24,   0.57,   1.17), (  9.67,   2.54,   2.57), ( 10.47,   2.12,   3.42), ( 11.04,   2.39,   2.70), (  9.86,   2.50,   1.73), ( 10.46,   2.15,   0.80), (  9.70,   1.89,   0.38), (  9.40,   1.16,   1.55), ( 10.13,   0.90,   2.64), ( 10.12,   0.82,   3.23), ( 10.12,   0.85,   3.30), (  9.86,   1.10,   2.75), (  9.51,   1.25,   2.06), (  9.87,   0.98,   1.58), (  9.60,   0.60,   1.70), (  9.93,   0.45,   2.14), (  9.94,   0.73,   2.49), (  9.58,   1.04,   2.50), ( 10.07,   1.30,   2.25), (  9.90,   1.36,   2.09), (  9.58,   1.17,   1.92), (  9.89,   0.82,   2.02), (  9.88,   1.21,   2.39), (  9.44,   1.31,   2.06), (  9.69,   1.05,   2.08), (  9.86,   1.20,   1.87), ( 10.07,   1.30,   2.01), ( 10.02,   1.13,   2.01), (  9.92,   1.17,   2.04), (  9.87,   1.27,   1.93), ( 10.15,   1.21,   2.11), ( 10.17,   1.18,   2.14), ( 10.00,   1.36,   2.05), (  9.74,   1.28,   1.88), (  9.98,   1.25,   2.04), (  9.73,   1.34,   1.97), (  9.90,   1.25,   1.98), (  9.64,   1.25,   1.92), (  9.91,   1.25,   2.07), (  9.84,   1.26,   1.95), (  9.61,   1.22,   1.91), ( 10.06,   1.17,   2.06), (  9.73,   1.33,   1.99), (  9.87,   1.21,   2.02), (  9.65,   1.11,   1.95), (  9.65,   1.15,   1.88), (  9.84,   1.20,   2.00), (  9.93,   1.18,   1.99), (  9.70,   1.17,   1.87), (  9.45,   1.17,   1.86), (  9.86,   1.17,   1.88), ( 10.04,   1.19,   1.99), ( 10.13,   1.28,   2.00), (  9.93,   1.20,   1.91), (  9.95,   1.18,   2.04), (  9.90,   1.26,   2.01), (  9.79,   1.26,   1.90), (  9.65,   1.28,   1.94), (  9.61,   1.21,   1.93), (  9.89,   1.28,   2.01), (  9.97,   1.33,   2.06), ( 10.11,   1.27,   2.04), ( 10.00,   1.37,   2.05), (  9.62,   1.30,   1.99), (  9.36,   1.23,   2.00), ( 10.55,   1.29,   2.17), (  8.89,   1.62,   1.74), (  3.98,   1.56,   1.45), (  0.01,   1.09,   0.11), (  1.02,  -0.13,   1.17), (  0.19,  -0.86,   0.49), ( -0.02,  -0.77,   0.33), (  0.53,  -0.33,   1.37), ( -1.58,   0.17,   0.01), ( 18.95,   4.79,  -3.82), ( 19.24,   0.44,   9.88), ( 19.54,   8.63,   5.71), (  3.73,  -0.57,   0.92), (  6.71,   1.18,  -2.28), (  9.29,   0.31,   5.75), (  4.01,  -0.20,   6.88), ( 10.15,   1.41,   3.34), ( 11.35,   2.68,   3.83), ( 14.06,   2.06,   3.09), ( 11.53,   1.63,   2.25), (  9.07,   0.75,   0.96), (  8.55,   0.91,   0.87), ( 10.22,   1.73,   1.67), ( 11.15,   2.10,   2.01), ( 10.71,   1.81,   1.71), ( 10.13,   1.27,   1.61), (  9.23,   1.01,   1.28), (  9.57,   1.21,   1.56), (  9.96,   1.68,   1.70), (  9.96,   1.71,   1.65), (  9.81,   1.41,   1.55), (  9.82,   1.27,   1.62), (  9.72,   1.47,   1.74), (  9.99,   1.61,   1.79)
        )
        self._accDataIndex = 0
        self.rndGen_touch = random.Random(3)
        self._touchData = (0, 0, 1, 0, 0, 2, 0, 0, 4, 0, 0, 8, 0, 0, 16, 0, 0, 32, 0, 0, 64, 0, 0, 128, 0, 0)
        self._touchDataIndex = 0

        # Overwrite original methods with emulated ones:
        self.acc             = self._accEmu
        self.acc_wts         = self._accEmu_wts
        self.buttonAny       = self._buttonAnyEmu
        self.buttonAny_wts   = self._buttonAnyEmu_wts
        self.buttonLeft      = self._buttonLeftEmu
        self.buttonLeft_wts  = self._buttonLeftEmu_wts
        self.buttonRight     = self._buttonRightEmu
        self.buttonRight_wts = self._buttonRightEmu_wts
        self.config          = self._configEmu
        self.idn             = self._idnEmu
        self.led             = self._ledEmu
        self.ledDemo         = self._ledDemoEmu
        self.light           = self._lightEmu
        self.light_wts       = self._lightEmu_wts
        self.switch          = self._switchEmu
        self.switch_wts      = self._switchEmu_wts
        self.temp            = self._tempEmu
        self.temp_wts        = self._tempEmu_wts
        self.touch           = self._touchEmu
        self.touch_wts       = self._touchEmu_wts
        self.uptime          = self._uptimeEmu

    def _accEmu(self) -> Tuple[float, float, float]:
        '''Internal method to replay recorded accelerometer data.'''
        lastValues = self._accData[self._accDataIndex]
        self._accDataIndex += 1 # increment index
        self._accDataIndex = (self._accDataIndex) % len(self._accData) # ring-counter
        return lastValues

        # '''Internal method to emulate drifting accelerometer.'''
        # limit = 20.0
        # self.rndVal_accX += 1.0 * (self.rndGen_accX.random() -0.5)
        # self.rndVal_accX = round(self._clamp(-20.0, self.rndVal_accX, +20.0), 2)
        # # math.sqrt(ax^2 + ay^2) shall be less than a limit, e.g. 9.81 m/s^2 or 20.0 m/s^2 in case of movements
        # #           ax^2 + ay^2 = 20^2
        # #                  ay   = math.sqrt(20^2 - ax^2)
        # limitReduction = math.sqrt(limit*limit - self.rndVal_accX*self.rndVal_accX)
        # self.rndVal_accY += 1.0 * (self.rndGen_accY.random() -0.5)
        # self.rndVal_accY = round(self._clamp( -(limit-limitReduction), self.rndVal_accY, +(limit-limitReduction) ), 2)
        # # math.sqrt(ax^2 + ay^2 +az^2) shall be less than a limit, e.g. 9.81 m/s^2 or 20.0 m/s^2 in case of movements
        # #           ax^2 + ay^2 +az^2 = 20^2
        # #                        az   = math.sqrt(20^2 - ax^2 - ay^2)
        # limitReduction = math.sqrt(limit*limit - self.rndVal_accX*self.rndVal_accX - self.rndVal_accY*self.rndVal_accY)
        # self.rndVal_accZ += 1.0 * (self.rndGen_accZ.random() -0.5)
        # self.rndVal_accZ = round(self._clamp( -(limit-limitReduction), self.rndVal_accZ, +(limit-limitReduction) ), 2)

        # return self.rndVal_accX, self.rndVal_accY, self.rndVal_accZ

    def _accEmu_wts(self) -> Tuple[float, float, float, float]:
        raise Exception(f'ERROR in cpg_scpi: acc_wts() is not implemented in emulation mode.')

    def _buttonAnyEmu(self) -> bool:
        raise Exception(f'ERROR in cpg_scpi: buttonAny() is not implemented in emulation mode.')

    def _buttonAnyEmu_wts(self) -> Tuple[float, bool]:
        raise Exception(f'ERROR in cpg_scpi: buttonAny_wts() is not implemented in emulation mode.')

    def _buttonLeftEmu(self) -> bool:
        raise Exception(f'ERROR in cpg_scpi: buttonLeft() is not implemented in emulation mode.')

    def _buttonLeftEmu_wts(self) -> Tuple[float, bool]:
        raise Exception(f'ERROR in cpg_scpi: buttonLeft_wts() is not implemented in emulation mode.')

    def _buttonRightEmu(self) -> bool:
        raise Exception(f'ERROR in cpg_scpi: buttonRight() is not implemented in emulation mode.')

    def _buttonRightEmu_wts(self) -> Tuple[float, bool]:
        raise Exception(f'ERROR in cpg_scpi: buttonRight_wts() is not implemented in emulation mode.')

    def _configEmu(self) -> str:
        raise Exception(f'ERROR in cpg_scpi: config() is not implemented in emulation mode.')

    def _idnEmu(self) -> str:
        raise Exception(f'ERROR in cpg_scpi: idn() is not implemented in emulation mode.')

    def _ledEmu(self, value) -> None:
        '''Control the 10 neopixel LEDs with a value between 0 (all off) and 1023 (all on).'''
        print(f'LEDs {value:010b}')

    def _ledDemoEmu(self) -> None:
        '''Briefly flash all 10 neopixel LEDs with different colors.'''
        # print(f'LEDs {0:010b}')
        print(f'LEDs {1023:010b}')
        print(f'LEDs {0:010b}')

    def _lightEmu(self) -> int:
        '''Internal method to emulate drifting light sensor.'''
        lastValue = self.rndVal_light
        # Calculate new value
        self.rndVal_light += int(80 * (self.rndGen_light.random() -0.5))
        self.rndVal_light = int(self._clamp(0, self.rndVal_light, 1023))
        return lastValue

    def _lightEmu_wts(self) -> Tuple[float, int]:
        raise Exception(f'ERROR in cpg_scpi: light_wts() is not implemented in emulation mode.')

    def _switchEmu(self) -> bool:
        raise Exception(f'ERROR in cpg_scpi: switch() is not implemented in emulation mode.')

    def _switchEmu_wts(self) -> Tuple[float, bool]:
        raise Exception(f'ERROR in cpg_scpi: switch_wts() is not implemented in emulation mode.')

    def _tempEmu(self) -> float:
        '''Internal method to emulate drifting temperature sensor.'''
        lastValue = self.rndVal_temp
        # Calculate new value
        self.rndVal_temp += 2.0 * (self.rndGen_temp.random() -0.5)
        self.rndVal_temp = round(self._clamp(10, self.rndVal_temp, 30), 2)
        return lastValue

    def _tempEmu_wts(self) -> Tuple[float, float]:
        raise Exception(f'ERROR in cpg_scpi: temp_wts() is not implemented in emulation mode.')

    def _touchEmu(self) -> int:
        '''Emulate touch sensors, return a single int value between 0 and 255 with one bit for each sensor.'''
        # The first values come from stored data
        if self._touchDataIndex < len(self._touchData):
            self._touchDataIndex += 1
            return self._touchData[self._touchDataIndex-1]
        else:
            # Appox. 50% of all values should be 0, the rest between 1 and 255:
            val = self.rndGen_touch.randint(1, 10)
            if val <= 5:
                return 0
            else:
                return self.rndGen_touch.randint(1, 255)

    def _touchEmu_wts(self) -> Tuple[float, int]:
        raise Exception(f'ERROR in cpg_scpi: touch_wts() is not implemented in emulation mode.')

    def _uptimeEmu(self) -> float:
        raise Exception(f'ERROR in cpg_scpi: uptime() is not implemented in emulation mode.')




    def _clamp(self, minVal, val, maxVal):
        return max(min(maxVal, val), minVal)

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

