import cpg_scpi; cpg = cpg_scpi.CircuitPlayground()

cpg.close()
del cpg
del cpg_scpi # does not really help


import cpg_scpi
cpg_scpi.selfTest(True)
cpg_scpi.selfTest()

# cmd/terminal:
# python -m cpg_scpi
