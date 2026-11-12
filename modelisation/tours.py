# Les huit silhouettes de tours du quartier, chacune en trois hauteurs (0 courte, 1 moyenne, 2 haute).
from outils import *

FH = 3.9
def N(h):
    return (19, 30, 41)[h]

def ceinture(M, poly, z0, z1, dep, m):
    for i in range(len(poly)):
        p0, p1, L, u, nr = arete(poly, i)
        M.boite((p0 + p1) / 2 + nr * (dep / 2), u, nr, L / 2 + dep * 0.45, dep / 2, z0, z1, m, "a")

def ecran(M, poly, z, etages=2, trame=3.0):
    """Couronnement vitré qui masque les équipements du toit."""
    return niveaux(M, lambda k: poly, z, etages, FH, dict(STYLES["lisse"], all=0.0, trame=trame), double=True)[0]

def t0_fuseau(h):
    """Tour carrée à pans coupés, meneaux d'aluminium, sommet effilé et flèche."""
    M = Maillage("t0")
    base = pans(37, 37, 6)
    z = socle(M, gonfle(base, 1.1), 0, 9.5)
    n = N(h); nc = 6 + h; n1 = n - nc
    z, _ = niveaux(M, lambda k: base, z, n1, FH, "rideau", meca={n1 // 2})
    ceinture(M, base, z - 0.5, z + 0.5, 0.55, "accent")
    haut = ech(base, 0.36)
    z, top = niveaux(M, lambda k: melange(base, haut, (k / nc) ** 1.2), z, nc, FH, "lisse")
    for i in (1, 3, 5, 7):  # arêtiers du sommet
        a0, a1, _, _, na = arete(base, i); b0, b1, _, _, nb = arete(top, i)
        M.barre(((a0.x + a1.x) / 2 + na.x * .3, (a0.y + a1.y) / 2 + na.y * .3, z - nc * FH), ((b0.x + b1.x) / 2 + nb.x * .3, (b0.y + b1.y) / 2 + nb.y * .3, z), 0.7, "alu")
    acrotere(M, top, z, "alu", 0.9); M.dalle(top, z + 0.05, "toit")
    M.cyl(0, 0, 2.2, 2.2, z, z + 2.4, "tech", 10)
    M.cyl(0, 0, 1.0, 0.45, z + 2.4, z + 13, "alu", 8)
    M.cyl(0, 0, 0.45, 0.1, z + 13, z + 30, "alu", 6)
    M.cyl(0, 0, 1.5, 1.5, z + 6, z + 6.6, "accent", 10, "")
    return M.objet()

def t1_ellipse(h):
    """Tour elliptique à bandeaux clairs filants, écran de verre en couronne, hélisurface."""
    M = Maillage("t1")
    base = rond(23, 15.5, 36)
    z = socle(M, gonfle(base, 1.07), 0, 9, trame=5, m_pile="beton")
    n = N(h)
    z, _ = niveaux(M, lambda k: base, z, n, FH, "bandes", meca={n // 2} if h else ())
    zt = z
    z = ecran(M, base, z, 2, 3.2)
    ceinture(M, base, z, z + 0.55, 0.5, "accent")
    toiture(M, ech(base, 0.96), zt, "beton", 0.5, tech=3, helipad=(h == 2), grue=(h != 2))
    return M.objet()

def t2_cristal(h):
    """Cristal hexagonal qui s'affine vers le haut, tenu par une résille de poutres diagonales."""
    M = Maillage("t2")
    n = N(h) + 1
    b0, b1 = rond(24.5, 24.5, 6, 0.5), rond(15.5, 15.5, 6, 0.5)
    zs = socle(M, gonfle(b0, 1.06), 0, 9.5, trame=6.2, m_pile="noir", m_bandeau="alu")
    forme = lambda k: melange(b0, b1, k / n)
    z, top = niveaux(M, forme, zs, n, FH, "resille")
    mod = 6
    for i in range(6):
        for k0 in range(0, n, mod):
            k1 = min(n, k0 + mod)
            A0, A1, _, _, na = arete(forme(k0), i); B0, B1, _, _, nb = arete(forme(k1), i)
            za, zb = zs + k0 * FH, zs + k1 * FH
            P = lambda p, nn, zz: (p.x + nn.x * 0.4, p.y + nn.y * 0.4, zz)
            M.barre(P(A0, na, za), P(B1, nb, zb), 0.9, "beton", 0.6)
            M.barre(P(A1, na, za), P(B0, nb, zb), 0.9, "beton", 0.6)
            M.barre(P(A0, na, za), P(A1, na, za), 0.8, "beton", 0.6)
            M.barre((A0.x * 1.012, A0.y * 1.012, za), (B0.x * 1.012, B0.y * 1.012, zb), 1.3, "beton")
    ceinture(M, top, z - 0.4, z + 0.9, 0.6, "accent")
    toiture(M, ech(top, 0.97), z, "alu", 1.1, tech=2)
    return M.objet()

def t3_jumelles(h):
    """Deux lames jumelles de hauteurs différentes sur un socle commun, reliées par des passerelles."""
    M = Maillage("t3")
    n = N(h)
    pod = rect(46, 44)
    z0 = socle(M, pod, 0, 9.5)
    M.dalle(pod, z0, "toit"); acrotere(M, pod, z0, "pierre", 1.0)
    M.cube(0, 0, 7, 36, z0, z0 + 0.5, "vegetal")
    for xx in (-13, -5, 3, 11):
        M.cyl(0, xx + 1, 1.7, 1.2, z0 + 0.5, z0 + 3.2, "vegetal", 7)
    sommets = []
    for s, k in ((-1, 1.0), (1, 0.82)):
        b = place(rect(15, 40), s * 13, 0)
        nf = round(n * k)
        z, _ = niveaux(M, lambda kk: b, z0, nf, FH, "rideau", meca={nf // 2})
        zt = z
        z = ecran(M, b, z, 2)
        ceinture(M, b, z, z + 0.5, 0.35, "alu")
        toiture(M, gonfle(b, 0.96), zt, "noir", 0.5, tech=3, edicule=(s < 0), grue=(s > 0))
        sommets.append(zt)
        for y in (-20.4, 20.4):  # lames lumineuses sur les angles intérieurs
            M.cube(s * 5.2, y, 0.7, 0.7, z0, zt + FH * 2, "accent", "b")
    bas = sommets[1] - z0
    for t in ((0.38, 0.72) if h else (0.55,)):
        zb = z0 + round(bas * t / FH) * FH
        M.cube(0, 0, 11.2, 9, zb, zb + 0.5, "alu", ""); M.cube(0, 0, 11.2, 9, zb + FH * 2 - 0.5, zb + FH * 2, "alu", "")
        for y, ny in ((-4.5, -1), (4.5, 1)):
            for k in range(3):
                x0, x1 = -5.5 + k * 3.67, -5.5 + (k + 1) * 3.67
                pts = [(x0, y, zb + 0.5), (x1, y, zb + 0.5), (x1, y, zb + FH * 2 - 0.5), (x0, y, zb + FH * 2 - 0.5)]
                M.panneau(*(pts if ny < 0 else pts[::-1]), "hall", 0.02)
    return M.objet()

def arc(a0, a1, nseg, r_ext=64.0, r_int=47.0, c=54.0):
    A = [math.radians(a0 + (a1 - a0) * i / nseg) for i in range(nseg + 1)]
    ext = [V2(r_ext * math.sin(a), c - r_ext * math.cos(a)) for a in A]
    inte = [V2(r_int * math.sin(a), c - r_int * math.cos(a)) for a in reversed(A)]
    return ext + inte

def t4_voile(h):
    """Voile courbe : un grand mur aveugle clair d'un côté, des terrasses plantées en gradins de l'autre."""
    M = Maillage("t4")
    n = N(h)
    plein = arc(-22, 22, 8)
    z = socle(M, gonfle(plein, 1.05), 0, 9.0, trame=6.1, marches=False)
    marches = 5
    pas = max(2, round(n * 0.09))
    nbase = n - marches * pas
    for j in range(marches + 1):
        seg = 8 - j
        p = arc(-22, 22 - 5.5 * j, seg)
        nf = nbase if j == 0 else pas
        aveugle = {2 * seg + 1: "beton"}
        zt, _ = niveaux(M, lambda k: p, z, nf, FH, "ailettes" if False else dict(STYLES["rideau"], trame=3.05, lame=0.7, ep=0.24), pleins=aveugle,
                        meca={nbase // 2} if (j == 0 and h) else ())
        if j < marches:  # terrasse plantée sur le gradin libéré
            t = arc(22 - 5.5 * (j + 1), 22 - 5.5 * j, 1)
            M.dalle(t, zt, "toit"); acrotere(M, t, zt, "alu", 1.1, 0.25)
            cx, cy = sum(q.x for q in t) / 4, sum(q.y for q in t) / 4
            M.cyl(cx, cy, 2.6, 2.6, zt, zt + 0.5, "vegetal", 8); M.cyl(cx, cy, 1.5, 1.0, zt + 0.5, zt + 3.2, "vegetal", 7)
        z = zt
    seg = 8 - marches
    p = arc(-22, 22 - 5.5 * marches, seg)
    cx, cy = sum(q.x for q in p) / len(p), sum(q.y for q in p) / len(p)
    toiture(M, p, z, "alu", 1.2, tech=2, centre=(cx, cy), etendue=(9, 9), grue=False)
    # le mur aveugle porte une lame de couleur sur toute la hauteur
    a0, a1, L, u, nr = arete(p, 2 * seg + 1)
    M.boite((a0 + a1) / 2 + nr * 0.3, u, nr, 1.3, 0.3, 9.0, z + 5, "accent", "b")
    M.boite((a0 + a1) / 2 + nr * 0.2, u, nr, L / 2 + 0.3, 0.2, z, z + 3.2, "beton", "b")
    return M.objet()

def t5_faisceau(h):
    """Faisceau de trois fûts ronds de verre sombre à ailettes de bronze, de hauteurs décalées."""
    M = Maillage("t5")
    n = N(h)
    pod = rond(26.5, 25, 14, 0.5)
    z0 = socle(M, pod, 0, 9.5, trame=5.5, m_pile="bronze", m_bandeau="noir")
    M.dalle(pod, z0, "toit"); acrotere(M, pod, z0, "noir", 0.9)
    for (x, y, k) in ((-9.5, -7, 1.0), (11, -3.5, 0.8), (-1.5, 11.5, 0.62)):
        b = place(rond(12.6, 12.6, 20), x, y)
        nf = round(n * k)
        z, _ = niveaux(M, lambda kk: b, z0, nf, FH, dict(STYLES["ailettes"], trame=4.2, lame=0.9, ep=0.3), meca={nf // 2} if nf > 16 else ())
        zt = z
        z = ecran(M, b, z, 1, 4.2)
        ceinture(M, b, z, z + 0.7, 0.45, "accent")
        toiture(M, place(rond(12.2, 12.2, 20), x, y), zt, "noir", 0.4, tech=2, edicule=(k == 1.0), grue=False)
    return M.objet()

def t6_redents(h):
    """Tour à redents d'inspiration Art déco : piles de pierre, allèges de bronze, lanternes et flèche."""
    M = Maillage("t6")
    n = N(h)
    base = pans(38, 38, 4)
    z = socle(M, gonfle(base, 1.1), 0, 10)
    parts = [(1.0, round(n * 0.60)), (0.78, round(n * 0.24)), (0.56, n - round(n * 0.60) - round(n * 0.24))]
    for j, (s, nf) in enumerate(parts):
        p = ech(base, s)
        z, _ = niveaux(M, lambda k: p, z, nf, FH, "piles", meca={nf // 2} if (j == 0 and h) else ())
        if j < 2:
            M.dalle(p, z, "toit"); acrotere(M, p, z, "pierre", 1.4, 0.6)
            q = ech(base, s * 0.93)
            for i in (0, 2, 4, 6):  # lanternes d'angle
                a0, a1, _, _, _ = arete(q, i)
                for c in (a0, a1):
                    M.cube(c.x, c.y, 1.6, 1.6, z, z + 3.4, "pierre"); M.cube(c.x, c.y, 1.0, 1.0, z + 3.4, z + 4.6, "lumiere")
    p = ech(base, 0.56)
    acrotere(M, p, z, "pierre", 2.4, 0.8); M.dalle(p, z + 0.05, "toit")
    ceinture(M, p, z + 2.4, z + 3.0, 0.3, "accent")
    M.cube(0, 0, 11, 11, z, z + 6.5, "pierre"); M.cube(0, 0, 7, 7, z + 6.5, z + 11, "pierre"); M.cube(0, 0, 7.6, 7.6, z + 9.2, z + 9.9, "accent", "")
    M.cyl(0, 0, 1.6, 0.5, z + 11, z + 22, "bronze", 8); M.cyl(0, 0, 0.5, 0.1, z + 22, z + 36, "alu", 6)
    return M.objet()

def t7_torsade(h):
    """Tour torsadée : chaque plancher pivote d'un cran, les bandeaux blancs dessinent l'hélice."""
    M = Maillage("t7")
    n = N(h) + 1
    base = pans(31, 31, 5.5)
    z0 = socle(M, pans(40, 40, 6), 0, 9.5, m_pile="beton")
    M.dalle(pans(40, 40, 6), z0, "toit"); acrotere(M, pans(40, 40, 6), z0, "beton", 0.9)
    pas = math.radians(1.7)
    forme = lambda k: tourne(base, pas * k)
    z, top = niveaux(M, forme, z0, n, FH, dict(STYLES["bandes"], trame=3.3, all=1.25, dep=0.45), pleins={1: "beton", 3: "beton", 5: "beton", 7: "beton"})
    for k in range(n):  # filets de couleur qui montent en hélice sur les pans coupés
        for i in (1, 5):
            a0, a1, _, _, na = arete(forme(k), i); b0, b1, _, _, nb = arete(forme(k + 1), i)
            ma, mb = (a0 + a1) / 2 + na * 0.2, (b0 + b1) / 2 + nb * 0.2
            M.barre((ma.x, ma.y, z0 + k * FH), (mb.x, mb.y, z0 + (k + 1) * FH), 1.1, "accent", 0.3)
    zt = z
    z = ecran(M, top, z, 2, 3.3)
    ceinture(M, top, z, z + 0.5, 0.35, "beton")
    toiture(M, gonfle(top, 0.95), zt, "beton", 0.5, tech=3)
    return M.objet()

TOURS = [t0_fuseau, t1_ellipse, t2_cristal, t3_jumelles, t4_voile, t5_faisceau, t6_redents, t7_torsade]
