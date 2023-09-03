import cpg_scpi
import directplot as dp

print("CPG-Mikrofon")
print("============")
print()

cpg = cpg_scpi.CircuitPlayground()

dp.init(["CPG"], 1, showMarker=False)
dp.xylabel(0, "Messindex", "Wert")
dp.label(0, "Mic. [0...1023]")

# print('|   i | Mic. |')

for i in range(1000):
    mic = cpg.microphone()
    dp.add(0, i, mic)
    # print(f'| {i:3} | {mic:4} |')
    # cpg.wait(1)

print('Fertig. Bitte Plotfenster schließen.')
dp.waitforclose()
