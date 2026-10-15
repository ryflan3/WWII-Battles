"""UI graphics: portrait background, nation icons, leader portraits, promotion, building, resource and improvement icons
(white vector shapes that Unciv tints)."""
import math
from PIL import Image, ImageDraw, ImageFilter
from figures import *


def portrait_background():
    big = 512
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([8, 8, big - 8, big - 8], fill=(186, 190, 168, 255), outline=(52, 58, 40, 255), width=18)
    d.ellipse([40, 40, big - 40, big - 40], outline=(130, 136, 108, 255), width=6)
    return img.resize((128, 128), Image.LANCZOS)


# ------------------------------------------------------------------ vector helpers (white icons)

def vcanvas(n=400):
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def star_points(cx, cy, r, inner=0.38, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def finish_icon(img, size=100):
    return img.resize((size, size), Image.LANCZOS)


W8 = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def vector_icon(fn):
    img, d = vcanvas()
    fn(d)
    return finish_icon(img)


def nation_allies():
    """The SHAEF shoulder patch: a flaming crusader's sword rising from darkness toward a rainbow of peace."""
    img, d = vcanvas()
    d.pieslice([30, 40, 370, 380], 180, 360, fill=W8)                   # the shield-shaped patch, top
    d.rectangle([30, 210, 370, 260], fill=W8)
    d.polygon([(30, 260), (370, 260), (200, 380)], fill=W8)
    d.arc([70, 90, 330, 350], 190, 350, fill=CLEAR, width=22)           # rainbow
    d.polygon([(186, 330), (214, 330), (210, 150), (200, 120), (190, 150)], fill=CLEAR)     # sword blade
    d.rectangle([150, 300, 250, 316], fill=CLEAR)                       # cross-guard
    for i, dx in enumerate((-46, -24, 24, 46)):                         # flames
        d.polygon([(200 + dx * 0.4, 200), (200 + dx, 150 - abs(dx) // 2), (200 + dx * 0.7, 210)], fill=CLEAR)
    return finish_icon(img)


def nation_germany():
    """The Balkenkreuz, the cross marking of the German armed forces."""
    img, d = vcanvas()
    d.rectangle([150, 40, 250, 360], fill=W8)
    d.rectangle([40, 150, 360, 250], fill=W8)
    d.rectangle([180, 70, 220, 330], fill=CLEAR)
    d.rectangle([70, 180, 330, 220], fill=CLEAR)
    return finish_icon(img)


def leader_portrait(name):
    """Black-and-white press-photo style bust portraits."""
    n = 512
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg, frame = (196, 194, 184, 255), (40, 40, 38, 255)
    d.ellipse([24, 10, n - 24, n - 10], fill=bg)
    vig = Image.new("L", (n, n), 0)
    ImageDraw.Draw(vig).ellipse([60, 46, n - 60, n - 46], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(40))
    dark = Image.new("RGBA", (n, n), (96, 96, 92, 255))
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse([24, 10, n - 24, n - 10], fill=255)
    mask = Image.composite(Image.new("L", (n, n), 0), mask, vig)
    img.paste(dark, (0, 0), mask.point(lambda v: int(v * 0.55)))
    d = ImageDraw.Draw(img)
    ike = name == "Dwight D. Eisenhower"
    coat = (104, 98, 76) if ike else (112, 116, 104)
    coat_d = shade(coat, 0.75)
    skin, skin_d = (216, 186, 154), (180, 148, 118)
    # shoulders and jacket
    d.polygon([(70, 500), (110, 362), (200, 334), (312, 334), (402, 362), (442, 500)], fill=coat)
    if ike:
        # the short 'Ike jacket', shirt and tie, five stars on the shoulder loops
        d.polygon([(206, 334), (256, 430), (306, 334)], fill=(188, 172, 136))
        d.polygon([(246, 350), (256, 440), (266, 350)], fill=(118, 104, 72))
        for x0 in (120, 330):
            d.rectangle([x0, 356, x0 + 66, 374], fill=coat_d)
            for k in range(5):
                d.polygon(star_points(x0 + 8 + k * 12.5, 365, 7), fill=(230, 224, 200))
    else:
        # field-grey tunic, collar patches, the Pour le Mérite at the throat
        d.polygon([(200, 334), (256, 452), (312, 334)], fill=coat_d)
        d.polygon([(216, 334), (256, 400), (296, 334)], fill=(220, 218, 206))
        d.rectangle([186, 346, 226, 372], fill=(200, 60, 50)); d.rectangle([286, 346, 326, 372], fill=(200, 60, 50))
        d.polygon([(256, 380), (268, 400), (256, 420), (244, 400)], fill=(60, 80, 140))
        d.ellipse([244, 424, 268, 448], fill=(30, 30, 30))                  # Knight's Cross
    # neck and head
    d.rectangle([226, 290, 286, 340], fill=skin_d)
    d.ellipse([184, 120, 328, 312], fill=skin)
    d.ellipse([174, 196, 194, 242], fill=skin_d); d.ellipse([318, 196, 338, 242], fill=skin_d)
    if ike:
        d.chord([188, 120, 324, 196], 180, 360, fill=(200, 176, 140))      # high bald crown
        d.rectangle([184, 168, 198, 214], fill=(170, 150, 120)); d.rectangle([314, 168, 328, 214], fill=(170, 150, 120))
        for x in (228, 284):
            d.ellipse([x - 9, 202, x + 9, 212], fill=(60, 56, 52))
            d.line([x - 15, 190, x + 13, 188], fill=(150, 130, 100), width=5)
        d.polygon([(256, 206), (246, 252), (266, 252)], fill=skin_d)
        d.chord([214, 252, 298, 300], 0, 180, fill=(250, 248, 240))         # the famous grin
        d.arc([214, 244, 298, 300], 10, 170, fill=(150, 110, 90), width=4)
    else:
        # peaked field cap with the goggles he took from a British general in the desert
        d.polygon([(176, 176), (336, 176), (350, 196), (162, 196)], fill=(90, 94, 84))
        d.chord([184, 92, 328, 210], 180, 360, fill=(104, 108, 96))
        d.rectangle([186, 160, 326, 178], fill=(70, 74, 66))
        d.ellipse([200, 132, 240, 160], fill=(170, 190, 200)); d.ellipse([272, 132, 312, 160], fill=(170, 190, 200))
        d.ellipse([207, 139, 233, 153], fill=(110, 130, 140)); d.ellipse([279, 139, 305, 153], fill=(110, 130, 140))
        d.polygon([(236, 196), (276, 196), (256, 210)], fill=(80, 80, 76))   # visor
        for x in (228, 284):
            d.ellipse([x - 9, 214, x + 9, 224], fill=(56, 52, 48))
            d.line([x - 15, 204, x + 13, 204], fill=(110, 96, 80), width=5)
        d.polygon([(256, 216), (244, 262), (268, 262)], fill=skin_d)
        d.line([232, 282, 280, 282], fill=(120, 90, 76), width=5)
    d.ellipse([24, 10, n - 24, n - 10], outline=frame, width=16)
    d.ellipse([46, 32, n - 46, n - 32], outline=(140, 138, 128, 255), width=4)
    cut = Image.new("L", (n, n), 0)
    ImageDraw.Draw(cut).ellipse([24, 10, n - 24, n - 10], fill=255)
    img.putalpha(Image.composite(img.split()[3], Image.new("L", (n, n), 0), cut))
    # a press photograph: render everything in monochrome
    g = img.convert("LA").convert("RGBA")
    g.putalpha(img.split()[3])
    return g.resize((256, 256), Image.LANCZOS)


# ------------------------------------------------------------------ promotion icons

def pi_flag(d):
    d.rectangle([110, 60, 130, 360], fill=W8)
    d.polygon([(130, 70), (310, 110), (130, 200)], fill=W8)


def pi_shovel(d):
    d.polygon([(90, 330), (250, 140), (270, 160), (110, 350)], fill=W8)
    d.polygon([(240, 120), (300, 60), (350, 110), (290, 170)], fill=W8)
    d.ellipse([60, 320, 120, 380], outline=W8, width=18)


def pi_arrow(d):
    for off in (0, 110):
        d.polygon([(60 + off, 90), (160 + off, 200), (60 + off, 310), (110 + off, 310), (210 + off, 200), (110 + off, 90)], fill=W8)


def pi_hedge(d):
    d.rectangle([30, 250, 370, 330], fill=W8)
    for x in range(50, 370, 64):
        d.ellipse([x - 44, 140, x + 44, 270], fill=W8)


def pi_house(d):
    d.polygon([(60, 190), (200, 60), (340, 190)], fill=W8)
    d.rectangle([90, 190, 310, 350], fill=W8)
    d.rectangle([170, 260, 230, 350], fill=CLEAR)
    d.rectangle([110, 210, 150, 250], fill=CLEAR); d.rectangle([250, 210, 290, 250], fill=CLEAR)


def pi_bazooka(d):
    d.polygon([(40, 250), (320, 130), (336, 166), (56, 286)], fill=W8)
    d.ellipse([300, 110, 370, 190], fill=W8)
    d.rectangle([150, 220, 172, 300], fill=W8)


def pi_boot(d):
    d.polygon([(140, 50), (230, 50), (230, 250), (330, 280), (340, 340), (120, 340), (130, 250)], fill=W8)


def pi_chevrons(d):
    for i in range(3):
        y = 90 + i * 80
        d.polygon([(60, y + 60), (200, y), (340, y + 60), (340, y + 110), (200, y + 50), (60, y + 110)], fill=W8)


def pi_cross(d):
    d.rectangle([160, 60, 240, 340], fill=W8)
    d.rectangle([60, 160, 340, 240], fill=W8)


def pi_crosshair(d):
    d.ellipse([60, 60, 340, 340], outline=W8, width=30)
    d.rectangle([185, 30, 215, 370], fill=W8)
    d.rectangle([30, 185, 370, 215], fill=W8)


def pi_tank(d):
    d.rounded_rectangle([40, 230, 360, 320], radius=40, fill=W8)
    d.rectangle([70, 180, 300, 236], fill=W8)
    d.rectangle([140, 120, 260, 186], fill=W8)
    d.rectangle([250, 140, 380, 160], fill=W8)
    for x in (90, 160, 230, 300):
        d.ellipse([x - 22, 254, x + 22, 298], fill=CLEAR)


def pi_hull_down(d):
    d.chord([0, 210, 400, 560], 180, 360, fill=W8)
    d.rectangle([140, 140, 260, 210], fill=W8)
    d.rectangle([250, 160, 380, 180], fill=W8)


def pi_tank_kill(d):
    pi_tank(d)
    d.line([60, 60, 340, 340], fill=CLEAR, width=40)
    d.line([60, 60, 340, 340], fill=W8, width=18)


def pi_breakthrough(d):
    d.polygon([(40, 160), (240, 160), (240, 80), (380, 200), (240, 320), (240, 240), (40, 240)], fill=W8)


def pi_helmet(d):
    d.chord([60, 80, 340, 380], 180, 360, fill=W8)
    d.rectangle([40, 222, 360, 252], fill=W8)


def pi_binoculars(d):
    for x in (130, 270):
        d.ellipse([x - 70, 170, x + 70, 330], fill=W8)
        d.ellipse([x - 40, 200, x + 40, 300], fill=CLEAR)
        d.rectangle([x - 40, 90, x + 40, 200], fill=W8)
    d.rectangle([180, 160, 220, 240], fill=W8)


def pi_cannon(d):
    d.polygon([(60, 170), (330, 120), (340, 160), (70, 230)], fill=W8)
    d.ellipse([110, 180, 250, 320], outline=W8, width=26)
    d.line([180, 250, 40, 340], fill=W8, width=24)


def pi_plane(d):
    d.polygon([(40, 190), (360, 190), (360, 220), (40, 220)], fill=W8)          # wing
    d.polygon([(180, 100), (220, 100), (230, 330), (170, 330)], fill=W8)        # fuselage
    d.rectangle([130, 300, 270, 330], fill=W8)
    d.ellipse([180, 70, 220, 110], fill=W8)


def pi_range(d):
    d.arc([40, 80, 360, 420], 200, 340, fill=W8, width=24)
    d.polygon([(320, 150), (370, 230), (290, 220)], fill=W8)
    d.ellipse([20, 260, 80, 320], fill=W8)


def pi_wheels(d):
    for x in (110, 290):
        d.ellipse([x - 70, 200, x + 70, 340], outline=W8, width=26)
    d.polygon([(60, 120), (260, 120), (260, 60), (360, 150), (260, 240), (260, 180), (60, 180)], fill=W8)


def pi_eye(d):
    d.chord([40, 110, 360, 290], 180, 360, fill=W8)
    d.chord([40, 110, 360, 290], 0, 180, fill=W8)
    d.ellipse([140, 140, 260, 260], fill=CLEAR)
    d.ellipse([175, 175, 225, 225], fill=W8)


def pi_anchor(d):
    d.ellipse([170, 30, 230, 90], outline=W8, width=18)
    d.rectangle([188, 86, 212, 340], fill=W8)
    d.rectangle([120, 120, 280, 142], fill=W8)
    d.arc([70, 180, 330, 370], 0, 180, fill=W8, width=26)
    d.polygon([(60, 270), (100, 230), (110, 290)], fill=W8)
    d.polygon([(340, 270), (300, 230), (290, 290)], fill=W8)


def pi_shell(d):
    d.rounded_rectangle([150, 120, 250, 360], radius=10, fill=W8)
    d.chord([150, 30, 250, 230], 180, 360, fill=W8)
    d.rectangle([150, 280, 250, 300], fill=CLEAR)


def pi_wrench(d):
    d.polygon([(110, 330), (270, 170), (300, 200), (140, 360)], fill=W8)
    d.ellipse([230, 50, 370, 190], fill=W8)
    d.polygon([(290, 60), (340, 110), (310, 140), (260, 90)], fill=CLEAR)


def pi_us_general(d):
    d.rectangle([40, 150, 360, 250], outline=W8, width=22)
    for x in (130, 270):
        d.polygon(star_points(x, 200, 44), fill=W8)


def pi_br_general(d):
    # crossed sword and baton, the insignia of a British general officer
    d.line([80, 320, 320, 80], fill=W8, width=30)
    d.line([80, 80, 320, 320], fill=W8, width=40)
    d.ellipse([170, 170, 230, 230], fill=W8)
    d.chord([120, 20, 280, 140], 180, 360, fill=W8)       # crown
    d.rectangle([120, 80, 280, 110], fill=W8)


def pi_de_general(d):
    # collar patch with the gold 'Larisch' embroidery of a German general
    d.rounded_rectangle([80, 60, 320, 340], radius=30, outline=W8, width=24)
    for y in (120, 200, 280):
        d.arc([120, y - 50, 280, y + 30], 200, 340, fill=W8, width=22)
        d.ellipse([186, y - 26, 214, y + 2], fill=W8)


PROMOTION_ICONS = {
    "Rally": pi_flag, "Dug In": pi_shovel, "Assault": pi_arrow, "Hedgerow Fighting": pi_hedge, "Street Fighting": pi_house,
    "Bazooka Teams": pi_bazooka, "Forced March": pi_boot, "Veterans": pi_chevrons, "Battalion Aid Station": pi_cross,
    "Gunnery": pi_crosshair, "Hull Down": pi_hull_down, "Tank Killers": pi_tank_kill, "Exploitation": pi_breakthrough,
    "Infantry Support": pi_helmet, "Fire Direction": pi_binoculars, "Counter-Battery": pi_cannon,
    "Air Observation Post": pi_plane, "Long Range": pi_range, "Shoot and Scoot": pi_wheels, "Ambush": pi_eye,
    "Naval Gunfire": pi_shell, "Damage Control": pi_wrench,
}


# ------------------------------------------------------------------ building, resource and improvement icons

def bi_headquarters(d):
    d.polygon([(40, 340), (200, 120), (360, 340)], fill=W8)
    d.polygon([(170, 340), (200, 230), (230, 340)], fill=CLEAR)
    d.rectangle([194, 30, 206, 130], fill=W8)
    d.polygon([(206, 30), (310, 55), (206, 85)], fill=W8)


def bi_depot(d):
    for x, y in ((50, 230), (170, 230), (110, 120)):           # crates
        d.rectangle([x, y, x + 110, y + 110], fill=W8)
        d.line([x, y, x + 110, y + 110], fill=CLEAR, width=10)
    for x in (290, 340):                                        # jerrycans
        d.rounded_rectangle([x - 22, 200, x + 22, 340], radius=8, fill=W8)
        d.line([x - 22, 250, x + 22, 250], fill=CLEAR, width=8)


def bi_hedgehog(d):
    d.line([60, 340, 340, 80], fill=W8, width=34)
    d.line([60, 80, 340, 340], fill=W8, width=34)
    d.line([200, 40, 200, 370], fill=W8, width=34)
    d.rectangle([40, 340, 360, 370], fill=W8)


def bi_anchor(d):
    pi_anchor(d)


def bi_landing(d):
    """A landing craft with its ramp down."""
    d.polygon([(40, 220), (290, 220), (290, 320), (60, 320)], fill=W8)
    d.polygon([(290, 220), (380, 300), (360, 330), (290, 300)], fill=W8)
    d.rectangle([60, 180, 110, 220], fill=W8)
    for x in (140, 190, 240):
        d.chord([x - 22, 170, x + 22, 214], 180, 360, fill=W8)
    d.line([20, 350, 380, 350], fill=W8, width=14)


def bi_arrivals(d):
    d.polygon([(130, 380), (180, 20), (220, 20), (270, 380)], fill=W8)
    d.rectangle([194, 60, 206, 100], fill=CLEAR); d.rectangle([194, 170, 206, 220], fill=CLEAR); d.rectangle([194, 290, 206, 340], fill=CLEAR)
    d.polygon([(40, 200), (110, 130), (110, 170), (150, 170), (150, 230), (110, 230), (110, 270)], fill=W8)
    d.polygon([(360, 200), (290, 130), (290, 170), (250, 170), (250, 230), (290, 230), (290, 270)], fill=W8)


def bi_glider(d):
    d.polygon([(30, 190), (370, 170), (370, 200), (30, 220)], fill=W8)      # wing
    d.polygon([(80, 230), (340, 210), (360, 250), (90, 270)], fill=W8)       # fuselage
    d.polygon([(40, 220), (80, 160), (100, 240)], fill=W8)                   # tail fin


def pi_hillflag(d):
    d.chord([20, 220, 380, 500], 180, 360, fill=W8)
    d.rectangle([190, 60, 210, 250], fill=W8)
    d.polygon([(210, 60), (330, 95), (210, 140)], fill=W8)


def ri_calendar(d):
    d.rounded_rectangle([60, 80, 340, 350], radius=24, fill=W8)
    d.rectangle([60, 150, 340, 166], fill=CLEAR)
    for x in (130, 270):
        d.rounded_rectangle([x - 14, 40, x + 14, 120], radius=12, fill=W8)
        d.ellipse([x - 22, 92, x + 22, 136], fill=CLEAR)
        d.rounded_rectangle([x - 9, 50, x + 9, 120], radius=8, fill=W8)
    for row in range(3):
        for col in range(4):
            x, y = 100 + col * 58, 195 + row * 50
            d.rectangle([x, y, x + 30, y + 26], fill=CLEAR)


def ri_watch(d):
    """A wristwatch."""
    d.rounded_rectangle([150, 20, 250, 110], radius=10, fill=W8)
    d.rounded_rectangle([150, 290, 250, 380], radius=10, fill=W8)
    d.ellipse([80, 90, 320, 310], fill=W8)
    d.ellipse([104, 114, 296, 286], fill=CLEAR)
    d.ellipse([118, 128, 282, 272], fill=W8)
    d.line([200, 200, 200, 140], fill=CLEAR, width=16)
    d.line([200, 200, 250, 225], fill=CLEAR, width=14)
    d.rectangle([318, 186, 340, 214], fill=W8)


def ri_scroll(d):
    d.rounded_rectangle([90, 70, 310, 330], radius=20, fill=W8)
    d.ellipse([60, 40, 340, 110], fill=W8)
    d.ellipse([60, 290, 340, 360], fill=W8)
    for y in (140, 185, 230, 275):
        d.line([130, y, 270, y], fill=CLEAR, width=12)


def ii_foxholes(d):
    for cx in (120, 280):
        d.chord([cx - 100, 200, cx + 100, 360], 180, 360, fill=W8)
        d.ellipse([cx - 60, 230, cx + 60, 300], fill=CLEAR)
        d.chord([cx - 40, 150, cx + 40, 250], 180, 360, fill=W8)        # a helmet peering out
    d.rectangle([20, 330, 380, 350], fill=W8)
