# PokeNet project page

Website for **PokeNet: Learning Kinematic Models of Articulated Objects from Human Observations** (ICRA 2026).

- Live site: https://sequential-joints.github.io
- Paper: https://arxiv.org/abs/2602.02741
- Code: https://github.com/gupta-anmol99/Object-Kinematic-Modeling

## Layout

- `index.html`: the page
- `static/css/site.css`: styles
- `static/js/results.js`: results charts (data from Tables II and III of the paper)
- `static/videos/method/`: method animations (rendered from `manim/`)
- `manim/`: Manim scenes for the method animations

## Re-rendering the animations

Requires the `website` conda env (`conda create -n website -c conda-forge python=3.11 manim ffmpeg`).

```bash
bash manim/render.sh
```

This renders every scene at 1080p and writes web-ready `.mp4` files and poster images to `static/videos/method/`.

## Preview locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

Website template adapted from [Nerfies](https://github.com/nerfies/nerfies.github.io) (CC BY-SA 4.0).
