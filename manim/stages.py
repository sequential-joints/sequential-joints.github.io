"""Per-component animations for the Method section.

Scenes:  SpatialEncoding, TemporalEncoding, JointSetDecoder, JointStates, Matching
"""
from common import *


def heading(num, text):
    badge = VGroup(Circle(radius=0.26, fill_color=INK, fill_opacity=1, stroke_width=0),
                   T(str(num), 20, "#FFFFFF", weight=BOLD))
    t = T(text, 28, weight=BOLD)
    g = VGroup(badge, t).arrange(RIGHT, buff=0.22).to_corner(UL, buff=0.4)
    return g


def fade_all(scene, keep=()):
    scene.play(*[FadeOut(m) for m in scene.mobjects if m not in keep], run_time=0.7)


# ============================================================ 1. spatial
class SpatialEncoding(Scene):
    def construct(self):
        h = heading(1, "Spatial encoding: one frame → one token")
        self.add(h)

        obj = Dishwasher().place([-4.3, -0.1, 0], 1.15)
        obj.set_state(*demo_state(0.62))
        lbl = M("P_t \\in \\mathbb{R}^{N\\times 3}", 30).next_to(obj, DOWN, buff=0.5)
        self.play(FadeIn(obj, lag_ratio=0.002), FadeIn(lbl), run_time=1.4)

        # PointNet++ : farthest point sampling + ball grouping
        allpts = [d for g in (obj.body, obj.faces, obj.door, obj.rack) for d in g if d.get_fill_opacity() > 0.5]
        P = np.array([d.get_center() for d in allpts])
        Q = 7
        idx = [0]
        dist = np.linalg.norm(P - P[0], axis=1)
        for _ in range(Q - 1):
            i = int(np.argmax(dist))
            idx.append(i)
            dist = np.minimum(dist, np.linalg.norm(P - P[i], axis=1))
        cents = [P[i] for i in idx]
        tag = T("PointNet++: sample centroids, group neighbours", 20, MUTED).to_edge(LEFT, buff=0.6).set_y(2.5)
        rings = VGroup(*[Circle(radius=0.55, color=LOCAL_OR, stroke_width=2.5,
                                fill_color=LOCAL_OR, fill_opacity=0.12).move_to(c) for c in cents])
        cdots = VGroup(*[Dot(c, radius=0.06, color=LOCAL_OR_L, stroke_color=INK, stroke_width=1.5)
                         for c in cents])
        self.play(FadeIn(tag), LaggedStart(*[GrowFromCenter(d) for d in cdots], lag_ratio=0.12),
                  run_time=1.0)
        self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.1), run_time=1.0)

        # each group becomes a local feature token
        cols = [interpolate_color(ManimColor(LOCAL_OR_L), ManimColor(LOCAL_OR), i / (Q - 1))
                for i in range(Q)]
        toks = VGroup(*[token(c, 0.28, 1.1, stroke=LOCAL_OR) for c in cols]).arrange(RIGHT, buff=0.1)
        cls = token(CLS_GRAY, 0.28, 1.1, stroke=INK)
        row = VGroup(cls, toks).arrange(RIGHT, buff=0.22).move_to([2.9, -0.2, 0])
        self.play(*[ReplacementTransform(VGroup(rings[i], cdots[i]), toks[i]) for i in range(Q)],
                  obj.animate.set_opacity(0.25), run_time=1.3)
        xl = M("X_t=\\{x_{t,1},\\dots,x_{t,Q}\\}", 26).next_to(toks, DOWN, buff=0.75)
        cl = T("[CLS]", 16, weight=BOLD).next_to(cls, DOWN, buff=0.75).align_to(xl, DOWN)
        self.play(FadeIn(cls, shift=0.3 * RIGHT), FadeIn(cl), FadeIn(xl), run_time=0.7)

        enc = block(row.width + 0.8, 2.3, ENC_YEL, None).move_to(row).shift(0.05 * UP)
        enc_l = T("Spatial Encoder (transformer)", 18, weight=MEDIUM).next_to(enc, UP, buff=0.12)
        self.add(enc)
        self.bring_to_front(row)
        self.play(FadeIn(enc), FadeIn(enc_l), FadeOut(tag), run_time=0.6)

        # CLS attends over the local tokens
        w = [0.9, 0.3, 0.6, 1.0, 0.2, 0.7, 0.45]
        arcs = VGroup(*[ArcBetweenPoints(cls.get_top(), t.get_top(), angle=-PI / 2.5,
                                         color=SEQ_GRN, stroke_width=1 + 5 * wi,
                                         stroke_opacity=0.35 + 0.6 * wi) for t, wi in zip(toks, w)])
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.08), run_time=1.2)
        self.play(cls.animate.set_fill(SEQ_GRN).set_stroke(SEQ_GRN), run_time=0.5)
        self.play(FadeOut(arcs), run_time=0.3)

        out = token(SEQ_GRN, 0.3, 0.9, stroke=SEQ_GRN)
        out_l = M("\\hat c_t \\in \\mathbb{R}^{D}", 30)
        out_c = T("frame-level representation", 18, MUTED)
        VGroup(out, out_l, out_c).arrange(RIGHT, buff=0.3).move_to([2.9, -3.05, 0])
        self.play(TransformFromCopy(cls, out), FadeIn(out_l), FadeIn(out_c), run_time=1.0)
        self.wait(2.0)
        fade_all(self)


