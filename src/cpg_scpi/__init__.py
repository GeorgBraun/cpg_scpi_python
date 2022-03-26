"""CPG SCPI

Educational client library to use Adafruit Circuit Playground via SCPI protocol in Python3.
"""

__version__ = '0.0.3'
__author__ = 'Georg Braun'

import serial    # Docu at https://pythonhosted.org/pyserial/
import serial.tools.list_ports
import sys
import time
import inspect as _inspect
from typing import Tuple

def selfTest(timestamps: bool = False) -> None:
    cpg = CircuitPlayground()
    cpg.selfTest(timestamps)

class CircuitPlayground:
    '''Class to communicate with an Adafruit Circuit Playground via a serial com port and the SCPI protocol'''

    def __init__(self, comport = 'auto', baudrate = 115200) -> None:
        '''Create a CircuitPlayground object and connect to CircuitPlayground via serial com port.'''
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
        '''Measure light intensity and return it as a single int value between 0 and 1023 with 680 corresponding to approx. 1000 lux.'''
        # SI response from CPG:
        # '16105 197' 
        return self._parseIntAfterTimestamp1( self._query('MEAS:LIGHT?', 1) )

    def light_wts(self) -> Tuple[float, int]:
        '''Measure light intensity and return it with timestamp in seconds as a tuple with float and int (timestamp, light)'''
        # SI response from CPG:
        # '16105 197' 
        return self._parseIntWithTimestamp1( self._query('MEAS:LIGHT?', 1) )

    # Microphone:

    def microphone(self) -> int:
        '''Measure microphone value and return it as a single int value between 0 and 1023 with approx. 330 corresponding to silence.'''
        # SI response from CPG:
        # '16105 330'
        return self._parseIntAfterTimestamp1( self._query('MEAS:SOUND?', 1) )

    def microphone_wts(self) -> Tuple[float, int]:
        '''Measure microphone value and return it with timestamp in seconds as a tuple with float and int (timestamp, sound).'''
        # SI response from CPG:
        # '16105 330'
        return self._parseIntWithTimestamp1( self._query('MEAS:SOUND?', 1) )

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
        return self._query(f'OUT:LED {int(value)}', 0)

    def ledDemo(self) -> None:
        return self._query('OUT:DEMO:LED', 0)

    # Timing:

    def wait(self, seconds: float = 0):
        '''Waits for seconds, e.g. 0.1 for 100 milli-seconds'''
        time.sleep(seconds)

    # Self test:

    def _printSelfTestDeliLine(self) -> None:
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    
    def _printSelfTestHeadingWithDeliLine(self, heading) -> None:
        self._printSelfTestDeliLine()
        print(heading)

    def selfTest(self, timestamps: bool = False) -> None:
        if timestamps:
            self._printSelfTestHeadingWithDeliLine(f'cpg_scpi v{__version__}\nRUNNING SOME SELF-TESTS WITH THE CPG with timestamps ...\n')
        else:
            self._printSelfTestHeadingWithDeliLine(f'cpg_scpi v{__version__}\nRUNNING SOME SELF-TESTS WITH THE CPG without timestamps ...\n')
        
        self.test_led()
        self.test_buttonAny(timestamps)
        self.test_temp(timestamps)
        self.test_acc(timestamps)

        self._printSelfTestHeadingWithDeliLine('DONE WITH SELF-TESTS')
        self._printSelfTestDeliLine()

    def test_buttonAny(self, timestamps) -> None:
        if timestamps:
            outHeading = '| count |    timestamp | any button |'
            outFormat =  '| {:5} | {:12.3f} | {!s:10} |'
        else:
            outHeading = '| count | any button |'
            outFormat =  '| {:5} | {!s:10} |'

        self._printSelfTestHeadingWithDeliLine('Button-Self-Test: Press left or right button...')
        print(outHeading)
        self.wait(2)
        count = 20
        for i in range(count):
            result = (count-i, *self.buttonAny_wts()) if timestamps else (count-i, self.buttonAny())
            print(outFormat.format(*result))
            self.wait(0.5)

    def test_temp(self, timestamps) -> None:
        if timestamps:
            outHeading = '| count |    timestamp | temp °C |'
            outFormat =  '| {:5} | {:12.3f} | {:7.2f} |'
        else:
            outHeading = '| count | temp °C |'
            outFormat =  '| {:5} | {:7.2f} |'

        self._printSelfTestHeadingWithDeliLine('Temp-Sensor-Self-Test ...')
        print(outHeading)
        self.wait(2)
        count = 20
        for i in range(count):
            result = (count-i, *self.temp_wts()) if timestamps else (count-i, self.temp())
            print(outFormat.format(*result))
            self.wait(0.5)

    def test_acc(self, timestamps) -> None:
        if timestamps:
            outHeading = '| count |    timestamp | x m/s^2 | y m/s^2 | z m/s^2 |'
            outFormat =  '| {:5} | {:12.3f} | {:7.2f} | {:7.2f} | {:7.2f} |'
            testFunction = self.acc_wts
        else:
            outHeading = '| count | x m/s^2 | y m/s^2 | z m/s^2 |'
            outFormat =  '| {:5} | {:7.2f} | {:7.2f} | {:7.2f} |'
            testFunction = self.acc

        self._printSelfTestHeadingWithDeliLine('Accelerometer-Self-Test ...')
        print(outHeading)
        self.wait(2)
        count = 60
        for i in range(count):
            print(outFormat.format(count-i, *testFunction()))
            self.wait(0.2)

    def test_led(self) -> None:
        '''Flash LEDs and run a short chasing light.'''
        self._printSelfTestHeadingWithDeliLine('LED-Self-Test: Flash LEDs and run a short chasing light.')
        self.test_ledDemo()
        value=1
        for i in range(10):
            self.led(value)
            self.wait(0.2)
            value *= 2
        for i in range(10):
            value //= 2
            self.led(value)
            self.wait(0.2)
        self.test_ledDemo()

    def test_ledDemo(self) -> None:
        '''Flash LEDs three times.'''
        for i in range(3):
            self.ledDemo()
            self.wait(0.2)

    def testAccSpeed(self, iterations: int = 100) -> None:
        '''Measure how long it takes to do an accelerometer measurement.'''
        print(f'Testing acc measurement speed with {iterations} iterations. Please wait ...')
        import timeit
        result = timeit.Timer(stmt=lambda: self.acc(), setup='pass').timeit(number=iterations)
        print(f'Total time: {result:.1f} seconds.')
        print(f'On average {(result*1000/iterations):.1f} ms per measurement.')

    def testLightSpeed(self, iterations: int = 100) -> None:
        '''Measure how long it takes to do a light sensor measurement.'''
        print(f'Testing light measurement speed with {iterations} iterations. Please wait ...')
        import timeit
        result = timeit.Timer(stmt=lambda: self.light(), setup='pass').timeit(number=iterations)
        print(f'Total time: {result:.1f} seconds.')
        print(f'On average {(result*1000/iterations):.1f} ms per measurement.')

    def _testResponseWaitTime(self, iterations: int = 10000) -> None:
        '''Test it the wait time for additional, unexpected responses is long enough.'''
        print(f'Testing Response-Wait-Time with {iterations} iterations ...')
        for i in range(iterations):
            if i%100==0: print('try-count', i)
            try:
                # Request acc measurement values, but do not expect any response, even if the CPG will send one.
                self._query('MEAS:ACC?', 0)
                # If we are still here, we did not get a response. This is bad.
                print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                print('ERROR in testResponseWaitTime(): CPG-Response was too late.')
                print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
            except Exception:
                # The normal behavior is a response, resulting in an exception.
                # This is what we expected. Therefore, just continue.
                pass

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

        self.comPortObj = serial.Serial(self.comPort, self.baudrate, timeout=5) # timeout is for reads
        print(f'Connected to {self.comPortObj.name} with {self.comPortObj.baudrate} baud (bit/second).')
    
    def _findComPort(self) -> None:
        '''Searches COM ports for Adafruit Circuit Playground. Takes the first hit. Aborts the main program if none is found.'''
        x=list(serial.tools.list_ports.grep("adafruit"))
        if len(x)==0:
            print('=====================================================')
            print('ERROR in cpg_scpi: Could not find any serial port for')
            print('                   Adafruit Circuit Playground.')
            print()
            print('Will terminate program.')
            print('=====================================================')
            # self.comPort = None # not useful as long as we exit in the next line.
            sys.exit(1)
        elif len(x)>1:
            self.comPort = x[0].device
            print( '=====================================================')
            print(f'WARNING in cpg_scpi: Found {len(x)} Circuit Playgrounds.')
            print(f'                     Will take the one on {self.comPort}.')
            print( '=====================================================')
        else: # len(x)==1
            self.comPort = x[0].device
            print( '==============================================================')
            print(f'INFO in cpg_scpi: Found Circuit Playgrounds on {self.comPort}')
            print( '==============================================================')



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

