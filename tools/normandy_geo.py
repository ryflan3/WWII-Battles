"""Vector geography of the Normandy invasion coast, rasterized onto Unciv's hex grid.

Coordinates are (latitude, longitude) in degrees. One hex is about 2 km (1.25 miles). The map is 58 columns x 25 rows
and runs from the Cotentin west of Sainte-Mère-Église to the Dives, and from the Channel down to Saint-Lô and Caen.

Run from the repository root:
    python3 tools/normandy_geo.py            -> writes tools/build/normandy_tiles.json
The Kotlin tool (tools/cwtool) turns that JSON into the Unciv map file "maps/Normandy (free play)" and the scenario saves.
"""
import json, math, os, sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dday_oob as oob

# ---------------------------------------------------------------- grid

KM_PER_HEX = 2.0
WORLD_PER_KM = math.sqrt(3) / KM_PER_HEX          # Unciv world units per km (neighbouring hexes are sqrt(3) apart)
WIDTH, HEIGHT = 58, 25
LAT0, LON0 = 49.300, -0.770                         # the map's centre tile
KM_PER_DEG_LAT = 111.2
KM_PER_DEG_LON = 111.32 * math.cos(math.radians(LAT0))


def ll_to_km(lat, lon):
    return (lon - LON0) * KM_PER_DEG_LON, (lat - LAT0) * KM_PER_DEG_LAT


def col_row_to_hex(col, row):
    two_rows = row * 2 + (1 if abs(col) % 2 == 1 else 0)
    return (two_rows - col) // 2, (two_rows + col) // 2


def hex_to_world(x, y):
    return 1.5 * (y - x), math.sqrt(3) / 2 * (x + y)


def hex_to_km(x, y):
    wx, wy = hex_to_world(x, y)
    return wx / WORLD_PER_KM, wy / WORLD_PER_KM