# ============================================================ 2. temporal
class TemporalEncoding(Scene):
    def construct(self):
        h = heading(2, "Temporal encoding: reasoning across frames")
        self.add(h)
        NT = 6
        xs = np.linspace(-5.3, 5.3, NT)
        frames = VGroup()
        for i, x in enumerate(xs):
            d = Dishwasher(detail=0.55, dot_r=0.03).place([x - 0.15, 1.35, 0], 0.4)
            d.set_state(*demo_state(i / (NT - 1)))
            frames.add(d)
        tl = VGroup(*[M(f"t={i + 1}" if i < NT - 1 else "t=T", 22, MUTED).move_to([x, 2.5, 0])
                      for i, x in enumerate(xs)])
        self.play(LaggedStart(*[FadeIn(f, shift=0.2 * DOWN) for f in frames], lag_ratio=0.12),
                  FadeIn(tl), run_time=1.3)

        toks = VGroup(*[token(SEQ_GRN_L, 0.3, 0.9, stroke=SEQ_GRN).move_to([x, -0.6, 0]) for x in xs])
        cl = VGroup(*[M(f"\\hat c_{{{i + 1 if i < NT - 1 else 'T'}}}", 24).next_to(t, RIGHT, buff=0.08)
                      for i, t in enumerate(toks)])
        self.play(*[TransformFromCopy(f, t) for f, t in zip(frames, toks)], FadeIn(cl), run_time=1.0)

        enc = block(12.2, 1.5, ENC_YEL, None).move_to([0, -0.6, 0])
        enc_l = T("Temporal Encoder (transformer over time)", 18, weight=MEDIUM).next_to(enc, UP, buff=0.1)
        self.add(enc)
        self.bring_to_front(toks, cl)
        self.play(FadeIn(enc), FadeIn(enc_l), run_time=0.5)

        # show attention for two query frames: when the door finishes, and when the rack moves
        for q, weights in ((2, [0.3, 0.9, 1.0, 0.8, 0.2, 0.1]), (4, [0.1, 0.2, 0.7, 0.9, 1.0, 0.8])):
            hl = SurroundingRectangle(toks[q], color=SEQ_GRN, buff=0.08, stroke_width=3)
            arcs = VGroup(*[ArcBetweenPoints(toks[q].get_bottom(), toks[j].get_bottom(),
                                             angle=PI / 3 if j > q else -PI / 3,
                                             color=SEQ_GRN, stroke_width=1 + 6 * w,
                                             stroke_opacity=0.3 + 0.7 * w)
                            for j, w in enumerate(weights) if j != q])
            self.play(Create(hl), LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.08),
                      run_time=1.0)
            self.wait(0.4)
            self.play(FadeOut(hl), FadeOut(arcs), run_time=0.4)

        # outputs = temporal memory
        mem = VGroup(*[token(interpolate_color(ManimColor(SEQ_GRN_L), ManimColor(SEQ_GRN), i / (NT - 1)),
                             0.3, 0.9, stroke=SEQ_GRN).move_to([x, -2.75, 0]) for i, x in enumerate(xs)])
        arrs = VGroup(*[flow([x, -1.4, 0], [x, -2.25, 0], sw=4, tip=0.14, buff=0.02) for x in xs])
        ml = T("sequence encodings = memory for the decoders", 20, MUTED).next_to(mem, DOWN, buff=0.2)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.05),
                  LaggedStart(*[GrowFromEdge(m, UP) for m in mem], lag_ratio=0.08),
                  FadeIn(ml), run_time=1.2)
        self.wait(2.0)
        fade_all(self)


