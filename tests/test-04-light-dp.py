import cpg_scpi
import directplot as dp

print("CPG-Beleuchtungssensor")
print("======================")
print()

cpg = cpg_scpi.CircuitPlayground()

dp.init(["CPG"], 1, showMarker=False)
dp.xylabel(0, "Messindex", "Wert")
dp.label(0, "Bel. [0...1023]")

# print('|   i | Bel. |')

for i in range(1000):
    light = cpg.light()
    dp.add(0, i, light)
    # print(f'| {i:3} | {light:4} |')
    # cpg.wait(1)

print('Fertig. Bitte Plotfenster schließen.')
dp.waitforclose()
