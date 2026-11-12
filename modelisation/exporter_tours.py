# Construit, cuit l'occlusion et exporte chaque tour en GLB compressé.
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outils import *
import tours
ICI = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ICI, "modeles"), exist_ok=True)
choix = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else range(8)
hauteurs = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else range(3)
for i in choix:
    for h in hauteurs:
        demarrer(); random.seed(100 + i * 7 + h)
        t = time.time()
        ob = tours.TOURS[i](h)
        zmax = max(v.co.z for v in ob.data.vertices)
        cuire_ao(ob)
        ko = exporter(ob, os.path.join(ICI, "modeles", f"t{i}_h{h}.glb")) / 1024
        print(f"t{i}_h{h} : {triangles(ob)} triangles, {zmax:.0f} m, {ko:.0f} ko, {time.time() - t:.0f} s", flush=True)
