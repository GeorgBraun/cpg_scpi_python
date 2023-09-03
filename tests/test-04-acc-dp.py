import cpg_scpi
import directplot as dp

print("CPG-Accelerometer")
print("=================")
print()

cpg = cpg_scpi.CircuitPlayground()
dp.init(["CPG"], 3, showMarker=False)
dp.xylabel(0, "Messindex", "Wert")
dp.label(0, "x m/s^2")
dp.label(1, "y m/s^2")
dp.label(2, "z m/s^2")

print('|    i | x m/s^2 | y m/s^2 | z m/s^2 |')

for i in range(1000):
    x, y, z = cpg.acc()
    dp.add(0, i, x, refresh=False)
    dp.add(1, i, y, refresh=False)
    dp.add(2, i, z, refresh=True)
    # print(f'| {i:4} | {x:7.2f} | {y:7.2f} | {z:7.2f} |')
    #cpg.wait(0.05)

print('Fertig. Bitte Plotfenster schließen.')
dp.waitforclose()
