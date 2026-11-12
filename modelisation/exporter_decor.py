import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outils import *
import decor
ICI = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ICI, "modeles"), exist_ok=True)
noms = sys.argv[1].split(",") if len(sys.argv) > 1 else list(decor.DECOR)
for nom in noms:
    demarrer(); random.seed(sum(map(ord, nom)))
    t = time.time()
    ob = decor.DECOR[nom]()
    zmax = max(v.co.z for v in ob.data.vertices)
    petit = nom.startswith(("arbre", "lampadaire", "voiture", "bateau"))
    cuire_ao(ob, distance=(2.5 if petit else 9.0), plancher=(0.5 if petit else 0.38), sol=(nom != "bateau"))
    ko = exporter(ob, os.path.join(ICI, "modeles", f"{nom}.glb")) / 1024
    print(f"{nom} : {triangles(ob)} triangles, {zmax:.0f} m, {ko:.0f} ko, {time.time() - t:.0f} s", flush=True)