def all_hexes():
    # same ranges as Unciv's rectangular TileMap constructor (Kotlin integer division truncates toward zero)
    for col in range(-(WIDTH // 2), (WIDTH - 1) // 2 + 1):
        for row in range(-(HEIGHT // 2), (HEIGHT - 1) // 2 + 1):
            yield col_row_to_hex(col, row)


HEXES = list(all_hexes())
HEXSET = set(HEXES)
POS = {h: hex_to_km(*h) for h in HEXES}            # km from the centre
NEIGHBOR_OFFSETS = [(1, 1), (-1, -1), (0, 1), (1, 0), (0, -1), (-1, 0)]


def neighbors(h):
    for dx, dy in NEIGHBOR_OFFSETS:
        n = (h[0] + dx, h[1] + dy)
        if n in HEXSET:
            yield n


def hex_distance(a, b):
    dx, dy = a[0] - b[0], a[1] - b[1]
    return max(abs(dx), abs(dy)) if dx * dy >= 0 else abs(dx) + abs(dy)


def nearest_hex(lat, lon):
    px, py = ll_to_km(lat, lon)
    return min(HEXES, key=lambda h: (POS[h][0] - px) ** 2 + (POS[h][1] - py) ** 2)


# ---------------------------------------------------------------- geometry helpers (all in km)

def km_pts(pts):
    return [ll_to_km(*p) for p in pts]


def dist_point_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def dist_polyline(px, py, pts):
    return min(dist_point_segment(px, py, *pts[i], *pts[i + 1]) for i in range(len(pts) - 1))


def in_polygon(px, py, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def in_ellipse(px, py, cx, cy, rx, ry):
    return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0


def segments_intersect(p1, p2, p3, p4):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0)


def hex_path(pts_ll, step=0.15):
    """Rasterize a (lat, lon) polyline into a connected list of hexes."""
    pts = km_pts(pts_ll)
    path = []
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        for k in range(n + 1):
            px, py = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
            h = min(HEXES, key=lambda q: (POS[q][0] - px) ** 2 + (POS[q][1] - py) ** 2)
            if math.hypot(POS[h][0] - px, POS[h][1] - py) > 1.3:   # off the map
                continue
            if not path or path[-1] != h:
                if path and h not in set(neighbors(path[-1])):
                    # bridge a diagonal jump with the shared neighbour closest to the line
                    common = set(neighbors(path[-1])) & set(neighbors(h))
                    if common:
                        path.append(min(common, key=lambda q: (POS[q][0] - px) ** 2 + (POS[q][1] - py) ** 2))
                path.append(h)
    # straighten: drop any hex whose predecessor and successor are already adjacent (removes zig-zags)
    changed = True
    while changed:
        changed = False
        for i in range(1, len(path) - 1):
            a, c = path[i - 1], path[i + 1]
            if (c[0] - a[0], c[1] - a[1]) in NEIGHBOR_OFFSETS or a == c:
                del path[i]
                changed = True
                break
    return path


def noise(h, salt=0):
    """Deterministic pseudo-random number in [0, 1) for a hex."""
    v = (h[0] * 73856093) ^ (h[1] * 19349663) ^ (salt * 83492791)
    v = (v * 2654435761) & 0xFFFFFFFF
    return v / 2 ** 32


# ---------------------------------------------------------------- the coast
# Land is everything inside this polygon: the coast from Quinéville round the Baie des Veys to Cabourg, closed far
# outside the map to the south.

LAND = [
    (49.60, -1.62), (49.60, -1.327), (49.530, -1.306), (49.513, -1.294), (49.490, -1.264), (49.468, -1.246),
    (49.446, -1.226), (49.430, -1.208), (49.415, -1.184), (49.400, -1.170), (49.384, -1.162), (49.366, -1.164),
    # the Baie des Veys: estuaries of the Douve and the Vire
    (49.352, -1.180), (49.338, -1.196), (49.326, -1.182), (49.322, -1.152), (49.327, -1.120), (49.337, -1.098),
    (49.352, -1.082), (49.369, -1.071), (49.383, -1.056), (49.390, -1.036),
    # Grandcamp, Pointe du Hoc, Omaha
    (49.395, -1.010), (49.401, -0.990), (49.395, -0.965), (49.390, -0.937), (49.383, -0.913), (49.375, -0.890),
    (49.367, -0.868), (49.360, -0.848), (49.354, -0.825), (49.350, -0.800), (49.349, -0.775), (49.348, -0.757),
    # Port-en-Bessin, Longues, Arromanches
    (49.348, -0.730), (49.348, -0.700), (49.345, -0.665), (49.342, -0.630), (49.341, -0.610),
    # Gold
    (49.339, -0.585), (49.337, -0.555), (49.336, -0.525), (49.337, -0.495), (49.337, -0.470),
    # Juno
    (49.338, -0.455), (49.337, -0.430), (49.336, -0.410), (49.333, -0.393), (49.328, -0.372), (49.318, -0.352),
    # Sword
    (49.307, -0.325), (49.299, -0.305), (49.292, -0.283), (49.288, -0.262), (49.285, -0.249),
    # the Orne estuary
    (49.271, -0.241), (49.266, -0.228), (49.276, -0.212),
    # Merville-Franceville, Cabourg, Houlgate
    (49.286, -0.195), (49.290, -0.160), (49.292, -0.125), (49.293, -0.090), (49.293, 0.10),
    (49.00, 0.10), (49.00, -1.62),
]
LAND_KM = km_pts(LAND)
ISLANDS = [("Iles Saint-Marcouf", 49.496, -1.149)]

# Coastal stretches: (from longitude, to longitude, feature) - west to east along the northern coast.
# The Cotentin shore (Utah) is beach all the way.
COAST_SEGMENTS = [
    (-1.10, -1.022, "Beach"),     # Grandcamp-Maisy
    (-1.022, -0.917, "Cliffs"),   # Pointe du Hoc to Pointe de la Percée
    (-0.917, -0.826, "Bluffs"),   # Omaha
    (-0.826, -0.625, "Cliffs"),   # Sainte-Honorine, Port-en-Bessin, Longues, Arromanches
    (-0.625, 0.10, "Beach"),      # Gold, Juno, Sword, Merville, Cabourg
]

# ---------------------------------------------------------------- rivers, flooding, roads

RIVERS = OrderedDict([
    ("Merderet", [(49.490, -1.365), (49.450, -1.362), (49.418, -1.356), (49.404, -1.352), (49.385, -1.346),
                  (49.362, -1.340), (49.345, -1.325)]),
    ("Douve", [(49.375, -1.470), (49.362, -1.420), (49.352, -1.380), (49.345, -1.325), (49.333, -1.290),
               (49.318, -1.258), (49.322, -1.225), (49.333, -1.196)]),
    ("Taute", [(49.235, -1.340), (49.262, -1.312), (49.288, -1.280), (49.310, -1.262)]),
    ("Vire", [(49.080, -1.095), (49.116, -1.100), (49.160, -1.108), (49.205, -1.112), (49.250, -1.120),
              (49.290, -1.128), (49.324, -1.132)]),
    ("Aure", [(49.290, -0.640), (49.276, -0.703), (49.290, -0.750), (49.300, -0.800), (49.306, -0.850),
              (49.310, -0.905), (49.315, -0.960), (49.320, -1.020), (49.318, -1.070), (49.324, -1.112)]),
    ("Seulles", [(49.080, -0.650), (49.140, -0.635), (49.176, -0.622), (49.215, -0.600), (49.250, -0.575),
                 (49.283, -0.545), (49.305, -0.510), (49.322, -0.478), (49.336, -0.460)]),
    ("Orne", [(49.080, -0.395), (49.130, -0.375), (49.175, -0.358), (49.200, -0.330), (49.222, -0.300),
              (49.240, -0.270), (49.258, -0.252), (49.270, -0.238)]),
    ("Dives", [(49.080, -0.120), (49.140, -0.130), (49.190, -0.145), (49.215, -0.148), (49.236, -0.142),
               (49.258, -0.140), (49.276, -0.128), (49.292, -0.115)]),
])

FLOODED_AREAS = [   # polygons the Germans flooded, or marsh
    # behind Utah Beach: the inundated pastures crossed only by the four causeways
    [(49.455, -1.258), (49.432, -1.226), (49.404, -1.196), (49.380, -1.182), (49.370, -1.200), (49.392, -1.218),
     (49.420, -1.240), (49.450, -1.270)],
    # the Douve marshes north and west of Carentan
    [(49.360, -1.430), (49.357, -1.370), (49.343, -1.300), (49.328, -1.268), (49.318, -1.226), (49.304, -1.222),
     (49.300, -1.262), (49.318, -1.300), (49.332, -1.355), (49.338, -1.430)],
    # the Taute marshes south-west of Carentan
    [(49.300, -1.268), (49.272, -1.300), (49.245, -1.335), (49.236, -1.315), (49.268, -1.278), (49.292, -1.258)],
    # the Aure valley behind Omaha, flooded from Trévières to Isigny
    [(49.325, -1.090), (49.326, -1.000), (49.320, -0.930), (49.314, -0.880), (49.302, -0.880), (49.308, -0.940),
     (49.311, -1.010), (49.312, -1.090)],
    # the Dives valley east of the airborne bridgehead
    [(49.290, -0.110), (49.262, -0.122), (49.236, -0.128), (49.200, -0.132), (49.170, -0.120), (49.170, -0.155),
     (49.205, -0.165), (49.240, -0.162), (49.268, -0.160), (49.290, -0.140)],
]
MERDERET_FLOOD_KM = 0.9      # the Merderet was flooded about a kilometre either side of the river

ROADS = OrderedDict([
    # the Cherbourg - Carentan - Bayeux - Caen highway (N13)
    ("N13", [(49.540, -1.420), (49.503, -1.430), (49.488, -1.381), (49.445, -1.345), (49.408, -1.317),
             (49.370, -1.290), (49.334, -1.268), (49.303, -1.248), (49.310, -1.180), (49.318, -1.102),
             (49.318, -1.020), (49.322, -0.960), (49.330, -0.898), (49.315, -0.830), (49.290, -0.760),
             (49.276, -0.703), (49.255, -0.630), (49.230, -0.560), (49.205, -0.505), (49.185, -0.452),
             (49.183, -0.370)]),
    ("Utah causeway", [(49.415, -1.181), (49.405, -1.210), (49.392, -1.230), (49.379, -1.226)]),
    ("Ste-Marie - Carentan", [(49.379, -1.226), (49.355, -1.245), (49.334, -1.268)]),
    ("Ste-Mere - Ste-Marie", [(49.408, -1.317), (49.392, -1.270), (49.379, -1.226)]),
    ("Merderet crossings", [(49.408, -1.317), (49.404, -1.352), (49.408, -1.400), (49.402, -1.460)]),
    ("Chef-du-Pont", [(49.408, -1.317), (49.385, -1.345), (49.380, -1.400), (49.375, -1.460)]),
    ("Utah coast road", [(49.530, -1.320), (49.488, -1.381)]),
    ("Carentan - Saint-Lo", [(49.303, -1.248), (49.260, -1.200), (49.200, -1.150), (49.116, -1.091)]),
    ("Carentan - Periers", [(49.303, -1.248), (49.260, -1.330), (49.210, -1.400), (49.190, -1.460)]),
    ("Isigny - Saint-Lo", [(49.318, -1.102), (49.250, -1.100), (49.180, -1.095), (49.116, -1.091)]),
    ("Grandcamp", [(49.388, -1.045), (49.340, -1.050), (49.318, -1.102)]),
    ("Grandcamp - Vierville", [(49.388, -1.045), (49.392, -0.995), (49.378, -0.905)]),
    ("Omaha coast", [(49.378, -0.905), (49.366, -0.873), (49.352, -0.846), (49.346, -0.800), (49.346, -0.757)]),
    ("Vierville draw", [(49.378, -0.905), (49.330, -0.898), (49.309, -0.905)]),
    ("Les Moulins draw", [(49.366, -0.873), (49.340, -0.880), (49.330, -0.898)]),
    ("Bayeux - Saint-Lo", [(49.276, -0.703), (49.240, -0.780), (49.200, -0.860), (49.160, -0.980), (49.116, -1.091)]),
    ("Bayeux - Port-en-Bessin", [(49.276, -0.703), (49.346, -0.757)]),
    ("Bayeux - Arromanches", [(49.276, -0.703), (49.300, -0.660), (49.338, -0.620), (49.338, -0.585)]),
    ("Bayeux - Tilly - Villers", [(49.276, -0.703), (49.230, -0.665), (49.176, -0.622), (49.083, -0.656)]),
    ("Gold - Creully", [(49.336, -0.525), (49.300, -0.540), (49.283, -0.545), (49.230, -0.560)]),
    ("Juno coast", [(49.338, -0.585), (49.337, -0.525), (49.336, -0.457), (49.335, -0.395), (49.318, -0.352),
                    (49.300, -0.302), (49.284, -0.258)]),
    ("Courseulles - Caen", [(49.336, -0.457), (49.300, -0.440), (49.255, -0.430), (49.205, -0.410),
                            (49.183, -0.370)]),
    ("Douvres - Caen", [(49.330, -0.390), (49.296, -0.378), (49.250, -0.360), (49.183, -0.370)]),
    ("Caen - Ouistreham", [(49.183, -0.370), (49.215, -0.320), (49.242, -0.283), (49.284, -0.258)]),
    ("Sword - Bieville", [(49.296, -0.302), (49.270, -0.312), (49.240, -0.320), (49.215, -0.320)]),
    ("Pegasus - Ranville - Troarn", [(49.242, -0.274), (49.231, -0.257), (49.215, -0.220), (49.180, -0.180),
                                     (49.160, -0.092)]),
    ("Ranville - Cabourg", [(49.231, -0.257), (49.250, -0.220), (49.271, -0.190), (49.285, -0.120)]),
    ("Caen - Falaise", [(49.183, -0.370), (49.140, -0.355), (49.086, -0.340)]),
    ("Caen - Troarn", [(49.183, -0.370), (49.180, -0.290), (49.180, -0.180)]),
    ("Caen - Villers-Bocage", [(49.183, -0.370), (49.150, -0.470), (49.110, -0.580), (49.083, -0.656)]),
    ("Caen - Tilly", [(49.183, -0.370), (49.180, -0.460), (49.176, -0.622)]),
    ("Bayeux - Caumont", [(49.276, -0.703), (49.200, -0.760), (49.100, -0.800)]),
])

# ---------------------------------------------------------------- land cover

CAEN_PLAIN = [  # open wheat country between the Seulles and the Orne: Plains, few hedges
    (49.330, -0.560), (49.330, -0.360), (49.300, -0.300), (49.250, -0.290), (49.200, -0.320), (49.120, -0.300),
    (49.090, -0.380), (49.110, -0.520), (49.180, -0.560), (49.240, -0.585), (49.300, -0.585)]
BOCAGE_FREE = [  # the plain east of Caen and the Dives levels
    (49.200, -0.330), (49.180, -0.200), (49.130, -0.180), (49.110, -0.300)]

WOODS = [  # (lat, lon, rx km, ry km, density)
    (49.190, -0.900, 6.0, 3.2, 0.95),     # Forêt de Cerisy
    (49.212, -0.195, 2.6, 2.4, 0.95),     # Bois de Bavent
    (49.245, -0.215, 1.2, 1.0, 0.8),      # woods on the Bréville ridge
    (49.470, -1.420, 2.0, 1.6, 0.7),      # woods west of Montebourg
    (49.130, -0.700, 2.5, 2.0, 0.7),      # woods south of Tilly
    (49.110, -0.470, 2.0, 1.8, 0.6),      # woods along the Odon
    (49.235, -1.000, 2.0, 1.6, 0.6),      # Bois du Molay
    (49.160, -1.250, 2.5, 2.0, 0.6),      # woods south of the Taute
    (49.330, -1.140, 1.0, 1.0, 0.5),
]
HILLS = [  # (lat, lon, rx km, ry km)
    (49.100, -0.800, 3.0, 1.6),           # the Caumont ridge
    (49.125, -0.505, 1.6, 1.2),           # Hill 112, above the Odon
    (49.160, -0.700, 1.4, 1.2),           # hills south of Tilly
    (49.110, -1.000, 2.0, 1.4),           # hills east of Saint-Lô
    (49.470, -1.400, 1.4, 1.2),           # the hill of Montebourg
]
RIDGES = OrderedDict([
    ("Périers ridge", [(49.262, -0.380), (49.266, -0.335), (49.262, -0.300)]),
    ("Bréville ridge", [(49.248, -0.230), (49.225, -0.210), (49.200, -0.205)]),
    ("Mont Fleury", [(49.322, -0.540), (49.318, -0.505)]),
    ("Bayeux ridge", [(49.255, -0.760), (49.240, -0.700)]),
])
TOWNS = OrderedDict([  # extra built-up hexes (the landmark towns get their own art)
    ("Isigny", (49.318, -1.102)), ("Montebourg", (49.488, -1.381)), ("Trévières", (49.309, -0.905)),
    ("Grandcamp", (49.388, -1.045)), ("Arromanches", (49.340, -0.621)), ("Creully", (49.285, -0.540)),
    ("Douvres", (49.296, -0.378)), ("Ouistreham", (49.282, -0.252)), ("Troarn", (49.180, -0.180)),
    ("Tilly-sur-Seulles", (49.176, -0.622)), ("Ranville", (49.231, -0.257)), ("Caen east", (49.180, -0.330)),
    ("Caen south", (49.160, -0.370)), ("Bretteville", (49.205, -0.505)), ("Sainte-Marie-du-Mont", (49.379, -1.226)),
    ("Le Molay", (49.250, -0.880)), ("Balleroy", (49.180, -0.840)), ("Ver-sur-Mer", (49.330, -0.525)),
    ("Bernières", (49.333, -0.421)), ("Lion-sur-Mer", (49.300, -0.320)),
])

LANDMARKS = OrderedDict([
    # the thirteen key positions
    ("La Madeleine", (49.415, -1.178)),
    ("Sainte-Mere-Eglise", (49.408, -1.317)),
    ("Carentan", (49.303, -1.248)),
    ("Pointe du Hoc", (49.396, -0.989)),
    ("Les Moulins", (49.367, -0.873)),
    ("Port-en-Bessin", (49.346, -0.757)),
    ("Le Hamel", (49.338, -0.585)),
    ("Bayeux", (49.276, -0.703)),
    ("Courseulles", (49.336, -0.457)),
    ("Carpiquet Airfield", (49.182, -0.452)),
    ("Caen", (49.183, -0.370)),
    ("La Breche", (49.296, -0.302)),
    ("Pegasus Bridge", (49.242, -0.274)),
    # other landmarks
    ("Iles Saint-Marcouf", (49.496, -1.149)),
    ("Crisbecq Battery", (49.474, -1.279)),
    ("La Fiere Causeway", (49.404, -1.352)),
    ("Brecourt Manor", (49.390, -1.215)),
    ("Vierville Draw", (49.378, -0.905)),
    ("Longues Battery", (49.343, -0.693)),
    ("Douvres Radar Station", (49.287, -0.400)),
    ("Merville Battery", (49.271, -0.197)),
])
COASTAL_LANDMARKS = {"La Madeleine", "Pointe du Hoc", "Les Moulins", "Port-en-Bessin", "Le Hamel", "Courseulles",
                     "La Breche", "Vierville Draw", "Longues Battery", "Iles Saint-Marcouf"}
FREE_PLAY_STARTS = {"Allies": (49.300, -0.640), "Germany": (49.116, -1.091)}


# ---------------------------------------------------------------- rasterize

def is_land_point(x, y):
    return in_polygon(x, y, LAND_KM)


def build():
    tiles = {h: {"base": "Grassland", "features": [], "road": False, "wonder": None} for h in HEXES}

    def add(h, f):
        if f not in tiles[h]["features"]:
            tiles[h]["features"].append(f)

    water = {h for h in HEXES if not is_land_point(*POS[h])}
    for name, lat, lon in ISLANDS:
        water.discard(nearest_hex(lat, lon))
    for h in water:
        tiles[h]["base"] = "Coast"
    land = [h for h in HEXES if h not in water]
    coast_row = {h for h in land if any(n in water for n in neighbors(h))}

    plain = km_pts(CAEN_PLAIN)
    bocage_free = km_pts(BOCAGE_FREE)
    for h in land:
        x, y = POS[h]
        if in_polygon(x, y, plain) or noise(h, 1) < 0.18:
            tiles[h]["base"] = "Plains"

    # coast: beaches, bluffs and cliffs
    for h in coast_row:
        x, y = POS[h]
        lon = x / KM_PER_DEG_LON + LON0
        lat = y / KM_PER_DEG_LAT + LAT0
        feature = "Beach"
        if lat < 49.41 or lon > -1.12:          # the Calvados coast, not the Cotentin shore
            for lo, hi, f in COAST_SEGMENTS:
                if lo <= lon < hi:
                    feature = f
        add(h, feature)

    # hills and ridges
    for lat, lon, rx, ry in HILLS:
        cx, cy = ll_to_km(lat, lon)
        for h in land:
            if h not in coast_row and in_ellipse(*POS[h], cx, cy, rx, ry):
                add(h, "Hill")
    for pts in RIDGES.values():
        for h in hex_path(pts):
            if h in land and h not in coast_row and "Hill" not in tiles[h]["features"]:
                add(h, "Ridge")

    # flooding
    for poly in FLOODED_AREAS:
        p = km_pts(poly)
        for h in land:
            if h not in coast_row and in_polygon(*POS[h], p):
                tiles[h]["features"] = ["Flooded"]
    merderet = km_pts(RIVERS["Merderet"])
    for h in land:
        if h not in coast_row and dist_polyline(*POS[h], merderet) < MERDERET_FLOOD_KM:
            tiles[h]["features"] = ["Flooded"]

    # towns
    for name, (lat, lon) in TOWNS.items():
        h = nearest_hex(lat, lon)
        if h in water:
            continue
        tiles[h]["features"] = [f for f in tiles[h]["features"] if f in ("Hill", "Ridge")] + ["Town"]

    # woods
    for lat, lon, rx, ry, density in WOODS:
        cx, cy = ll_to_km(lat, lon)
        for h in land:
            t = tiles[h]
            if h in coast_row or "Town" in t["features"] or "Flooded" in t["features"]:
                continue
            if in_ellipse(*POS[h], cx, cy, rx, ry) and noise(h, 4) < density:
                add(h, "Forest")

    # the bocage: small fields walled by hedgerows on earth banks, everywhere west of the Caen plain
    for h in land:
        t = tiles[h]
        x, y = POS[h]
        if h in coast_row or t["features"] and any(f in t["features"] for f in ("Town", "Flooded", "Forest")):
            continue
        if in_polygon(x, y, bocage_free):
            continue
        open_country = in_polygon(x, y, plain)
        if noise(h, 5) < (0.12 if open_country else 0.62):
            add(h, "Bocage")
        elif noise(h, 6) < (0.10 if open_country else 0.30):
            add(h, "Orchard")

    # landmarks (natural wonders) replace whatever else is on the tile. A coastal landmark goes on the nearest shore
    # hex, any other on the nearest inland hex.
    landmark_hex = {}
    for name, (lat, lon) in LANDMARKS.items():
        px, py = ll_to_km(lat, lon)
        if name == "Iles Saint-Marcouf":
            pool = [nearest_hex(lat, lon)]
        elif name in COASTAL_LANDMARKS:
            pool = coast_row
        else:
            pool = [h for h in land if h not in coast_row]
        h = min((q for q in pool if tiles[q]["wonder"] is None),
                key=lambda q: (POS[q][0] - px) ** 2 + (POS[q][1] - py) ** 2)
        landmark_hex[name] = h
        tiles[h]["wonder"] = name
        tiles[h]["features"] = []
        tiles[h]["base"] = "Plains" if name in ("Carpiquet Airfield", "Caen") else "Grassland"

    # roads
    road_tiles = set()
    for pts in ROADS.values():
        road_tiles.update(h for h in hex_path(pts) if h not in water)
    for h in road_tiles:
        tiles[h]["road"] = True

    # rivers: edges between adjacent land tiles whose connecting segment crosses the river line
    rivers = set()
    for pts in RIVERS.values():
        p = km_pts(pts)
        segs = [(p[i], p[i + 1]) for i in range(len(p) - 1)]
        for h in land:
            for n in neighbors(h):
                if n in water or (n, h) in rivers or (h, n) in rivers:
                    continue
                if any(segments_intersect(POS[h], POS[n], a, b) for a, b in segs):
                    rivers.add((h, n))

    # cities
    cities = []
    objective_names = {o[0] for o in oob.OBJECTIVES}
    for name, side, lat, lon, capital, kind, _ in oob.ENTRIES:
        if name in objective_names:
            continue        # an airhead is also a key position: founded below
        h = nearest_hex(lat, lon)
        if kind == "fleet":
            assert h in water, name
            islands = {nearest_hex(la, lo) for _, la, lo in ISLANDS}   # no German can reach these
            near = min(hex_distance(h, l) for l in land if l not in islands)
            assert near >= 5, (name, "only %d hexes from the mainland" % near)
        else:
            assert h not in water, name
            tiles[h]["features"] = []
            tiles[h]["wonder"] = None
        cities.append({"name": name, "civ": side, "x": h[0], "y": h[1], "capital": capital, "objective": False,
                       "kind": kind})
    entries = {e[0]: e for e in oob.ENTRIES}
    for name, landmark, side, _ in oob.OBJECTIVES:
        h = landmark_hex[landmark]
        kind = entries[name][5] if name in entries else ("beach" if name in oob.BEACHES else "objective")
        cities.append({"name": name, "civ": side, "x": h[0], "y": h[1], "capital": False, "objective": True,
                       "kind": kind})

    # tidy feature order: Hill/Ridge first, then vegetation, then the rest (Unciv uses the last one for movement cost)
    order = ["Hill", "Ridge", "Forest", "Bocage", "Orchard", "Town", "Beach", "Bluffs", "Cliffs", "Flooded"]
    for t in tiles.values():
        t["features"] = sorted(set(t["features"]), key=order.index)

    LANDMARK_HEX.update(landmark_hex)
    return tiles, sorted(rivers), cities, road_tiles, water


LANDMARK_HEX = {}


def unit_positions(tiles, cities, water):
    """Tiles of every unit on the field at the start (oob.START). A tile holds one military and one civilian unit
    (generals and medics are civilians). A unit asked for a taken or unsuitable tile goes to the nearest free one:
    land units of the Allies may start on water (embarked), ships only on water, German units only on land, and
    nobody in an enemy city."""
    city_side = {(c["x"], c["y"]): c["civ"] for c in cities}
    taken = set()
    out = []
    for s in oob.START:
        side, key, inst, lat, lon = s[:5]
        health = s[5] if len(s) > 5 else 100
        civilian = key in oob.CIVILIAN_KEYS
        naval = key in oob.NAVAL_KEYS
        want = nearest_hex(lat, lon)

        def ok(h):
            if (h, civilian) in taken or city_side.get(h, side) != side:
                return False
            if key == "HQSHIP":
                return h in water and city_side.get(h) == side          # aboard: in its fleet city
            if naval:
                return h in water and (h not in city_side)
            if side == "Germany":
                return h not in water
            if key in ("BATT",):
                return h not in water
            return True

        h = want
        if not ok(h):
            same_kind = side == "Allies" and not naval and key != "BATT"   # stay embarked, or stay ashore
            ring = sorted((q for q in HEXES if ok(q) and (not same_kind or (q in water) == (want in water))),
                          key=lambda q: (hex_distance(q, want), noise(q, 9)))
            h = ring[0]
            print("  moved %s '%s' from %s to %s" % (oob.unit_name(side, key), inst, want, h))
        taken.add((h, civilian))
        out.append({"civ": side, "unit": oob.unit_name(side, key), "name": inst, "x": h[0], "y": h[1],
                    "health": health, "embarked": h in water and not naval})
    return out


def export(path):
    tiles, rivers, cities, roads, water = build()
    starts = []
    for nation, (lat, lon) in FREE_PLAY_STARTS.items():
        h = nearest_hex(lat, lon)
        assert h not in water
        starts.append({"x": h[0], "y": h[1], "nation": nation})
    data = {
        "width": WIDTH, "height": HEIGHT,
        "tiles": [{"x": h[0], "y": h[1], **t} for h, t in tiles.items()],
        "rivers": [[a[0], a[1], b[0], b[1]] for a, b in rivers],
        "cities": cities,
        "startUnits": unit_positions(tiles, cities, water),
        "startingLocations": starts,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    return data


if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    d = export(os.path.join(root, "build", "normandy_tiles.json"))
    combos = {}
    for t in d["tiles"]:
        k = "+".join([t["base"]] + t["features"]) if not t["wonder"] else t["base"] + "+" + t["wonder"]
        combos[k] = combos.get(k, 0) + 1
    print("tiles", len(d["tiles"]), "river edges", len(d["rivers"]), "cities", len(d["cities"]),
          "units", len(d["startUnits"]))
    for k, v in sorted(combos.items(), key=lambda kv: -kv[1]):
        print("  %4d  %s" % (v, k))