# ======================================================= 3. joint set decoder
class JointSetDecoder(Scene):
    def construct(self):
        h = heading(3, "Joint set decoder: K queries → K joint hypotheses")
        self.add(h)
        K = 5

        mem = token_col(6, SEQ_GRN, SEQ_GRN_L, 0.2, 0.75, 0.06).move_to([-5.4, 1.1, 0])
        mem_l = T("memory", 16, MUTED).next_to(mem, UP, buff=0.12)
        qs = VGroup(*[slot_shape(QUERY_PUR_D, s=0.75) for _ in range(K)]).arrange(DOWN, buff=0.18)
        qs.move_to([-5.4, -1.8, 0]).rotate(0)
        qs.arrange(RIGHT, buff=0.12).move_to([-5.4, -1.3, 0])
        q_l = T("K learnable queries", 16, MUTED).next_to(qs, DOWN, buff=0.12)
        self.play(FadeIn(mem), FadeIn(mem_l), LaggedStart(*[FadeIn(q, shift=0.2 * UP) for q in qs],
                                                         lag_ratio=0.1), FadeIn(q_l), run_time=1.0)

        # cross attention
        lines = VGroup(*[Line(q.get_top(), m.get_bottom(), color=SEQ_GRN, stroke_width=1.5,
                              stroke_opacity=0.5) for q in qs for m in mem])
        ca = T("cross-attention", 16, SEQ_GRN).next_to(lines, LEFT, buff=0.1).shift(0.2 * RIGHT)
        ca.move_to([-5.4, -0.1, 0]).shift(1.4 * RIGHT)
        self.play(Create(lines), FadeIn(ca), run_time=1.0)
        self.play(FadeOut(lines), FadeOut(ca), run_time=0.3)

        # table of slot predictions
        heads = ["c", "\\tau", "d", "p", "o"]
        vals = [
            ["0.94", "\\text{rev}", "(1,0,0)", "(0,\\!-0.95,0)", "0.03"],
            ["0.05", "\\cdot", "\\cdot", "\\cdot", "\\cdot"],
            ["0.91", "\\text{pri}", "(0,0,\\!-1)", "(0,\\!-0.6,0.6)", "0.96"],
            ["0.07", "\\cdot", "\\cdot", "\\cdot", "\\cdot"],
            ["0.04", "\\cdot", "\\cdot", "\\cdot", "\\cdot"],
        ]
        colx = [-2.2, -1.1, 0.25, 2.1, 3.6]
        row_y = [1.2, 0.45, -0.3, -1.05, -1.8]
        hdr = VGroup(*[M(hh, 30).move_to([x, 2.05, 0]) for hh, x in zip(heads, colx)])
        hdr_desc = VGroup(*[T(s, 12, MUTED).next_to(hdr[i], UP, buff=0.06)
                            for i, s in enumerate(["confidence", "type", "axis dir.", "anchor", "order"])])
        slot_icons = VGroup(*[slot_shape(SLOT_LAV, s=0.55).move_to([-3.4, y, 0]) for y in row_y])
        slot_l = VGroup(*[M(f"s_{{{k + 1}}}", 22).next_to(slot_icons[k], LEFT, buff=0.12) for k in range(K)])
        cells = VGroup(*[VGroup(*[M(v, 24).move_to([x, y, 0]) for v, x in zip(r, colx)])
                         for r, y in zip(vals, row_y)])
        rows = VGroup(*[VGroup(slot_icons[k], slot_l[k], cells[k]) for k in range(K)])
        self.play(*[ReplacementTransform(qs[k], slot_icons[k]) for k in range(K)],
                  FadeOut(q_l), FadeIn(hdr), FadeIn(hdr_desc), FadeIn(slot_l), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(c, shift=0.2 * RIGHT) for c in cells], lag_ratio=0.12),
                  run_time=1.2)

        # confidence filtering
        thr = T("keep  c > μ", 20, weight=BOLD).move_to([-2.2, -2.75, 0])
        self.play(FadeIn(thr), Circumscribe(VGroup(*[c[0] for c in cells]), color=SEQ_GRN, buff=0.12),
                  run_time=1.0)
        self.play(*[rows[k].animate.set_opacity(0.12) for k in (1, 3, 4)], run_time=0.7)

        # sort by order score
        srt = T("sort by  o", 20, weight=BOLD).move_to([3.6, -2.75, 0])
        self.play(FadeIn(srt), Circumscribe(VGroup(cells[0][4], cells[2][4]), color=QUERY_PUR_D, buff=0.1),
                  run_time=0.9)
        self.play(FadeOut(VGroup(*[rows[k] for k in (1, 3, 4)])),
                  rows[0].animate.shift((row_y[0] - rows[0][0].get_y()) * UP),
                  rows[2].animate.shift((row_y[1] - rows[2][0].get_y()) * UP), run_time=0.8)
        n1 = T("1st", 18, REV_COL, weight=BOLD).next_to(rows[0], RIGHT, buff=0.35)
        n2 = T("2nd", 18, PRI_COL, weight=BOLD).next_to(rows[2], RIGHT, buff=0.35)
        n2.align_to(n1, LEFT)
        self.play(FadeIn(n1), FadeIn(n2), FadeOut(mem), FadeOut(mem_l), run_time=0.5)

        # render on the object
        obj = Dishwasher(show_hand=False, detail=0.85).place([-1.7, -1.55, 0], 0.78)
        obj.set_state(*demo_state(1.0))
        grp = VGroup(obj)
        rev = revolute_axis(obj)
        anc = Dot(obj.world((0, -obj.H / 2, 0)), radius=0.06, color=INK)
        pri = prismatic_axis(obj)
        pdot = Dot(pri.get_start(), radius=0.06, color=INK)
        self.play(FadeOut(thr), FadeOut(srt), FadeIn(grp), run_time=0.7)
        self.play(Create(rev), FadeIn(anc), Indicate(n1, color=REV_COL), run_time=0.7)
        self.play(GrowArrow(pri), FadeIn(pdot), Indicate(n2, color=PRI_COL), run_time=0.7)
        cap = T("an ordered articulation model,\nwith no joint count or category given", 18, MUTED,
                line_spacing=0.9)
        cap.move_to([3.4, -1.9, 0])
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(2.2)
        fade_all(self)


