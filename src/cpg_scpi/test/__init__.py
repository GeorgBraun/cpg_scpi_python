'''Functional tests for CPG'''

from .. import CircuitPlayground
from .. import __version__ as CircuitPlaygroundVersion
import time

def funcTest(timestamps: bool = False) -> None:
    cpg = CircuitPlayground()

    if timestamps:
        _printFuncTestHeadingWithDeliLine(f'cpg_scpi v{CircuitPlaygroundVersion}\nRUNNING SOME FUNCTIONAL-TESTS WITH THE CPG with timestamps ...\n')
    else:
        _printFuncTestHeadingWithDeliLine(f'cpg_scpi v{CircuitPlaygroundVersion}\nRUNNING SOME FUNCTIONAL-TESTS WITH THE CPG without timestamps ...\n')
    
    test_led(cpg)
    test_buttonAny(cpg, timestamps)
    test_switch(cpg, timestamps)
    test_temp(cpg, timestamps)
    test_light(cpg, timestamps)
    test_acc(cpg, timestamps)
    test_touch(cpg, timestamps)

    _printFuncTestHeadingWithDeliLine('DONE WITH FUNCTIONAL-TESTS')
    _printFuncTestDeliLine()

def _printCountdown(start: int = 3) -> None:
    for i in range(start, 0, -1):
        print(i, end=" ", flush=True)
        time.sleep(1)
    print('', flush=True)

def _printFuncTestDeliLine() -> None:
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

def _printFuncTestHeadingWithDeliLine(heading) -> None:
    _printFuncTestDeliLine()
    print(heading)

def test_buttonAny(cpg, timestamps) -> None:
    if timestamps:
        outHeading = '| count |    timestamp | any button |'
        outFormat =  '| {:5} | {:12.3f} | {!s:10} |'
    else:
        outHeading = '| count | any button |'
        outFormat =  '| {:5} | {!s:10} |'

    _printFuncTestHeadingWithDeliLine('Button-Test: Press left or right button...')
    print(outHeading)
    _printCountdown(3)
    count = 10
    for i in range(count):
        result = (count-i, *cpg.buttonAny_wts()) if timestamps else (count-i, cpg.buttonAny())
        print(outFormat.format(*result))
        cpg.wait(0.5)

def test_switch(cpg, timestamps) -> None:
    if timestamps:
        outHeading = '| count |    timestamp | switch |'
        outFormat =  '| {:5} | {:12.3f} | {!s:6} |'
    else:
        outHeading = '| count | switch |'
        outFormat =  '| {:5} | {!s:6} |'

    _printFuncTestHeadingWithDeliLine('Switch-Test: Change slider switch position...')
    print(outHeading)
    _printCountdown(3)
    count = 10
    for i in range(count):
        result = (count-i, *cpg.switch_wts()) if timestamps else (count-i, cpg.switch())
        print(outFormat.format(*result))
        cpg.wait(0.5)

def test_temp(cpg, timestamps) -> None:
    if timestamps:
        outHeading = '| count |    timestamp | temp °C |'
        outFormat =  '| {:5} | {:12.3f} | {:7.2f} |'
    else:
        outHeading = '| count | temp °C |'
        outFormat =  '| {:5} | {:7.2f} |'

    _printFuncTestHeadingWithDeliLine('Temp-Sensor-Test ...')
    print(outHeading)
    _printCountdown(3)
    count = 20
    for i in range(count):
        result = (count-i, *cpg.temp_wts()) if timestamps else (count-i, cpg.temp())
        print(outFormat.format(*result))
        cpg.wait(0.5)

def test_light(cpg, timestamps) -> None:
    if timestamps:
        outHeading = '| count |    timestamp | light |'
        outFormat =  '| {:5} | {:12.3f} | {:5} |'
    else:
        outHeading = '| count | light |'
        outFormat =  '| {:5} | {:5} |'

    _printFuncTestHeadingWithDeliLine('Light-Sensor-Test: Move hand over light sensor...')
    print(outHeading)
    _printCountdown(3)
    count = 20
    for i in range(count):
        result = (count-i, *cpg.light_wts()) if timestamps else (count-i, cpg.light())
        print(outFormat.format(*result))
        cpg.wait(0.5)

