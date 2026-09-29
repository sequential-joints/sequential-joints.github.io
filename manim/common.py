"""Shared palette + helpers for the PokeNet method animations.

Colours follow the architecture figure in the paper (Fig. 2).
Render with:  bash manim/render.sh
"""
import numpy as np
from manim import *

# ---------------------------------------------------------------- palette
BG = "#FFFFFF"
INK = "#1F2A2E"
MUTED = "#6B7780"
LINE = "#B8C2C8"

PN_PINK = "#F4C7C7"        # PointNet++
LOCAL_OR = "#F0A24B"       # per-frame local features
LOCAL_OR_L = "#FBE3C4"
ENC_YEL = "#FFF2CC"        # spatial / temporal encoder
DEC_YEL = "#FFE08A"        # joint set decoder
SEQ_GRN = "#5E9E4A"        # sequence encodings
SEQ_GRN_L = "#D5E8CC"
QUERY_PUR = "#E6CFE0"      # learnable joint queries
QUERY_PUR_D = "#9C6B8E"
SLOT_LAV = "#DCD4EE"       # refined joint slots
SLOT_LAV_D = "#6E5BA8"
STATE_RED = "#EB9A9A"      # joint state block
STATE_RED_D = "#C0282D"
HUNG_PEACH = "#F8C99A"     # Hungarian matching
CLS_GRAY = "#E6E8EA"

# point-cloud part colours
PC_BODY = "#6C7A89"
PC_DOOR = "#2E86AB"
PC_RACK = "#D9674A"
PC_HAND = "#C99A6B"

REV_COL = "#2E86AB"        # revolute joint colour
PRI_COL = "#D9674A"        # prismatic joint colour

# Same typefaces as the website (Inter for text, Space Grotesk for headings)
import os
import manimpango
_FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
for _f in ("Inter.ttf", "SpaceGrotesk.ttf"):
    manimpango.register_font(os.path.join(_FD, _f))
FONT = "Inter"
HEAD_FONT = "Space Grotesk"

config.background_color = BG
config.frame_rate = 30

_OVERSAMPLE = 4  # render text large then scale down: avoids Pango's uneven letter spacing


def T(s, size=24, color=INK, weight=NORMAL, font=None, **kw):
    font = font or (HEAD_FONT if weight == BOLD else FONT)
    t = Text(s, font=font, font_size=size * _OVERSAMPLE, color=color, weight=weight, **kw)
    return t.scale(1 / _OVERSAMPLE)


def M(s, size=30, color=INK, **kw):
    return MathTex(s, font_size=size, color=color, **kw)


def block(w, h, fill, label=None, size=22, dashed=True, stroke=INK, radius=0.18,
          vertical=False):
    """Rounded, optionally dashed block like the paper figure."""
    r = RoundedRectangle(width=w, height=h, corner_radius=radius,
                         fill_color=fill, fill_opacity=1, stroke_width=0)
    border = RoundedRectangle(width=w, height=h, corner_radius=radius,
                              stroke_color=stroke, stroke_width=2.2)
    if dashed:
        border = DashedVMobject(border, num_dashes=int((w + h) * 7), dashed_ratio=0.6)
    g = VGroup(r, border)
    if label:
        t = T(label, size=size, color=INK, weight=MEDIUM)
        if vertical:
            t.rotate(PI / 2)
        if t.width > w * 0.9:
            t.scale_to_fit_width(w * 0.9)
        t.move_to(r)
        g.add(t)
    g.body = r
    return g


def token(color, w=0.16, h=0.5, stroke=None):
    return RoundedRectangle(width=w, height=h, corner_radius=0.04, fill_color=color,
                            fill_opacity=1, stroke_color=stroke or color, stroke_width=1)


def token_col(n, color, light, w=0.16, h=0.5, buff=0.05):
    """A row of feature 'bars' fading from light -> saturated (as in the figure)."""
    cols = [interpolate_color(ManimColor(light), ManimColor(color), i / max(1, n - 1))
            for i in range(n)]
    return VGroup(*[token(c, w, h) for c in cols]).arrange(RIGHT, buff=buff)


def slot_shape(color=SLOT_LAV, stroke=INK, s=1.0):
    """Parallelogram used for joint queries / slots in the figure."""
    p = Polygon([-0.12, -0.3, 0], [0.2, -0.3, 0], [0.12, 0.3, 0], [-0.2, 0.3, 0],
                fill_color=color, fill_opacity=1, stroke_color=stroke, stroke_width=2)
    return p.scale(s)


def flow(a, b, color=LINE, sw=6, buff=0.1, tip=0.18):
    return Arrow(a, b, buff=buff, color=color, stroke_width=sw,
                 max_tip_length_to_length_ratio=0.5, tip_length=tip)




# ------------------------------------------------------ point-cloud object
PC_BODY_L = "#AEB8C2"      # faint face samples
PC_INNER = "#D5DBE0"       # interior (visible once the door opens)

