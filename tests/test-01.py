import cpg_scpi
from time import sleep

def main():
    cpg = cpg_scpi.CircuitPlayground()

    if cpg.is_open:
        repeat(what=cpg.buttonAny, count=10, delaySeconds=1)
        repeat(what=cpg.buttonLeft, count=10, delaySeconds=1)
        repeat(what=cpg.buttonRight, count=10, delaySeconds=1)
        repeat(what=cpg.switch, count=10, delaySeconds=1)
        repeat(what=cpg.temp, count=10, delaySeconds=1)
        repeat(what=cpg.acc, count=10, delaySeconds=1)
        repeat(what=cpg.light, count=10, delaySeconds=1)
        repeat(what=cpg.sound, count=10, delaySeconds=1)
        repeat(what=cpg.capSense, count=10, delaySeconds=1)
        repeat(what=cpg.capTap, count=10, delaySeconds=1)
        repeat(what=cpg.time, count=10, delaySeconds=1)

        cpg.close()
        print(cpg.is_open)

def repeat(what, count, delaySeconds=0):
    print(f'Repeating {count} times: {what}')
    for i in range(count):
        print(what())
        if delaySeconds>0: sleep(delaySeconds)
        

main()
