"""Overview animation of the full PokeNet pipeline (top of the Method section)."""
from common import *

NF = 4  # frames shown in the filmstrip
YS = np.linspace(1.75, -2.35, NF)


def vbar(x, fill, label, w=0.8, h=4.9, y=-0.3, size=21):
    return block(w, h, fill, label, size, vertical=True).move_to([x, y, 0])


def harrows(x0, x1, sw=4, tip=0.14):
    return VGroup(*[flow([x0, y, 0], [x1, y, 0], sw=sw, tip=tip, buff=0.02)
                    for i, y in enumerate(YS) if i != 2])


class Overview(Scene):
    def construct(self):
        title = T("PokeNet", 34, weight=BOLD).to_corner(UL, buff=0.35)
        sub = T("one human demonstration  →  ordered articulation model", 20, MUTED)
        sub.next_to(title, RIGHT, buff=0.35).align_to(title, DOWN).shift(0.03 * UP)
        self.add(title, sub)

        # ------------------------------------------------------ 0. the demo
        live = Dishwasher().place([-0.3, -0.1, 0], 1.25)
        u = ValueTracker(0)
        live.add_updater(lambda m: m.set_state(*demo_state(u.get_value())))
        cap = T("A person opens the door, then pulls out the (initially hidden) rack",
                22, MUTED).move_to([0, -2.6, 0])
        self.play(FadeIn(live), FadeIn(cap), run_time=0.6)
        self.play(u.animate.set_value(1), run_time=3.4, rate_func=linear)
        live.clear_updaters()
        self.play(FadeOut(live), FadeOut(cap), run_time=0.4)

        # ---------------------------------------------------- 1. filmstrip
        film_bg = RoundedRectangle(width=2.0, height=5.3, corner_radius=0.15,
                                   fill_color="#F3F5F6", fill_opacity=1,
                                   stroke_color=LINE, stroke_width=1.5).move_to([-6.05, -0.3, 0])
        film_lbl = T("Point cloud video", 16, MUTED).next_to(film_bg, UP, buff=0.1)
        frames = VGroup()
        for i, y in enumerate(YS):
            d = Dishwasher(detail=0.55, dot_r=0.03).place([-6.2, y, 0], 0.34)
            d.set_state(*demo_state(i / (NF - 1)))
            frames.add(d)
        frames[2].set_opacity(0)
        tl = VGroup(*[M(s, 24, MUTED).move_to([-5.35, y, 0])
                      for s, y in zip(["P_1", "P_2", "\\vdots", "P_T"], YS)])
        self.play(FadeIn(film_bg), FadeIn(film_lbl),
                  LaggedStart(*[FadeIn(f, shift=0.2 * DOWN) for f in frames], lag_ratio=0.2),
                  FadeIn(tl), run_time=1.3)

        # ---------------------------------------------- 2. spatial encoding
        pn = vbar(-4.45, PN_PINK, "PointNet++", w=0.7, size=19)
        a1 = harrows(-5.05, -4.82)
        feats = VGroup(*[token_col(4, LOCAL_OR, LOCAL_OR_L, 0.1, 0.36, 0.03).move_to([-3.55, y, 0])
                         for y in YS])
        feats[2].become(M("\\vdots", 26, LOCAL_OR).move_to([-3.55, YS[2], 0]))
        a2 = harrows(-4.08, -3.83)
        self.play(FadeIn(pn), LaggedStart(*[GrowArrow(a) for a in a1], lag_ratio=0.1), run_time=0.7)
        self.play(LaggedStart(*[GrowArrow(a) for a in a2], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(f, shift=0.15 * RIGHT) for f in feats], lag_ratio=0.12),
                  run_time=0.8)
        feat_lbl = T("local features", 13, MUTED).next_to(feats[0], UP, buff=0.12)

        spat = vbar(-2.35, ENC_YEL, "Spatial Encoder")
        cls = block(0.75, 0.42, CLS_GRAY, "CLS", 14, dashed=False).move_to([-3.55, -3.15, 0])
        a3 = harrows(-3.25, -2.77)
        a_cls = flow(cls.get_right(), [-2.77, -3.15, 0], sw=4, tip=0.14, buff=0.02)
        spat.stretch_to_fit_height(5.3).move_to([-2.35, -0.55, 0])
        self.play(FadeIn(spat), FadeIn(cls), FadeIn(feat_lbl), run_time=0.6)
        self.play(LaggedStart(*[GrowArrow(a) for a in a3], lag_ratio=0.1), GrowArrow(a_cls),
                  run_time=0.6)

        # frame-level tokens ĉ_t travel into the temporal encoder
        temp = vbar(-0.45, ENC_YEL, "Temporal Encoder")
        a4 = harrows(-1.93, -0.87)
        ctok = VGroup(*[token(SEQ_GRN_L, 0.16, 0.42, stroke=SEQ_GRN).move_to([-1.62, y, 0])
                        for y in YS])
        ctok[2].set_opacity(0)
        c_lbl = M("\\hat c_t", 24).next_to(a4[0], UP, buff=0.08)
        self.play(FadeIn(temp), LaggedStart(*[GrowArrow(a) for a in a4], lag_ratio=0.1),
                  LaggedStart(*[GrowFromCenter(c) for c in ctok], lag_ratio=0.1),
                  FadeIn(c_lbl), run_time=0.9)
        self.play(*[ctok[i].animate.move_to([-0.45, YS[i], 0]) for i in range(NF)], run_time=0.6)
        arcs = VGroup()
        idx = [0, 1, 3]
        for a in idx:
            for b in idx:
                if a < b:
                    arcs.add(ArcBetweenPoints(ctok[a].get_right(), ctok[b].get_right(),
                                              angle=-PI / 2.2, color=SEQ_GRN, stroke_width=2.5))
        att = T("attention across time", 13, SEQ_GRN).next_to(temp, DOWN, buff=0.12)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.2), FadeIn(att), run_time=1.0)
        self.play(FadeOut(arcs), FadeOut(ctok), FadeOut(att), run_time=0.3)

        # memory / sequence encodings
        mem_box = block(1.3, 1.45, "#FFFFFF", None, stroke=SEQ_GRN).move_to([1.2, 0.55, 0])
        mem = token_col(4, SEQ_GRN, SEQ_GRN_L, 0.17, 0.85, 0.07).move_to(mem_box).shift(0.1 * UP)
        mem_lbl = T("Seq. encodings", 14).next_to(mem_box, DOWN, buff=0.08)
        a_mem = flow([-0.03, 0.55, 0], mem_box.get_left(), sw=5, buff=0.02)
        self.play(GrowArrow(a_mem), FadeIn(mem_box),
                  LaggedStart(*[GrowFromEdge(m, DOWN) for m in mem], lag_ratio=0.15),
                  FadeIn(mem_lbl), run_time=0.9)

        # ---------------------------------------------- 3. joint set decoder
        qbox = block(1.3, 1.2, QUERY_PUR, None).move_to([1.2, -1.9, 0])
        K = 4
        queries = VGroup(*[slot_shape(QUERY_PUR_D, s=0.5) for _ in range(K)]).arrange(RIGHT, buff=0.05)
        queries.move_to(qbox).shift(0.12 * UP)
        q_lbl = T("K joint queries", 13).next_to(qbox, DOWN, buff=0.08)
        self.play(FadeIn(qbox), LaggedStart(*[FadeIn(q, shift=0.1 * UP) for q in queries],
                                            lag_ratio=0.1), FadeIn(q_lbl), run_time=0.8)

        dec = block(1.9, 1.7, DEC_YEL, None).move_to([3.25, -0.7, 0])
        dec_lbl = T("Joint Set Decoder", 15, weight=MEDIUM).move_to(dec).shift(0.58 * DOWN)
        layers = VGroup(*[RoundedRectangle(width=0.26, height=0.8, corner_radius=0.08,
                                           fill_color="#F2F2F2", fill_opacity=1,
                                           stroke_color=INK, stroke_width=1.5) for _ in range(3)])
        layers.arrange(RIGHT, buff=0.28).move_to(dec).shift(0.18 * UP)
        a_m = flow(mem_box.get_right(), [dec.get_left()[0], -0.25, 0], sw=5, buff=0.05)
        a_q = flow(qbox.get_right(), [dec.get_left()[0], -1.2, 0], sw=5, buff=0.05)
        self.play(FadeIn(dec), FadeIn(layers), FadeIn(dec_lbl), GrowArrow(a_m), GrowArrow(a_q),
                  run_time=0.7)
        qs = queries.copy()
        self.play(qs.animate.move_to(layers).scale(0.9), run_time=0.7)
        xattn = VGroup(*[Line(q.get_center(), m.get_top(), color=SEQ_GRN, stroke_width=1.5,
                              stroke_opacity=0.6) for q in qs for m in mem])
        self.play(Create(xattn), run_time=0.6)
        self.play(FadeOut(xattn), Indicate(layers, color=DEC_YEL, scale_factor=1.05), run_time=0.6)

        slots = VGroup(*[slot_shape(SLOT_LAV, s=0.55) for _ in range(K)]).arrange(RIGHT, buff=0.2)
        slots.move_to([5.55, -2.05, 0])
        confs = [0.92, 0.08, 0.86, 0.11]
        bars = VGroup()
        for s, c in zip(slots, confs):
            bg = Rectangle(width=0.13, height=0.75, stroke_color=LINE, stroke_width=1.2)
            bg.next_to(s, UP, buff=0.1)
            fg = Rectangle(width=0.13, height=0.75 * c,
                           fill_color=SEQ_GRN if c > 0.5 else STATE_RED_D,
                           fill_opacity=1, stroke_width=0)
            fg.move_to(bg.get_bottom(), aligned_edge=DOWN)
            bars.add(VGroup(bg, fg))
        base = bars[0][0].get_bottom()[1]
        thr = DashedLine([4.6, base + 0.37, 0], [6.5, base + 0.37, 0], color=INK, stroke_width=1.5)
        thr_lbl = M("\\mu", 22).next_to(thr, RIGHT, buff=0.06)
        slot_lbl = T("refined joint slots", 13).next_to(slots, DOWN, buff=0.1)
        a_out = flow(dec.get_right() + 0.35 * DOWN, [4.55, -1.6, 0], sw=5, buff=0.05)
        self.play(ReplacementTransform(qs, slots), GrowArrow(a_out), FadeIn(slot_lbl), run_time=0.8)
        conf_lbl = T("confidence c", 13, MUTED).next_to(bars, UP, buff=0.06)
        self.play(FadeIn(VGroup(*[b[0] for b in bars])),
                  LaggedStart(*[GrowFromEdge(b[1], DOWN) for b in bars], lag_ratio=0.1),
                  FadeIn(conf_lbl), run_time=0.8)
        self.play(Create(thr), FadeIn(thr_lbl), run_time=0.4)
        self.play(*[VGroup(slots[i], bars[i]).animate.set_opacity(0.15) for i in (1, 3)],
                  run_time=0.6)

        # ---------------------------------------------- 4. joint state block
        jsb = block(1.9, 1.2, STATE_RED, None).move_to([3.25, 2.05, 0])
        jsb_lbl = T("Joint State Block", 15, weight=MEDIUM).move_to(jsb).shift(0.36 * DOWN)
        jl = VGroup(*[RoundedRectangle(width=0.2, height=0.5, corner_radius=0.06,
                                       fill_color="#F2F2F2", fill_opacity=1, stroke_color=INK,
                                       stroke_width=1.5) for _ in range(3)])
        jl.arrange(RIGHT, buff=0.28).move_to(jsb).shift(0.15 * UP)
        a_js = flow(mem_box.get_top(), jsb.get_left() + 0.2 * DOWN, sw=5, buff=0.05)
        self.play(GrowArrow(a_js), FadeIn(jsb), FadeIn(jl), FadeIn(jsb_lbl), run_time=0.7)

        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=1.7, y_length=1.2,
                  axis_config={"color": MUTED, "stroke_width": 1.5, "include_ticks": False,
                               "tip_length": 0.12, "tip_width": 0.1})
        ax.move_to([5.65, 2.05, 0])
        th = ax.plot(lambda x: smooth(np.clip(x / 0.5, 0, 1)), color=REV_COL, stroke_width=3)
        rh = ax.plot(lambda x: smooth(np.clip((x - 0.5) / 0.5, 0, 1)), color=PRI_COL, stroke_width=3)
        th_l = M("\\theta_t", 20, REV_COL).next_to(ax, UP, buff=0.02).shift(0.4 * LEFT)
        rh_l = M("\\rho_t", 20, PRI_COL).next_to(th_l, RIGHT, buff=0.35)
        t_l = M("t", 18, MUTED).next_to(ax.x_axis.get_end(), RIGHT, buff=0.06)
        st_lbl = T("joint states per time step", 13, MUTED).next_to(ax, DOWN, buff=0.12)
        a_st = flow(jsb.get_right(), ax.get_left() + 0.05 * LEFT, sw=5, buff=0.05)
        self.play(GrowArrow(a_st), Create(ax), FadeIn(t_l), FadeIn(st_lbl), run_time=0.5)
        self.play(Create(th), Create(rh), FadeIn(th_l), FadeIn(rh_l), run_time=1.2)

        # ------------------------------------------ 5. ordered articulation model
        keep = VGroup(slots[0], slots[2])
        out = VGroup(
            VGroup(T("1", 18, REV_COL, weight=BOLD), T("revolute · door", 16, REV_COL)).arrange(RIGHT, buff=0.15),
            VGroup(T("2", 18, PRI_COL, weight=BOLD), T("prismatic · rack", 16, PRI_COL)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        out_box = SurroundingRectangle(out, buff=0.15, corner_radius=0.1, color=INK, stroke_width=1.5)
        outg = VGroup(out_box, out).move_to([5.55, 0.25, 0])
        out_lbl = T("valid joints, sorted by order o", 13, MUTED).next_to(out_box, UP, buff=0.08)
        self.play(TransformFromCopy(keep, out), Create(out_box), FadeIn(out_lbl), run_time=0.9)

        # recovered axes drawn onto the observed object
        last = frames[-1]
        rev = revolute_axis(last, sw=3.5)
        pri = prismatic_axis(last, sw=3.5, tip=0.1)
        self.play(Create(rev), GrowArrow(pri), run_time=0.8)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (title, sub)], run_time=0.8)