# ============================================================ 4. joint states
class JointStates(Scene):
    def construct(self):
        h = heading(4, "Joint state block: every joint, every frame")
        self.add(h)

        obj = Dishwasher().place([-4.9, -0.1, 0], 0.85)
        u = ValueTracker(0)
        obj.add_updater(lambda m: m.set_state(*demo_state(u.get_value())))

        # unit circle for the revolute slot
        circ = Circle(radius=0.95, color=LINE, stroke_width=2).move_to([-0.75, 0.75, 0])
        c_ax = VGroup(Line(circ.get_left(), circ.get_right(), color=LINE, stroke_width=1),
                      Line(circ.get_bottom(), circ.get_top(), color=LINE, stroke_width=1))

        def rev_pt():
            ph, _ = demo_state(u.get_value())
            return circ.get_center() + 0.95 * np.array([np.sin(ph), np.cos(ph), 0])
        pt = always_redraw(lambda: Dot(rev_pt(), radius=0.09, color=REV_COL))
        rad = always_redraw(lambda: Line(circ.get_center(), rev_pt(), color=REV_COL, stroke_width=3))
        rev_l = M("y_{t,k}=(\\sin\\theta,\\ \\cos\\theta,\\ 0)", 24, REV_COL).next_to(circ, DOWN, buff=0.18)
        rev_t = T("revolute slot", 16, REV_COL, weight=BOLD).next_to(circ, UP, buff=0.12)

        # slider for the prismatic slot
        track = Line([-1.7, -2.3, 0], [0.2, -2.3, 0], color=LINE, stroke_width=4)
        knob = always_redraw(lambda: Dot(track.point_from_proportion(demo_state(u.get_value())[1] / 1.15),
                                         radius=0.1, color=PRI_COL))
        pri_l = M("y_{t,k}=(0,\\ 0,\\ \\rho)", 24, PRI_COL).next_to(track, DOWN, buff=0.2)
        pri_t = T("prismatic slot", 16, PRI_COL, weight=BOLD).next_to(track, UP, buff=0.2)

        # time plots
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1.1, 0.5], x_length=4.0, y_length=3.6,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False,
                               "tip_length": 0.15, "tip_width": 0.12}).move_to([4.35, -0.1, 0])
        xl = M("t", 24, MUTED).next_to(ax.x_axis.get_end(), RIGHT, buff=0.1)
        yl = T("joint state (normalised)", 15, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.12)
        th = always_redraw(lambda: ax.plot(lambda x: demo_state(x)[0] / (PI / 2),
                                           x_range=[0, max(1e-3, u.get_value())], color=REV_COL,
                                           stroke_width=4))
        rh = always_redraw(lambda: ax.plot(lambda x: demo_state(x)[1] / 1.15,
                                           x_range=[0, max(1e-3, u.get_value())], color=PRI_COL,
                                           stroke_width=4))
        cur = always_redraw(lambda: DashedLine(ax.c2p(u.get_value(), 0), ax.c2p(u.get_value(), 1.1),
                                               color=INK, stroke_width=1.5))
        leg = VGroup(M("\\theta_t", 26, REV_COL), M("\\rho_t", 26, PRI_COL)).arrange(RIGHT, buff=0.5)
        leg.next_to(ax, UP, buff=0.15)

        self.play(FadeIn(obj), FadeIn(circ), FadeIn(c_ax), FadeIn(pt), FadeIn(rad), FadeIn(rev_l),
                  FadeIn(rev_t), FadeIn(track), FadeIn(knob), FadeIn(pri_l), FadeIn(pri_t),
                  Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(leg), run_time=1.0)
        self.add(th, rh, cur)
        self.play(u.animate.set_value(1), run_time=6.0, rate_func=linear)
        note = T("sin/cos avoids the 0°/360° wrap-around; output shape K × T × 3", 17, MUTED)
        note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note), run_time=0.5)
        self.wait(2.0)
        obj.clear_updaters()
        fade_all(self)