# oblique projection: depth (z, into the screen) goes up-and-right
_KX, _KY = 0.5 * np.cos(np.radians(35)), 0.5 * np.sin(np.radians(35))


def _edge(a, b, step):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = max(2, int(round(np.linalg.norm(b - a) / step)) + 1)
    return np.linspace(a, b, n)


def _grid(origin, u, v, step, margin=0.5):
    """Regular grid of samples on the parallelogram origin + s*u + t*v (s,t in [0,1])."""
    origin, u, v = (np.asarray(x, float) for x in (origin, u, v))
    nu = max(1, int(np.linalg.norm(u) / step))
    nv = max(1, int(np.linalg.norm(v) / step))
    ss = (np.arange(nu) + margin) / nu
    tt = (np.arange(nv) + margin) / nv
    return np.array([origin + s * u + t * v for s in ss for t in tt])


class Dishwasher(VGroup):
    """A dishwasher drawn as a clean, structured 3-D point cloud.

    Object coords: x (width), y (height), z (depth, 0 = front, D = back).
    Joint 1, revolute: the door hinges about the bottom-front edge and folds toward the viewer (phi).
    Joint 2, prismatic: the rack slides out along -z (rho). It is hidden while the door is closed.
    """

    W, H, D = 1.6, 1.9, 1.45

    def __init__(self, detail=1.0, show_hand=True, dot_r=0.022, **_):
        super().__init__()
        W, H, D = self.W, self.H, self.D
        es = 0.07 / detail          # spacing along edges
        fs = 0.16 / detail          # spacing on faces
        x0, x1, y0, y1 = -W / 2, W / 2, -H / 2, H / 2
        self.center_off = np.array([_KX * D / 2, _KY * D / 2 - 0.25, 0])
        c = lambda x, y, z: (x, y, z)

        # ---- body: visible edges (strong) + top/right faces (faint) + interior (appears when open)
        vis_edges = [(c(x0, y1, 0), c(x1, y1, 0)), (c(x0, y0, 0), c(x1, y0, 0)),
                     (c(x0, y0, 0), c(x0, y1, 0)), (c(x1, y0, 0), c(x1, y1, 0)),
                     (c(x0, y1, 0), c(x0, y1, D)), (c(x1, y1, 0), c(x1, y1, D)),
                     (c(x1, y0, 0), c(x1, y0, D)), (c(x0, y1, D), c(x1, y1, D)),
                     (c(x1, y0, D), c(x1, y1, D))]
        edges = np.concatenate([_edge(a, b, es) for a, b in vis_edges])
        faces = np.concatenate([_grid((x0, y1, 0), (W, 0, 0), (0, 0, D), fs),
                                _grid((x1, y0, 0), (0, H, 0), (0, 0, D), fs)])
        inner = np.concatenate([_grid((x0, y0, D), (W, 0, 0), (0, H, 0), fs),   # back wall
                                _grid((x0, y0, 0), (W, 0, 0), (0, 0, D), fs)])  # floor
        self.body_pts = [edges, faces, inner]
        self.body = VGroup(*[Dot(radius=dot_r, color=PC_BODY) for _ in edges])
        self.faces = VGroup(*[Dot(radius=dot_r * 0.8, color=PC_BODY_L) for _ in faces])
        self.inner = VGroup(*[Dot(radius=dot_r * 0.75, color=PC_INNER) for _ in inner])

        # ---- door (local: hinge line on x-axis, height h along +y when closed)
        dh = H
        d_edges = np.concatenate([_edge((x0, 0, 0), (x1, 0, 0), es), _edge((x0, dh, 0), (x1, dh, 0), es),
                                  _edge((x0, 0, 0), (x0, dh, 0), es), _edge((x1, 0, 0), (x1, dh, 0), es)])
        d_face = _grid((x0, 0, 0), (W, 0, 0), (0, dh, 0), fs * 0.9)
        d_handle = _edge((-0.45, dh - 0.16, -0.05), (0.45, dh - 0.16, -0.05), es * 0.7)
        self.door_local = np.concatenate([d_edges, d_face, d_handle])
        nde, ndf = len(d_edges), len(d_face)
        self.door = VGroup(*[Dot(radius=dot_r * (1.0 if i < nde else 0.8 if i < nde + ndf else 1.25),
                                 color=PC_DOOR if i < nde or i >= nde + ndf else "#8CC0D6")
                             for i in range(len(self.door_local))])

        # ---- rack: wire basket with tines
        rx0, rx1, rz0, rz1 = x0 + 0.12, x1 - 0.12, 0.08, D - 0.1
        ry0, ry1 = y0 + 0.2, y0 + 0.5
        rk = []
        for y in (ry0, ry1):
            rk += [_edge((rx0, y, rz0), (rx1, y, rz0), es), _edge((rx0, y, rz1), (rx1, y, rz1), es),
                   _edge((rx0, y, rz0), (rx0, y, rz1), es), _edge((rx1, y, rz0), (rx1, y, rz1), es)]
        for x in (rx0, rx1):
            for z in (rz0, rz1):
                rk.append(_edge((x, ry0, z), (x, ry1, z), es))
        for z in np.linspace(rz0 + 0.2, rz1 - 0.2, 4):          # tines
            for x in np.linspace(rx0 + 0.15, rx1 - 0.15, 5):
                rk.append(_edge((x, ry0, z), (x, ry0 + 0.24, z), es))
        self.rack_local = np.concatenate(rk)
        self.rack = VGroup(*[Dot(radius=dot_r, color=PC_RACK) for _ in self.rack_local])

        # ---- hand: a tidy disc of samples at the contact point
        hp = [(0, 0, 0)]
        for r, n in ((0.06, 6), (0.12, 12)):
            hp += [(r * np.cos(a), r * np.sin(a), 0) for a in np.linspace(0, TAU, n, endpoint=False)]
        self.hand_local = np.array(hp)
        self.hand = VGroup(*[Dot(radius=dot_r * 1.2, color=PC_HAND) for _ in hp])

        self.add(self.inner, self.faces, self.body, self.rack, self.door)
        if show_hand:
            self.add(self.hand)
        self.origin = np.zeros(3)
        self.scale_f = 1.0
        self.phi, self.rho = 0.0, 0.0
        self.set_state(0, 0)

    # ---------------------------------------------------------- geometry
    def proj(self, P):
        P = np.atleast_2d(np.asarray(P, float))
        xy = np.c_[P[:, 0] + _KX * P[:, 2], P[:, 1] + _KY * P[:, 2], np.zeros(len(P))]
        return self.origin + self.scale_f * (xy - self.center_off)

    def world(self, p):
        return self.proj(p)[0]

    def _door_pts(self, phi):
        L = self.door_local
        c, s = np.cos(phi), np.sin(phi)
        y = L[:, 1] * c + L[:, 2] * s
        z = -L[:, 1] * s + L[:, 2] * c
        return np.c_[L[:, 0], -self.H / 2 + y, z]

    def _hand_pt(self, phi, rho):
        if rho < 1e-3:   # holding the door handle
            h = self.H - 0.16
            return np.array([0.3, -self.H / 2 + h * np.cos(phi), -h * np.sin(phi) - 0.06])
        return np.array([0.0, -self.H / 2 + 0.5, 0.08 - rho])

    def _set(self, grp, P):
        for dot, p in zip(grp, self.proj(P)):
            dot.move_to(p)

    def set_state(self, phi, rho):
        self.phi, self.rho = phi, rho
        self._set(self.door, self._door_pts(phi))
        self._set(self.rack, self.rack_local + np.array([0, 0, -rho]))
        hp = self.proj([self._hand_pt(phi, rho)])[0]
        for dot, q in zip(self.hand, self.hand_local):
            dot.move_to(hp + self.scale_f * q)
        # the interior and rack are occluded until the door is mostly open
        vis = float(np.clip((phi - 0.8) / 0.5, 0, 1))
        self.rack.set_opacity(vis)
        self.inner.set_opacity(vis)
        return self

    def place(self, center, scale):
        self.origin = np.array(center, dtype=float)
        k = scale / self.scale_f
        self.scale_f = scale
        for grp in (self.inner, self.faces, self.body, self.door, self.rack, self.hand):
            for dot in grp:
                dot.scale(k)
        for grp, P in zip((self.body, self.faces, self.inner), self.body_pts):
            self._set(grp, P)
        return self.set_state(self.phi, self.rho)

    # ---------------------------------------------------------- joint axes (world coords)
    def hinge_axis(self, ext=0.45):
        W, H = self.W, self.H
        return self.world((-W / 2 - ext, -H / 2, 0)), self.world((W / 2 + ext, -H / 2, 0))

    def slide_axis(self, length=1.3):
        a = np.array([self.W / 2 + 0.3, -self.H / 2 + 0.35, 0.6])
        return self.world(a), self.world(a + np.array([0, 0, -length]))


def demo_state(u):
    """Canonical demonstration: door opens (u<0.5), then rack slides (u>=0.5)."""
    u = np.clip(u, 0, 1)
    phi = PI / 2 * smooth(np.clip(u / 0.5, 0, 1))
    rho = 1.1 * smooth(np.clip((u - 0.5) / 0.5, 0, 1))
    return phi, rho


def revolute_axis(obj, color=REV_COL, sw=4):
    a, b = obj.hinge_axis()
    return DashedLine(a, b, color=color, stroke_width=sw, dash_length=0.08)


def prismatic_axis(obj, color=PRI_COL, sw=4, length=1.5, tip=0.16):
    a, b = obj.slide_axis(length)
    return Arrow(a, b, buff=0, color=color, stroke_width=sw, tip_length=tip,
                 max_tip_length_to_length_ratio=0.3)
