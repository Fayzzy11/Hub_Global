# Grande Arche, immeubles de bureaux, arbres, mobilier, pont, monuments : tout le décor du quartier.
from outils import *
from tours import FH, ceinture, ecran

def caisson(M, o, ex, ey, n, w, h, carreaux=6, bord=1.5, creux=0.9):
    """Un caisson de la Grande Arche : cadre de marbre, embrasure, vitrage en retrait divisé en carreaux."""
    o, ex, ey, n = Vector(o), Vector(ex), Vector(ey), Vector(n)
    P = lambda a, b, d=0.0: o + ex * a + ey * b - n * d
    for (a0, b0, a1, b1) in ((0, 0, w, bord), (0, h - bord, w, h), (0, bord, bord, h - bord), (w - bord, bord, w, h - bord)):
        M.face_n([P(a0, b0), P(a1, b0), P(a1, b1), P(a0, b1)], n, "marbre")
    i0, i1, j0, j1 = bord, w - bord, bord, h - bord
    for (pa, pb, nn) in (((i0, j0), (i1, j0), ey), ((i1, j0), (i1, j1), -ex), ((i1, j1), (i0, j1), -ey), ((i0, j1), (i0, j0), ex)):
        M.face_n([P(*pa), P(*pb), P(*pb, creux), P(*pa, creux)], nn, "marbre")
    cw, ch = (i1 - i0) / carreaux, (j1 - j0) / carreaux
    for a in range(carreaux):
        for b in range(carreaux):
            q = [P(i0 + a * cw, j0 + b * ch, creux), P(i0 + (a + 1) * cw, j0 + b * ch, creux), P(i0 + (a + 1) * cw, j0 + (b + 1) * ch, creux), P(i0 + a * cw, j0 + (b + 1) * ch, creux)]
            if (q[1] - q[0]).cross(q[3] - q[0]).dot(n) < 0:
                q = [q[1], q[0], q[3], q[2]]
            M.panneau(*q, None, 0.05)

