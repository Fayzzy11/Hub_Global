# Boîte à outils de modélisation (Blender sans interface) pour le quartier du hub.
# Unités : mètres. Axe Z vers le haut. L'entrée des tours regarde vers -Y.
import bpy, bmesh, math, random, os
from mathutils import Vector

scene = None
MATS = {}

def demarrer():
    global scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    MATS.clear()
    # Couleurs d'aperçu seulement : dans l'app, les matériaux sont recréés d'après leur nom.
    for nom, coul, metal, rug in [
        ("verre_a", (0.22, 0.36, 0.48), 1.0, 0.03), ("verre_b", (0.26, 0.42, 0.55), 1.0, 0.05),
        ("verre_c", (0.30, 0.47, 0.60), 1.0, 0.08), ("verre_d", (0.34, 0.50, 0.62), 1.0, 0.04),
        ("verre_e", (0.55, 0.62, 0.66), 0.6, 0.25),
        ("hall", (0.10, 0.13, 0.16), 1.0, 0.05), ("alu", (0.66, 0.68, 0.70), 1.0, 0.32),
        ("noir", (0.035, 0.038, 0.042), 0.9, 0.38), ("bronze", (0.42, 0.29, 0.16), 1.0, 0.36),
        ("pierre", (0.74, 0.70, 0.62), 0.0, 0.78), ("beton", (0.86, 0.86, 0.84), 0.0, 0.62),
        ("toit", (0.23, 0.23, 0.24), 0.0, 0.9), ("tech", (0.50, 0.52, 0.54), 0.6, 0.55),
        ("accent", (0.85, 0.55, 0.10), 0.2, 0.4), ("lumiere", (1.0, 0.93, 0.78), 0.0, 0.4),
        ("vegetal", (0.10, 0.26, 0.07), 0.0, 0.9), ("ecorce", (0.12, 0.085, 0.06), 0.0, 0.9),
        ("marbre", (0.90, 0.89, 0.86), 0.0, 0.35), ("zinc", (0.42, 0.45, 0.49), 0.5, 0.5),
        ("rouge", (0.75, 0.06, 0.04), 0.1, 0.4), ("eau", (0.10, 0.25, 0.35), 0.9, 0.08),
        ("carrosserie", (0.8, 0.8, 0.8), 0.6, 0.3), ("pneu", (0.02, 0.02, 0.02), 0.0, 0.9),
        ("fer", (0.30, 0.24, 0.19), 0.6, 0.6), ("toile", (0.95, 0.95, 0.93), 0.0, 0.7),
        ("chaussee", (0.07, 0.075, 0.085), 0.0, 0.9), ("coque", (0.93, 0.93, 0.91), 0.1, 0.5),
    ]:
        m = bpy.data.materials.new(nom)
        if not m.node_tree:
            m.use_nodes = True
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b is None:
            b = m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            o = m.node_tree.nodes.new('ShaderNodeOutputMaterial')
            m.node_tree.links.new(b.outputs[0], o.inputs[0])
        b.inputs["Base Color"].default_value = (*coul, 1)
        b.inputs["Metallic"].default_value = metal
        b.inputs["Roughness"].default_value = rug
        MATS[nom] = m
    return scene

VERRES = ["verre_a", "verre_b", "verre_c", "verre_d", "verre_e"]
POIDS = [0.31, 0.29, 0.25, 0.11, 0.04]
def verre():
    return random.choices(VERRES, POIDS)[0]

def V2(x, y):
    return Vector((x, y))

K4 = ((-1, -1), (1, -1), (1, 1), (-1, 1))

