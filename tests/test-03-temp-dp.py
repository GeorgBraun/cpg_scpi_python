import cpg_scpi
import directplot as dp

print("CPG-Temperatursensor")
print("====================")
print()

cpg = cpg_scpi.CircuitPlayground()

dp.init(["CPG"], 1, showMarker=False)
dp.xylabel(0, "Messindex", "Wert")
dp.label(0, "Temp °C")

print('|   i | t °C |')

for i in range(1000):
    temperature = cpg.temp()
    dp.add(0, i, temperature)
    print(f'| {i:3} | {temperature:4.1f} |')
    # print(f'| {i:3} | {temperature} |')
    # cpg.wait(1)

print('Fertig. Bitte Plotfenster schließen.')
dp.waitforclose()