def arche():
    """La Grande Arche : cube évidé de 110 m, caissons de marbre et de verre, embrasures biseautées,
    emmarchement monumental, nuage de toile tendue et ascenseurs panoramiques."""
    M = Maillage("arche")
    X, Y, H, T, Z0, B = 56.0, 54.0, 110.0, 18.7, 5.4, 6.0
    yi, zi = Y - T, Z0 + H - T          # nu intérieur des jambes, sous-face du toit
    # parvis surélevé et grands escaliers de part et d'autre
    M.cube(0, 0, 2 * X + 16, 2 * Y + 12, 0, Z0, "pierre")
    for s in (-1, 1):
        for k in range(12):
            x0 = X + 8
            M.cube(s * (x0 + (12 - k) * 0.65), 0, (12 - k) * 1.3, 78, k * 0.45, (k + 1) * 0.45, "marbre")
    nc = 5
    cw, chh = 2 * X / nc, H / nc
    for s in (-1, 1):
        # faces extérieures des jambes
        for a in range(nc):
            for b in range(nc):
                caisson(M, (-X + a * cw, s * Y, Z0 + b * chh), (1, 0, 0), (0, 0, 1), (0, s, 0), cw, chh)
        # faces intérieures (dans le vide de l'arche), en retrait du biseau
        xi = X - B
        ciw, cih = 2 * xi / nc, (zi - Z0) / 4
        for a in range(nc):
            for b in range(4):
                caisson(M, (-xi + a * ciw, s * yi, Z0 + b * cih), (1, 0, 0), (0, 0, 1), (0, -s, 0), ciw, cih)
    # sous-face du toit
    xi = X - B
    ciw, cid = 2 * xi / nc, 2 * yi / 3
    for a in range(nc):
        for b in range(3):
            caisson(M, (-xi + a * ciw, -yi + b * cid, zi), (1, 0, 0), (0, 1, 0), (0, 0, -1), ciw, cid)
    # toit : dalles de marbre, belvédère
    M.face_n([(-X, -Y, Z0 + H), (X, -Y, Z0 + H), (X, Y, Z0 + H), (-X, Y, Z0 + H)], (0, 0, 1), "marbre")
    acrotere(M, rect(2 * X, 2 * Y), Z0 + H, "marbre", 1.2, 0.8)
    for a in range(4):
        for b in range(3):
            M.cube(-36 + a * 24, -30 + b * 30, 16, 20, Z0 + H, Z0 + H + 0.25, "toit")
    M.cube(20, 0, 22, 30, Z0 + H, Z0 + H + 3.2, "tech"); M.cube(20, 0, 23, 31, Z0 + H + 3.2, Z0 + H + 3.6, "alu")
    # façades d'about : cadre de marbre et embrasures biseautées qui s'ouvrent vers l'extérieur
    for s in (-1, 1):
        x = s * X
        yo, zo = yi + B, zi + B   # bord de l'ouverture au nu de la façade
        for (y0, y1, z0, z1) in ((-Y, -yo, Z0, Z0 + H), (yo, Y, Z0, Z0 + H), (-yo, yo, zo, Z0 + H)):
            # dalles de marbre de 9 m environ, posées à joints creux
            ny, nz = max(1, round((y1 - y0) / 9)), max(1, round((z1 - z0) / 9))
            for a in range(ny):
                for b in range(nz):
                    ya, yb = y0 + (y1 - y0) * a / ny, y0 + (y1 - y0) * (a + 1) / ny
                    za, zb = z0 + (z1 - z0) * b / nz, z0 + (z1 - z0) * (b + 1) / nz
                    g = 0.12
                    M.face_n([(x, ya + g, za + g), (x, yb - g, za + g), (x, yb - g, zb - g), (x, ya + g, zb - g)], (s, 0, 0), "marbre")
            M.face_n([(x - s * 0.15, y0, z0), (x - s * 0.15, y1, z0), (x - s * 0.15, y1, z1), (x - s * 0.15, y0, z1)], (s, 0, 0), "noir")
        xin = s * (X - B)
        for t in (-1, 1):   # biseaux latéraux
            M.face_n([(x, t * yo, Z0), (xin, t * yi, Z0), (xin, t * yi, zi), (x, t * yo, zo)], (s * 0.7, -t * 0.7, 0), "marbre")
        M.face_n([(x, -yo, zo), (x, yo, zo), (xin, yi, zi), (xin, -yi, zi)], (s * 0.7, 0, -0.7), "marbre")
    # le « nuage » : toile tendue suspendue dans le vide
    nx, ny = 12, 9
    def nuage(i, j):
        u, v = i / nx, j / ny
        z = Z0 + 24 + 5.5 * math.sin(u * 7.3 + 1) * math.cos(v * 5.1) + 3.5 * math.sin(v * 9 + u * 4) + 7 * (0.5 - abs(u - 0.5)) + 6 * (0.5 - abs(v - 0.5))
        return (-30 + 60 * u + 2.5 * math.sin(v * 11), -24 + 48 * v + 2.5 * math.sin(u * 9), z)
    for i in range(nx):
        for j in range(ny):
            q = [nuage(i, j), nuage(i + 1, j), nuage(i + 1, j + 1), nuage(i, j + 1)]
            M.face(q, "toile"); M.face(q[::-1], "toile")
    for (i, j, tx, ty) in ((0, 0, -44, -yi), (nx, 0, 44, -yi), (0, ny, -44, yi), (nx, ny, 44, yi), (nx // 2, 0, 0, -yi), (nx // 2, ny, 0, yi)):
        M.barre(nuage(i, j), (tx, ty, Z0 + 58), 0.22, "alu")
    # ascenseurs panoramiques
    for (dx, dy) in ((-1.6, -1.6), (1.6, -1.6), (1.6, 1.6), (-1.6, 1.6)):
        M.cyl(22 + dx, 24 + dy, 0.22, 0.22, Z0, zi, "alu", 6)
    for z in range(int(Z0) + 9, int(zi), 9):
        M.cube(22, 24, 3.6, 3.6, z, z + 0.25, "alu", "")
    M.cube(22, 24, 2.8, 2.8, Z0 + 31, Z0 + 35, "hall", ""); M.cube(22, 24, 2.8, 2.8, Z0 + 66, Z0 + 70, "hall", "")
    return M.objet()

# ---------- immeubles de bureaux (au-delà du boulevard circulaire) ----------
def bureau(k):
    M = Maillage(f"bureau{k}")
    if k == 0:
        b = rect(34, 22); z = socle(M, b, 0, 7, trame=5.6, marches=False, auvent=True)
        z, _ = niveaux(M, lambda i: b, z, 10, 3.7, dict(STYLES["bandes"], trame=3.4, dep=0.35))
        toiture(M, gonfle(b, 0.97), z, "beton", 0.9, tech=3, grue=False)
    elif k == 1:
        b = rect(26, 26); z = socle(M, b, 0, 7, trame=5.2, marches=False, m_pile="noir", m_bandeau="alu")
        z, _ = niveaux(M, lambda i: b, z, 15, 3.7, dict(STYLES["rideau"], trame=3.25, pas=2))
        zt = z; z = ecran(M, b, z, 1, 3.25); toiture(M, gonfle(b, 0.96), zt, "noir", 0.4, tech=2, grue=False)
    elif k == 2:
        b = pans(30, 24, 3); z = socle(M, b, 0, 7.5, trame=6, marches=False)
        z, _ = niveaux(M, lambda i: b, z, 7, 3.7, dict(STYLES["piles"], trame=3.0))
        toiture(M, gonfle(b, 0.96), z, "pierre", 1.2, jardin=True)
    else:
        b = rect(40, 18); z = socle(M, b, 0, 7, trame=5.7, marches=False, m_pile="beton")
        z, _ = niveaux(M, lambda i: b, z, 12, 3.7, dict(STYLES["ailettes"], trame=3.33, lame=0.7, m_lame="alu", pas=2))
        M.dalle(b, z, "toit"); b2 = place(rect(18, 18), -11, 0)
        z2, _ = niveaux(M, lambda i: b2, z, 4, 3.7, dict(STYLES["ailettes"], trame=3.0, lame=0.7, m_lame="alu", pas=2))
        acrotere(M, b, z, "alu", 1.0); toiture(M, gonfle(b2, 0.95), z2, "alu", 0.9, tech=2, grue=False)
        M.cube(9, 0, 16, 12, z, z + 0.45, "vegetal")
    return M.objet()

# ---------- arbres ----------
def arbre(k):
    M = Maillage(f"arbre{k}")
    if k == 0:   # platane : houppier large
        M.cyl(0, 0, 0.42, 0.26, 0, 4.4, "ecorce", 7)
        for (dx, dy, dz) in ((1.9, 0.6, 6.4), (-1.6, 1.3, 6.8), (-0.4, -1.9, 6.2)):
            M.barre((0, 0, 3.6), (dx, dy, dz), 0.3, "ecorce")
        for (x, y, z, r) in ((0, 0, 8.6, 3.5), (2.5, 0.9, 7.2, 2.6), (-2.2, 1.7, 7.5, 2.7), (-0.6, -2.6, 7.0, 2.5), (1.2, -1.6, 9.4, 2.3), (-1.2, 0.8, 10.2, 2.2)):
            M.blob(x, y, z, r, "vegetal", 2, 0.16, 0.85)
    elif k == 1:  # tilleul : houppier haut et ovale
        M.cyl(0, 0, 0.34, 0.2, 0, 4.0, "ecorce", 7)
        for (x, y, z, r, sz) in ((0, 0, 7.4, 2.9, 1.25), (0.9, 0.5, 10.2, 2.3, 1.2), (-0.8, -0.5, 9.4, 2.3, 1.2), (0.1, 0.2, 12.4, 1.7, 1.2)):
            M.blob(x, y, z, r, "vegetal", 2, 0.15, sz)
    else:         # jeune arbre d'alignement
        M.cyl(0, 0, 0.2, 0.13, 0, 3.2, "ecorce", 6)
        for (x, y, z, r) in ((0, 0, 5.2, 2.0), (0.7, 0.4, 6.6, 1.5), (-0.6, -0.3, 6.3, 1.5)):
            M.blob(x, y, z, r, "vegetal", 2, 0.15, 1.0)
    return M.objet()

def lampadaire():
    M = Maillage("lampadaire")
    M.cyl(0, 0, 0.2, 0.2, 0, 0.9, "noir", 8); M.cyl(0, 0, 0.11, 0.08, 0.9, 9.0, "noir", 6)
    for s in (-1, 1):
        M.barre((0, 0, 8.6), (s * 1.5, 0, 9.3), 0.1, "noir"); M.barre((s * 1.5, 0, 9.3), (s * 2.4, 0, 9.2), 0.1, "noir")
        M.cube(s * 2.5, 0, 1.3, 0.5, 9.05, 9.3, "noir", ""); M.cube(s * 2.5, 0, 1.1, 0.4, 8.98, 9.05, "lumiere", "h")
    return M.objet()

def voiture():
    """Berline : caisse, habitacle vitré, quatre roues. L'avant regarde vers +X."""
    M = Maillage("voiture")
    M.profil([(-2.3, 0.32), (2.3, 0.32), (2.34, 0.62), (2.05, 0.82), (0.95, 0.9), (-1.75, 0.94), (-2.3, 0.86)], -0.92, 0.92, "carrosserie")
    M.profil([(-1.72, 0.92), (0.98, 0.88), (0.42, 1.38), (-1.2, 1.42)], -0.8, 0.8, "hall")
    M.profil([(-1.22, 1.4), (0.44, 1.36), (0.4, 1.45), (-1.18, 1.48)], -0.76, 0.76, "carrosserie")
    for x in (-1.45, 1.42):
        for y0, y1 in ((-0.98, -0.72), (0.72, 0.98)):
            M.profil([(x + 0.36 * math.cos(a * math.pi / 4), 0.36 + 0.36 * math.sin(a * math.pi / 4)) for a in range(8)], y0, y1, "pneu")
    for y in (-0.62, 0.62):
        M.face_n([(2.345, y - 0.2, 0.55), (2.345, y + 0.2, 0.55), (2.345, y + 0.2, 0.7), (2.345, y - 0.2, 0.7)], (1, 0, 0), "lumiere")
    return M.objet()

def sculpture():
    """Stabile rouge sur l'esplanade, clin d'œil à l'Araignée rouge de Calder."""
    M = Maillage("sculpture")
    sommet = Vector((0.5, 0.2, 13.5))
    for (px, py, bx, by) in ((9, 2, 5.5, 3.5), (-8, 4.5, -3, 6), (-6.5, -6, -6, -1), (4, -8, 6, -3), (0.5, 8.5, 3.5, 5)):
        p0, p1 = Vector((px, py, 0)), Vector((bx * 0.6, by * 0.6, 9.5))
        pts = [((1 - t) ** 2) * p0 + 2 * (1 - t) * t * p1 + (t ** 2) * sommet for t in [i / 7 for i in range(8)]]
        for i in range(7):
            M.barre(pts[i], pts[i + 1], 0.22, "rouge", 2.6 - i * 0.26)
    M.barre(sommet, (6.5, -1.5, 17.5), 0.2, "rouge", 1.6); M.barre(sommet, (-4, 2.5, 16.2), 0.2, "rouge", 1.3)
    return M.objet()

def pont():
    """Pont de Neuilly : tablier, deux arches d'acier de chaque côté d'une pile centrale, garde-corps, candélabres."""
    M = Maillage("pont")
    L, W, zt = 82.0, 20.0, 9.6
    M.cube(0, 0, 2 * L, 2 * W, zt - 1.5, zt - 0.1, "pierre", "")
    M.cube(0, 0, 2 * L, 2 * W - 9, zt - 0.1, zt, "chaussee")
    for s in (-1, 1):
        M.cube(0, s * (W - 2.25), 2 * L, 4.5, zt - 0.1, zt + 0.22, "pierre")
        M.cube(0, s * (W - 0.2), 2 * L, 0.3, zt + 0.22, zt + 1.3, "noir")
        for k in range(-4, 5):
            M.cyl(k * 18, s * (W - 0.8), 0.16, 0.1, zt + 0.22, zt + 7.5, "noir", 6)
            M.cube(k * 18, s * (W - 1.3), 0.5, 1.4, zt + 7.3, zt + 7.5, "noir", ""); M.cube(k * 18, s * (W - 1.5), 0.4, 0.9, zt + 7.22, zt + 7.3, "lumiere", "h")
        for cx in (-L / 2 - 1, L / 2 + 1):   # arches
            pts = [(cx + 36 * math.cos(math.pi * (1 - i / 12)), s * (W - 3), -1.0 + 8.3 * math.sin(math.pi * i / 12)) for i in range(13)]
            for i in range(12):
                M.barre(pts[i], pts[i + 1], 1.5, "fer", 1.0)
            for i in range(2, 11, 2):
                M.barre(pts[i], (pts[i][0], pts[i][1], zt - 1.5), 0.5, "fer")
    for cx in (-L - 1, 0, L + 1):
        M.cube(cx, 0, 9, 2 * W + 3, -2, zt - 1.5, "pierre")
    M.dalle([V2(-3, -W - 6), V2(5, -W - 2), V2(5, W + 2), V2(-3, W + 6)], 1.2, "pierre")
    return M.objet()

def eiffel():
    M = Maillage("eiffel")
    r = lambda z: 4.5 + 57.5 * math.exp(-z / 78.0)
    Zs = [0, 14, 28, 43, 57, 72, 86, 100, 115]
    for (sx, sy) in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        for i in range(len(Zs) - 1):
            z0, z1 = Zs[i], Zs[i + 1]
            e0, e1 = 7.5 - z0 * 0.035, 7.5 - z1 * 0.035
            M.boite2(V2(sx * r(z0), sy * r(z0)), V2(1, 0), V2(0, 1), V2(sx * r(z1), sy * r(z1)), V2(1, 0), V2(0, 1), e1, e1, z0, z1, "fer", "bh")
    def plateforme(z, h, deb):
        d = r(z) + deb
        M.cube(0, 0, 2 * d, 2 * d, z, z + h, "fer", ""); M.cube(0, 0, 2 * d + 2, 2 * d + 2, z + h, z + h + 1.2, "fer", "")
    plateforme(57, 5, 9); plateforme(115, 4, 6)
    # grandes arches décoratives entre les piliers
    for a in range(4):
        c, s = math.cos(a * math.pi / 2), math.sin(a * math.pi / 2)
        pts = []
        for i in range(11):
            t = -1 + 2 * i / 10
            u, z = t * 44, 52 - 34 * t * t
            d = r(max(0, z)) + 3
            pts.append((c * d - s * u, s * d + c * u, z))
        for i in range(10):
            M.barre(pts[i], pts[i + 1], 1.6, "fer", 1.0)
    # croisillons entre les deux premiers étages
    for a in range(4):
        c, s = math.cos(a * math.pi / 2), math.sin(a * math.pi / 2)
        for (za, zb) in ((62, 88), (88, 115)):
            ra, rb = r(za) + 5, r(zb) + 4
            P = lambda d, u, z: (c * d - s * u, s * d + c * u, z)
            M.barre(P(ra, -ra, za), P(rb, rb, zb), 1.1, "fer"); M.barre(P(ra, ra, za), P(rb, -rb, zb), 1.1, "fer")
    # flèche
    Z2 = [119, 150, 185, 220, 255, 276]
    for i in range(len(Z2) - 1):
        z0, z1 = Z2[i], Z2[i + 1]
        a0, a1 = r(z0) + 5.5, r(z1) + (5.5 if i < 4 else 2)
        M.boite2(V2(0, 0), V2(1, 0), V2(0, 1), V2(0, 0), V2(1, 0), V2(0, 1), a1, a1, z0, z1, "fer", "b")
        lo = a0
    M.cube(0, 0, 13, 13, 276, 281, "fer", ""); M.cube(0, 0, 7, 7, 281, 290, "fer"); M.cyl(0, 0, 0.9, 0.2, 290, 324, "fer", 6)
    return M.objet()

def arc_triomphe():
    """Arc de Triomphe : la grande voûte regarde l'avenue (axe X), deux petites voûtes traversent les piles."""
    M = Maillage("arc")
    D, W, H = 11.0, 22.5, 50.0     # demi-profondeur (X), demi-largeur (Y), hauteur
    ra, hs = 7.3, 21.5             # rayon de la voûte, hauteur de naissance
    arc = [(ra * math.cos(math.pi * i / 10), hs + ra * math.sin(math.pi * i / 10)) for i in range(11)]   # de +Y vers -Y
    for s in (-1, 1):
        x = s * D
        contour = [(-W, 0), (-ra, 0), (-ra, hs)] + [(y, z) for (y, z) in reversed(arc)][1:-1] + [(ra, hs), (ra, 0), (W, 0), (W, 36), (-W, 36)]
        M.face_n([(x, y, z) for (y, z) in contour], (s, 0, 0), "pierre")
    for i in range(10):   # intrados
        (ya, za), (yb, zb) = arc[i], arc[i + 1]
        M.face_n([(-D, ya, za), (D, ya, za), (D, yb, zb), (-D, yb, zb)], (0, -(ya + yb), -(za + zb - 2 * hs) - 0.01), "pierre")
    for t in (-1, 1):
        M.face_n([(-D, t * ra, 0), (D, t * ra, 0), (D, t * ra, hs), (-D, t * ra, hs)], (0, -t, 0), "pierre")
        M.face_n([(-D, t * W, 0), (D, t * W, 0), (D, t * W, 36), (-D, t * W, 36)], (0, t, 0), "pierre")
        M.cube(0, t * W, 9, 0.6, 0, 17, "noir", "b")   # petite voûte latérale, évoquée par un renfoncement sombre
        for s in (-1, 1):  # groupes sculptés au pied des piles
            M.cube(s * (D + 1.2), t * 15, 2.4, 8.5, 0, 3.2, "pierre"); M.cube(s * (D + 0.9), t * 15, 1.8, 6, 3.2, 12.5, "pierre")
    M.cube(0, 0, 2 * D + 2.4, 2 * W + 2.4, 36, 38.4, "pierre", "")     # corniche
    M.cube(0, 0, 2 * D + 0.8, 2 * W + 0.8, 34.2, 36, "pierre", "")     # frise
    M.cube(0, 0, 2 * D, 2 * W, 38.4, 47.5, "pierre")                   # attique
    M.cube(0, 0, 2 * D + 1.4, 2 * W + 1.4, 47.5, 49, "pierre", ""); M.cube(0, 0, 2 * D - 3, 2 * W - 3, 49, 50, "toit")
    return M.objet()

def bateau():
    """Bateau-mouche : coque blanche, pont vitré. L'avant regarde vers +X."""
    M = Maillage("bateau")
    coque = [V2(-21, -3.6), V2(13, -4.2), V2(20, -2.2), V2(23.5, 0), V2(20, 2.2), V2(13, 4.2), V2(-21, 3.6)]
    for i in range(len(coque)):
        p0, p1, L, u, nr = arete(coque, i)
        M.face([(p0.x * 0.94, p0.y * 0.86, -0.3), (p1.x * 0.94, p1.y * 0.86, -0.3), (p1.x, p1.y, 1.7), (p0.x, p0.y, 1.7)], "coque")
    M.dalle(coque, 1.7, "toit")
    cab = [V2(-17, -3.1), V2(11, -3.4), V2(15, 0), V2(11, 3.4), V2(-17, 3.1)]
    for i in range(len(cab)):
        p0, p1, L, u, nr = arete(cab, i)
        nb = max(1, round(L / 2.4))
        for k in range(nb):
            a, b = p0.lerp(p1, k / nb), p0.lerp(p1, (k + 1) / nb)
            M.panneau((a.x, a.y, 1.9), (b.x, b.y, 1.9), (b.x * 0.97, b.y * 0.9, 4.1), (a.x * 0.97, a.y * 0.9, 4.1), "hall", 0.02)
        M.face([(p0.x, p0.y, 1.7), (p1.x, p1.y, 1.7), (p1.x, p1.y, 1.9), (p0.x, p0.y, 1.9)], "coque")
    M.dalle([V2(p.x * 0.97, p.y * 0.9) for p in cab], 4.1, "coque")
    M.cube(-6, 0, 9, 4.4, 4.1, 4.3, "accent"); M.cube(-19.5, 0, 2.2, 5.6, 1.7, 2.9, "coque")
    return M.objet()

DECOR = {"arche": arche, "bureau0": lambda: bureau(0), "bureau1": lambda: bureau(1), "bureau2": lambda: bureau(2), "bureau3": lambda: bureau(3),
         "arbre0": lambda: arbre(0), "arbre1": lambda: arbre(1), "arbre2": lambda: arbre(2), "lampadaire": lampadaire, "voiture": voiture,
         "sculpture": sculpture, "pont": pont, "eiffel": eiffel, "arc": arc_triomphe, "bateau": bateau}