def test_acc(cpg, timestamps) -> None:
    if timestamps:
        outHeading = '| count |    timestamp | x m/s^2 | y m/s^2 | z m/s^2 |'
        outFormat =  '| {:5} | {:12.3f} | {:7.2f} | {:7.2f} | {:7.2f} |'
        testFunction = cpg.acc_wts
    else:
        outHeading = '| count | x m/s^2 | y m/s^2 | z m/s^2 |'
        outFormat =  '| {:5} | {:7.2f} | {:7.2f} | {:7.2f} |'
        testFunction = cpg.acc

    _printFuncTestHeadingWithDeliLine('Accelerometer-Test: Tilt the CPG board...')
    print(outHeading)
    _printCountdown(3)
    count = 60
    for i in range(count):
        print(outFormat.format(count-i, *testFunction()))
        cpg.wait(0.2)

def test_touch(cpg, timestamps) -> None:
    if timestamps:
        outHeading = '| count |    timestamp | touch |   binary |'
        outFormat =  '| {0:5} | {1:12.3f} | {2:5} | {2:08b} |'
    else:
        outHeading = '| count | touch |   binary |'
        outFormat =  '| {0:5} | {1:5} | {1:08b} |'

    _printFuncTestHeadingWithDeliLine('Touch-Sensor-Test: Touch capacitive sensor pads...')
    print(outHeading)
    _printCountdown(3)
    count = 30
    for i in range(count):
        result = (count-i, *cpg.touch_wts()) if timestamps else (count-i, cpg.touch())
        print(outFormat.format(*result))
        cpg.wait(0.5)

def test_led(cpg) -> None:
    '''Flash LEDs and run a short chasing light.'''
    _printFuncTestHeadingWithDeliLine('LED-Test: Flash LEDs and run a short chasing light...')
    print('|  flashing LEDs... |')
    test_ledDemo(cpg)
    value=1
    print('|  val |       LEDs |')
    for i in range(10):
        print(f'| {value:4} | {value:010b} |')
        cpg.led(value)
        cpg.wait(0.2)
        value <<= 1 # shift 1 bit to the left
    for i in range(10):
        value >>= 1 # shift 1 bit to the right
        print(f'| {value:4} | {value:010b} |')
        cpg.led(value)
        cpg.wait(0.2)
    print('|  flashing LEDs... |')
    test_ledDemo(cpg)

def test_ledDemo(cpg) -> None:
    '''Flash LEDs three times.'''
    for i in range(3):
        cpg.ledDemo()
        cpg.wait(0.2)

def testAccSpeed(cpg, iterations: int = 100) -> None:
    '''Measure how long it takes to do an accelerometer measurement.'''
    print(f'Testing acc measurement speed with {iterations} iterations. Please wait ...')
    import timeit
    result = timeit.Timer(stmt=lambda: cpg.acc(), setup='pass').timeit(number=iterations)
    print(f'Total time: {result:.1f} seconds.')
    print(f'On average {(result*1000/iterations):.1f} ms per measurement.')

def testLightSpeed(cpg, iterations: int = 100) -> None:
    '''Measure how long it takes to do a light sensor measurement.'''
    print(f'Testing light measurement speed with {iterations} iterations. Please wait ...')
    import timeit
    result = timeit.Timer(stmt=lambda: cpg.light(), setup='pass').timeit(number=iterations)
    print(f'Total time: {result:.1f} seconds.')
    print(f'On average {(result*1000/iterations):.1f} ms per measurement.')

def _testResponseWaitTime(cpg, iterations: int = 10000) -> None:
    '''Test it the wait time for additional, unexpected responses is long enough.'''
    print(f'Testing Response-Wait-Time with {iterations} iterations ...')
    for i in range(iterations):
        if i%100==0: print('try-count', i)
        try:
            # Request acc measurement values, but do not expect any response, even if the CPG will send one.
            cpg._query('MEAS:ACC?', 0)
            # If we are still here, we did not get a response. This is bad.
            print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
            print('ERROR in testResponseWaitTime(): CPG-Response was too late.')
            print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        except Exception:
            # The normal behavior is a response, resulting in an exception.
            # This is what we expected. Therefore, just continue.
            pass

