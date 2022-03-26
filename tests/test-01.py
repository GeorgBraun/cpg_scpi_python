import cpg_scpi
from time import sleep

def main():
    cpg = cpg_scpi.CircuitPlayground()

    cpg.test_ledDemo()
    # cpg.test_led()
    # value = cpg.acc()
    # print(f'acc: {value}')
    # value = cpg.light()
    # print(f'light: {value}')

    cpg.close()
    print()
    print(f'Closed connection to CPG. {cpg.is_open=}')

main()
