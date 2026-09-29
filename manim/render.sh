#!/bin/bash
# Render all method animations (1080p30) and export web-ready mp4 + poster to static/videos/method/
# Usage: bash manim/render.sh   (from repo root or manim/)
set -e
cd "$(dirname "$0")"
E=$HOME/miniconda3/envs/website/bin; export PATH="$E:$PATH"
OUT=../static/videos/method; mkdir -p "$OUT"
render() {  # file scene outname
  manim -qh --disable_caching "$1" "$2" 2>&1 | grep -E "Error|Played" || true
  src=media/videos/${1%.py}/1080p30/$2.mp4
  ffmpeg -loglevel error -y -i "$src" -c:v libx264 -pix_fmt yuv420p -crf 26 -preset slow \
         -vf "scale=1600:-2" -movflags +faststart -an "$OUT/$3.mp4"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src")
  ffmpeg -loglevel error -y -ss "$(python3 -c "print($d-1.3)")" -i "$src" -frames:v 1 \
         -vf "scale=1280:-2" -q:v 4 "$OUT/$3.jpg"
  echo "done $3 ($(du -h "$OUT/$3.mp4" | cut -f1))"
}
render overview.py Overview overview
render stages.py SpatialEncoding spatial
render stages.py TemporalEncoding temporal
render stages.py JointSetDecoder decoder
render stages.py JointStates states
render stages.py Matching matching