class Maillage:
    """Un seul maillage par objet, plusieurs matériaux : peu d'appels de dessin dans l'app."""
    def __init__(self, nom):
        self.nom, self.bm, self.mats = nom, bmesh.new(), []
    def mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)
    def face(self, pts, m):
        f = self.bm.faces.new([self.bm.verts.new(tuple(p)) for p in pts])
        f.material_index = self.mi(m)
    def boite2(self, c0, u0, n0, c1, u1, n1, a, b, z0, z1, m, sans=""):
        """Boîte entre deux sections (bas et haut) : c centre, u et n axes unitaires, a et b demi-côtés.
        sans : faces omises, b bas, h haut, a arrière (-n), f avant (+n), g (-u), d (+u)."""
        lo = [(c0 + u0 * (a * su) + n0 * (b * sn)) for su, sn in K4]
        hi = [(c1 + u1 * (a * su) + n1 * (b * sn)) for su, sn in K4]
        lo = [(p.x, p.y, z0) for p in lo]
        hi = [(p.x, p.y, z1) for p in hi]
        faces = {"b": lo[::-1], "h": hi}
        for i, k in enumerate("adfg"):
            faces[k] = [lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]]
        inverse = u0.x * n0.y - u0.y * n0.x < 0
        for k, f in faces.items():
            if k not in sans:
                self.face(f[::-1] if inverse else f, m)
    def boite(self, c, u, n, a, b, z0, z1, m, sans=""):
        self.boite2(c, u, n, c, u, n, a, b, z0, z1, m, sans)
    def cube(self, x, y, sx, sy, z0, z1, m, sans="b"):
        self.boite(V2(x, y), V2(1, 0), V2(0, 1), sx / 2, sy / 2, z0, z1, m, sans)
    def cyl(self, x, y, r0, r1, z0, z1, m, n=12, sans="b", ry=1.0):
        a = [2 * math.pi * i / n for i in range(n)]
        lo = [(x + r0 * math.cos(t), y + r0 * ry * math.sin(t), z0) for t in a]
        hi = [(x + r1 * math.cos(t), y + r1 * ry * math.sin(t), z1) for t in a]
        for i in range(n):
            j = (i + 1) % n
            self.face([lo[i], lo[j], hi[j], hi[i]], m)
        if "h" not in sans and r1 > 0.01:
            self.face(hi, m)
        if "b" not in sans:
            self.face(lo[::-1], m)
    def barre(self, p, q, ep, m, ep2=None):
        """Barre de section rectangulaire entre deux points de l'espace."""
        p, q = Vector(p), Vector(q)
        d = (q - p).normalized()
        ref = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
        s = d.cross(ref).normalized() * (ep / 2)
        t = d.cross(s).normalized() * ((ep2 or ep) / 2)
        lo = [p + s * a + t * b for a, b in K4]
        hi = [q + s * a + t * b for a, b in K4]
        fs = [lo[::-1], hi] + [[lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]] for i in range(4)]
        if s.cross(t).dot(d) < 0:
            fs = [f[::-1] for f in fs]
        for f in fs:
            self.face(f, m)
    def panneau(self, p0, p1, p2, p3, m=None, pli=0.07):
        """Vitrage : chaque panneau est très légèrement incliné, pour que les reflets varient comme sur une vraie façade."""
        p = [Vector(x) for x in (p0, p1, p2, p3)]
        n = (p[1] - p[0]).cross(p[3] - p[0])
        if n.length > 1e-6 and pli:
            n.normalize()
            a, b = random.uniform(-pli, pli), random.uniform(-pli, pli)
            for q, (s, t) in zip(p, ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))):
                q += n * (a * s + b * t)
        self.face(p, m or verre())
    def face_n(self, pts, n, m):
        """Face orientée d'office du côté de la normale voulue."""
        p = [Vector(x) for x in pts]
        if (p[1] - p[0]).cross(p[2] - p[0]).dot(Vector(n)) < 0:
            p.reverse()
        self.face(p, m)
    def blob(self, x, y, z, r, m, sub=2, bosses=0.18, sz=1.0, lisse=True):
        """Masse arrondie irrégulière (houppier d'arbre, nuage) : icosphère aux sommets déplacés."""
        from mathutils import Matrix
        avant = set(self.bm.faces)
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=1.0)
        for v in res["verts"]:
            k = r * random.uniform(1 - bosses, 1 + bosses)
            v.co = Vector((x + v.co.x * k, y + v.co.y * k, z + v.co.z * k * sz))
        mi = self.mi(m)
        for f in set(self.bm.faces) - avant:
            f.material_index = mi
            f.smooth = lisse
    def profil(self, pts, y0, y1, m, m_flancs=None):
        """Extrusion le long de Y d'un profil fermé dessiné dans le plan XZ (sens trigonométrique vu depuis -Y)."""
        n = len(pts)
        for i in range(n):
            (xa, za), (xb, zb) = pts[i], pts[(i + 1) % n]
            self.face_n([(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], (zb - za, 0, -(xb - xa)), m)
        self.face_n([(x, y0, z) for x, z in pts], (0, -1, 0), m_flancs or m)
        self.face_n([(x, y1, z) for x, z in pts], (0, 1, 0), m_flancs or m)
    def dalle(self, poly, z, m, dessous=False):
        pts = [(p.x, p.y, z) for p in poly]
        self.face(pts[::-1] if dessous else pts, m)
    def objet(self):
        me = bpy.data.meshes.new(self.nom)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(MATS[m])
        ob = bpy.data.objects.new(self.nom, me)
        scene.collection.objects.link(ob)
        return ob

# ---------- emprises (polygones dans le sens trigonométrique) ----------
def rect(w, d):
    return [V2(-w / 2, -d / 2), V2(w / 2, -d / 2), V2(w / 2, d / 2), V2(-w / 2, d / 2)]
def pans(w, d, c):
    return [V2(-w / 2 + c, -d / 2), V2(w / 2 - c, -d / 2), V2(w / 2, -d / 2 + c), V2(w / 2, d / 2 - c),
            V2(w / 2 - c, d / 2), V2(-w / 2 + c, d / 2), V2(-w / 2, d / 2 - c), V2(-w / 2, -d / 2 + c)]
def rond(rx, ry=None, n=32, dec=0.0):
    ry = ry or rx
    return [V2(rx * math.cos(2 * math.pi * (i + dec) / n), ry * math.sin(2 * math.pi * (i + dec) / n)) for i in range(n)]
def ech(poly, s, t=None):
    t = s if t is None else t
    return [V2(p.x * s, p.y * t) for p in poly]
def place(poly, x, y):
    return [p + V2(x, y) for p in poly]
def tourne(poly, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [V2(p.x * c - p.y * s, p.x * s + p.y * c) for p in poly]
def melange(pa, pb, k):
    return [a.lerp(b, k) for a, b in zip(pa, pb)]
def gonfle(poly, s):
    """Agrandit un polygone autour de son centre."""
    x0, y0, x1, y1 = boite_englobante(poly)
    c = V2((x0 + x1) / 2, (y0 + y1) / 2)
    return [c + (p - c) * s for p in poly]
def boite_englobante(poly):
    xs, ys = [p.x for p in poly], [p.y for p in poly]
    return min(xs), min(ys), max(xs), max(ys)
def arete(poly, i):
    p0, p1 = poly[i], poly[(i + 1) % len(poly)]
    e = p1 - p0
    L = e.length
    u = e / L
    return p0, p1, L, u, V2(u.y, -u.x)

# ---------- façades ----------
STYLES = {
    # trame : largeur d'une travée ; all : hauteur d'allège ; dep : saillie de l'allège ; lame : profondeur des meneaux
    "rideau":   dict(trame=3.0, all=0.9, dep=0.12, m_all="noir",   lame=0.40, ep=0.22, m_lame="alu",    pas=1),
    "ailettes": dict(trame=3.0, all=0.8, dep=0.12, m_all="noir",   lame=1.00, ep=0.26, m_lame="bronze", pas=1),
    "bandes":   dict(trame=3.2, all=1.5, dep=0.50, m_all="beton",  lame=0.0,  ep=0.0,  m_lame="noir",   pas=1),
    "piles":    dict(trame=3.0, all=1.1, dep=0.15, m_all="bronze", lame=0.85, ep=0.95, m_lame="pierre", pas=2),
    "lisse":    dict(trame=3.0, all=0.7, dep=0.06, m_all="noir",   lame=0.14, ep=0.14, m_lame="noir",   pas=1),
    "resille":  dict(trame=3.4, all=0.8, dep=0.10, m_all="noir",   lame=0.0,  ep=0.0,  m_lame="alu",    pas=1),
}

def niveaux(M, forme, z0, nfl, fh, style, meca=(), droit=None, lames_par_etage=False, pleins=None, double=False):
    """Empile nfl étages. forme(k) rend le polygone au niveau k (0..nfl) ; s'il ne change pas, les meneaux
    filent d'un seul tenant. meca : indices d'étages techniques (ventelles au lieu de vitrage)."""
    st = STYLES[style] if isinstance(style, str) else style
    polys = [forme(k) for k in range(nfl + 1)]
    if droit is None:
        droit = all((a - b).length < 1e-6 for a, b in zip(polys[0], polys[-1]))
    n = len(polys[0])
    for i in range(n):
        p0, p1, L, u, nr = arete(polys[0], i)
        nb = max(1, round(L / st["trame"]))
        for f in range(nfl):
            a0, a1, La, ua, na = arete(polys[f], i)
            b0, b1, Lb, ub, nb_ = arete(polys[f + 1], i)
            zf = z0 + f * fh
            mid = (a0 + a1) / 2
            if pleins and i in pleins:
                M.face([(a0.x, a0.y, zf), (a1.x, a1.y, zf), (b1.x, b1.y, zf + fh), (b0.x, b0.y, zf + fh)], pleins[i])
                continue
            if double:  # écran de couronnement : visible aussi depuis l'intérieur
                c0, c1, d0, d1 = a0 - na * 0.06, a1 - na * 0.06, b0 - nb_ * 0.06, b1 - nb_ * 0.06
                M.face([(c1.x, c1.y, zf), (c0.x, c0.y, zf), (d0.x, d0.y, zf + fh), (d1.x, d1.y, zf + fh)], "noir")
            if f in meca:
                # étage technique : bandeau sombre en retrait et trois ventelles filantes
                M.face([(a0.x, a0.y, zf), (a1.x, a1.y, zf), (b1.x, b1.y, zf + fh), (b0.x, b0.y, zf + fh)], "noir")
                for kz in (0.2, 0.5, 0.8):
                    M.boite(mid + na * 0.12, ua, na, La / 2, 0.12, zf + fh * kz - 0.22, zf + fh * kz + 0.22, "tech", "agd")
                continue
            if st["all"] > 0:
                M.boite(mid + na * (st["dep"] / 2), ua, na, La / 2 + (0.02 if n <= 8 else 0), st["dep"] / 2, zf, zf + st["all"], st["m_all"], "agd" if n > 8 else "a")
            ta = st["all"] / fh
            for k in range(nb):
                s0, s1 = k / nb, (k + 1) / nb
                q0, q1 = a0.lerp(a1, s0), a0.lerp(a1, s1)
                r0, r1 = b0.lerp(b1, s0), b0.lerp(b1, s1)
                q0, q1 = q0.lerp(r0, ta), q1.lerp(r1, ta)
                M.panneau((q0.x, q0.y, zf + st["all"]), (q1.x, q1.y, zf + st["all"]), (r1.x, r1.y, zf + fh), (r0.x, r0.y, zf + fh))
            if st["lame"] > 0 and (not droit or lames_par_etage):
                for k in range(0, nb + (0 if n > 8 else 1), st["pas"]):
                    s = k / nb
                    M.boite2(a0.lerp(a1, s) + na * (st["lame"] / 2), ua, na, b0.lerp(b1, s) + nb_ * (st["lame"] / 2), ub, nb_,
                             st["ep"] / 2, st["lame"] / 2, zf, zf + fh, st["m_lame"], "abh")
        if pleins and i in pleins:
            continue
        if st["lame"] > 0 and droit and not lames_par_etage:
            for k in range(0, nb + (0 if n > 8 else 1), st["pas"]):
                c = p0 + u * (L * k / nb) + nr * (st["lame"] / 2)
                M.boite(c, u, nr, st["ep"] / 2, st["lame"] / 2, z0, z0 + nfl * fh, st["m_lame"], "ab")
    return z0 + nfl * fh, polys[-1]

def acrotere(M, poly, z, m="noir", h=1.3, ep=0.4):
    for i in range(len(poly)):
        p0, p1, L, u, nr = arete(poly, i)
        M.boite((p0 + p1) / 2 - nr * (ep / 2 - 0.05), u, nr, L / 2 + 0.05, ep / 2, z, z + h, m, "b")

def toiture(M, poly, z, m_par="noir", h=1.3, tech=4, edicule=True, helipad=False, jardin=False, grue=True, centre=None, etendue=None):
    """Toit : acrotère, étanchéité, édicule technique, groupes froid, gaines, nacelle de nettoyage, hélisurface ou jardin."""
    acrotere(M, poly, z, m_par, h)
    M.dalle(poly, z + 0.05, "toit")
    x0, y0, x1, y1 = boite_englobante(poly)
    cx, cy = centre or ((x0 + x1) / 2, (y0 + y1) / 2)
    w, d = etendue or ((x1 - x0) * 0.62, (y1 - y0) * 0.62)
    if jardin:
        M.cube(cx, cy, w * 0.9, d * 0.9, z + 0.05, z + 0.45, "vegetal")
        for _ in range(5):
            M.cyl(cx + random.uniform(-w, w) * 0.38, cy + random.uniform(-d, d) * 0.38, 1.6, 1.1, z + 0.45, z + 3.0, "vegetal", 7)
        return z + 3
    haut = z + h
    if edicule:
        ew, ed, eh = w * 0.42, d * 0.42, random.uniform(3.6, 5.0)
        M.cube(cx, cy, ew, ed, z, z + eh, "tech")
        M.cube(cx, cy, ew + 0.5, ed + 0.5, z + eh, z + eh + 0.3, "noir")
        M.cube(cx, cy, ew + 0.06, ed + 0.06, z + eh * 0.35, z + eh * 0.75, "noir", "bh")
        haut = z + eh + 0.3
    for _ in range(tech):
        for _essai in range(12):
            px, py = cx + random.uniform(-w, w) / 2, cy + random.uniform(-d, d) / 2
            if not edicule or abs(px - cx) > w * 0.29 or abs(py - cy) > d * 0.29:
                break
        sx, sy, sh = random.uniform(2.2, 4.2), random.uniform(2.2, 4.2), random.uniform(1.4, 2.4)
        M.cube(px, py, sx, sy, z + 0.3, z + 0.3 + sh, "tech")
        M.cyl(px, py, min(sx, sy) * 0.36, min(sx, sy) * 0.36, z + 0.3 + sh, z + 0.5 + sh, "noir", 10)
    # gaine
    M.cube(cx, cy - d * 0.36, w * 0.8, 0.7, z + 0.3, z + 1.0, "alu")
    if grue:
        gx, gy = cx + w * 0.42, cy + d * 0.42
        M.cube(gx, gy, 2.4, 1.8, z + 0.2, z + 2.0, "alu")
        M.barre((gx, gy, z + 2.0), (gx + 5.5, gy + 3.5, z + 4.6), 0.45, "alu")
    if helipad:
        hz = (haut if edicule else z) + 2.2
        M.cyl(cx, cy, 9.5, 9.5, hz, hz + 0.5, "beton", 28, "")
        M.cyl(cx, cy, 7.4, 7.4, hz + 0.5, hz + 0.56, "accent", 28)
        M.cyl(cx, cy, 6.6, 6.6, hz + 0.56, hz + 0.6, "beton", 28)
        M.cube(cx - 1.6, cy, 0.7, 4.4, hz + 0.6, hz + 0.66, "accent")
        M.cube(cx + 1.6, cy, 0.7, 4.4, hz + 0.6, hz + 0.66, "accent")
        M.cube(cx, cy, 3.2, 0.7, hz + 0.6, hz + 0.66, "accent")
        for a in range(4):
            M.cyl(cx + 6 * math.cos(a * 1.5708 + .78), cy + 6 * math.sin(a * 1.5708 + .78), 0.3, 0.3, z, hz, "alu", 6)
        haut = hz + 0.7
    return haut

def socle(M, poly, z0, h, trame=6.0, m_pile="pierre", marches=True, auvent=True, m_bandeau=None):
    """Rez-de-chaussée double hauteur : hall vitré (éclairé la nuit), piles, bandeau, emmarchement, auvent et portes."""
    n = len(poly)
    if marches:
        for k, sc in enumerate((1.22, 1.14, 1.07)):
            pp = gonfle(poly, sc)
            zb, zh = z0 + k * 0.45, z0 + (k + 1) * 0.45
            for i in range(n):
                p0, p1, L, u, nr = arete(pp, i)
                M.face([(p0.x, p0.y, zb), (p1.x, p1.y, zb), (p1.x, p1.y, zh), (p0.x, p0.y, zh)], "pierre")
            M.dalle(pp, zh, "pierre")
        z0 += 1.35
    front, best = 0, 9
    for i in range(n):
        p0, p1, L, u, nr = arete(poly, i)
        if nr.y < best and L > 6:
            best, front = nr.y, i
    for i in range(n):
        p0, p1, L, u, nr = arete(poly, i)
        nb = max(1, round(L / trame))
        for k in range(nb):
            a, b = p0.lerp(p1, k / nb), p0.lerp(p1, (k + 1) / nb)
            M.panneau((a.x, a.y, z0), (b.x, b.y, z0), (b.x, b.y, z0 + h - 1.2), (a.x, a.y, z0 + h - 1.2), "hall", 0.02)
            M.boite((a + b) / 2 + nr * 0.06, u, nr, (b - a).length / 2, 0.06, z0 + (h - 1.2) * 0.55, z0 + (h - 1.2) * 0.55 + 0.16, "noir", "agd")
        for k in range(nb + (0 if n > 8 else 1)):
            M.boite(p0.lerp(p1, k / nb) + nr * 0.35, u, nr, 0.5, 0.5, z0, z0 + h - 1.2, m_pile, "bh")
        M.boite((p0 + p1) / 2 + nr * 0.35, u, nr, L / 2 + (0.5 if n <= 8 else 0), 0.55, z0 + h - 1.2, z0 + h, m_bandeau or m_pile, "a" if n <= 8 else "agd")
        if i == front and auvent:
            c = (p0 + p1) / 2
            larg = min(L * 0.5, 16)
            M.boite(c + nr * 3.2, u, nr, larg / 2, 3.2, z0 + 4.6, z0 + 4.95, "noir")
            M.boite(c + nr * 3.2, u, nr, larg / 2 - 0.3, 2.9, z0 + 4.55, z0 + 4.6, "lumiere", "h")
            for s in (-1, 1):
                M.boite(c + u * (s * (larg / 2 - 0.6)) + nr * 5.8, u, nr, 0.14, 0.14, z0, z0 + 4.6, "alu", "bh")
                M.boite(c + u * (s * 1.7) + nr * 0.25, u, nr, 1.5, 0.2, z0, z0 + 3.2, "noir", "b")
                M.boite(c + u * (s * 1.7) + nr * 0.5, u, nr, 1.25, 0.03, z0 + 0.2, z0 + 3.0, "lumiere", "ba")
            M.boite(c + nr * 0.35, u, nr, 3.4, 0.3, z0 + 3.2, z0 + 3.5, "accent", "b")
    return z0 + h

# ---------- cuisson de l'occlusion ambiante et export ----------
_DIRS = None
def _directions(n):
    """Rayons répartis sur l'hémisphère, pondérés par le cosinus (spirale de Fibonacci)."""
    global _DIRS
    if _DIRS is None or len(_DIRS) != n:
        _DIRS = []
        for i in range(n):
            r = math.sqrt((i + 0.5) / n)
            a = i * 2.39996323
            _DIRS.append((r * math.cos(a), r * math.sin(a), math.sqrt(max(0.0, 1 - r * r))))
    return _DIRS

def cuire_ao(ob, rayons=20, distance=9.0, plancher=0.38, sol=True):
    """Occlusion ambiante par lancer de rayons, stockée dans les couleurs de sommets : les creux, les dessous
    de débords et les pieds de façade sont assombris, sans aucun coût à l'affichage dans l'app."""
    from mathutils.bvhtree import BVHTree
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    if sol:
        bm.faces.new([bm.verts.new(p) for p in ((-500, -500, -0.02), (500, -500, -0.02), (500, 500, -0.02), (-500, 500, -0.02))])
    arbre = BVHTree.FromBMesh(bm)
    bm.free()
    ca = me.color_attributes.new("Col", 'BYTE_COLOR', 'CORNER')
    me.color_attributes.active_color = ca
    dirs = _directions(rayons)
    lancer = arbre.ray_cast
    data = ca.data
    for poly in me.polygons:
        n = poly.normal
        c = poly.center
        t = n.cross(Vector((0, 0, 1)))
        if t.length < 1e-4:
            t = Vector((1, 0, 0))
        t.normalize()
        b = n.cross(t)
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            ao = 0.0
            for retrait in (0.2, 0.46):  # si le coin est enfoui dans une pièce voisine, on mesure un peu plus loin du bord
                p = v + (c - v) * retrait + n * 0.07
                occ = 0.0
                for dx, dy, dz in dirs:
                    hit = lancer(p, t * dx + b * dy + n * dz, distance)
                    if hit[0] is not None:
                        occ += 1.0 - hit[3] / distance
                ao = max(ao, 1.0 - occ / rayons)
                if ao > 0.55:
                    break
            val = plancher + (1 - plancher) * ao
            data[li].color = (val, val, val, 1.0)

def exporter(ob, chemin, draco=True):
    for o in scene.objects:
        o.select_set(o == ob)
    bpy.context.view_layer.objects.active = ob
    props = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    args = dict(filepath=chemin, export_format='GLB', use_selection=True, export_yup=True, export_apply=True,
                export_texcoords=False, export_normals=True, export_animations=False, export_cameras=False, export_lights=False)
    if "export_vertex_color" in props:
        args["export_vertex_color"] = 'ACTIVE'
    if "export_all_vertex_colors" in props:
        args["export_all_vertex_colors"] = False
    if "export_active_vertex_color_when_no_material" in props:
        args["export_active_vertex_color_when_no_material"] = True
    if draco:
        args.update(export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
                    export_draco_position_quantization=14, export_draco_normal_quantization=9, export_draco_color_quantization=8)
    bpy.ops.export_scene.gltf(**args)
    return os.path.getsize(chemin)

def triangles(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)