# ======================================================= 5. matching + losses
class Matching(Scene):
    def construct(self):
        h = heading(5, "Training: Hungarian matching + set loss")
        self.add(h)
        K = 5
        ys = np.linspace(1.6, -1.6, K)
        preds = VGroup(*[slot_shape(SLOT_LAV, s=0.6).move_to([-5.2, y, 0]) for y in ys])
        pl = VGroup(*[M(f"\\hat s_{{{k + 1}}}", 22).next_to(preds[k], LEFT, buff=0.12) for k in range(K)])
        pt = T("K predicted slots", 16, MUTED).next_to(preds, UP, buff=0.25)

        gy = [0.8, -0.8]
        gts = VGroup(
            VGroup(RoundedRectangle(width=1.9, height=0.6, corner_radius=0.1, fill_color=REV_COL,
                                    fill_opacity=0.12, stroke_color=REV_COL, stroke_width=2),
                   T("door · revolute", 15, REV_COL)),
            VGroup(RoundedRectangle(width=1.9, height=0.6, corner_radius=0.1, fill_color=PRI_COL,
                                    fill_opacity=0.12, stroke_color=PRI_COL, stroke_width=2),
                   T("rack · prismatic", 15, PRI_COL)),
        )
        for g, y in zip(gts, gy):
            g[1].move_to(g[0])
            g.move_to([-1.3, y, 0])
        gt_t = T("M ground-truth joints", 16, MUTED).next_to(gts, UP, buff=0.9)
        gt_t.align_to(pt, UP)
        self.play(LaggedStart(*[FadeIn(p) for p in preds], lag_ratio=0.08), FadeIn(pl), FadeIn(pt),
                  FadeIn(gts), FadeIn(gt_t), run_time=1.0)

        # cost matrix
        cost = np.array([[0.2, 3.1], [2.8, 2.6], [3.3, 0.3], [2.4, 2.9], [2.7, 2.2]])
        cells = VGroup()
        for i in range(K):
            for j in range(2):
                v = cost[i, j]
                sq = Square(0.62, stroke_color=LINE, stroke_width=1.5,
                            fill_color=interpolate_color(ManimColor(HUNG_PEACH), ManimColor("#FFFFFF"),
                                                         min(1, v / 3.3)), fill_opacity=1)
                sq.move_to([2.3 + j * 0.62, 1.24 - i * 0.62, 0])
                cells.add(VGroup(sq, M(f"{v:.1f}", 20).move_to(sq)))
        c_t = T("matching cost", 16, MUTED).next_to(cells, UP, buff=0.3)
        c_sub = T("axis + anchor + type", 13, MUTED).next_to(c_t, DOWN, buff=0.05)
        c_t.shift(0.15 * UP)
        self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.04), FadeIn(c_t), FadeIn(c_sub),
                  run_time=1.2)
        best = [(0, 0), (2, 1)]
        hls = VGroup(*[SurroundingRectangle(cells[i * 2 + j], color=INK, buff=0.02, stroke_width=3.5)
                       for i, j in best])
        self.play(Create(hls), run_time=0.7)

        links = VGroup(*[Line(preds[i].get_right(), gts[j].get_left(), color=[REV_COL, PRI_COL][j],
                              stroke_width=4) for i, j in best])
        self.play(Create(links), run_time=0.8)
        nulls = VGroup(*[VGroup(M("\\varnothing", 24, MUTED), T("c → 0", 14, MUTED)).arrange(RIGHT, buff=0.1)
                         .next_to(preds[i], RIGHT, buff=0.35) for i in (1, 3, 4)])
        self.play(FadeIn(nulls), *[preds[i].animate.set_opacity(0.3) for i in (1, 3, 4)], run_time=0.7)

        # loss
        loss = M("\\mathcal L = \\lambda_{\\mathrm{conf}}\\mathcal L_{\\mathrm{conf}} + \\lambda_{\\mathrm{type}}\\mathcal L_{\\mathrm{type}}"
                 "+ \\lambda_{\\mathrm{axis}}\\mathcal L_{\\mathrm{axis}} + \\lambda_{\\mathrm{point}}\\mathcal L_{\\mathrm{point}}"
                 "+ \\lambda_{\\mathrm{order}}\\mathcal L_{\\mathrm{L1}} + \\lambda_{\\mathrm{rank}}\\mathcal L_{\\mathrm{rank}}"
                 "+ \\lambda_{\\mathrm{state}}\\mathcal L_{\\mathrm{state}}", 26)
        loss.move_to([0, -2.75, 0])
        if loss.width > 13.2:
            loss.scale_to_fit_width(13.2)
        self.play(Write(loss), run_time=2.0)
        rank = M("\\text{rank: }\\ \\hat o_i + m \\le \\hat o_j \\ \\text{ for } i \\prec j", 24, MUTED)
        rank.next_to(loss, DOWN, buff=0.3)
        self.play(FadeIn(rank), run_time=0.6)
        self.wait(2.2)
        fade_all(self)
