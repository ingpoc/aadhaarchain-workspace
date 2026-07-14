# Record commands (sketch)

Use only after dry-run matrix Pass. Adjust screen index after listing devices.

## List capture devices (macOS)

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

Comet on DELL is often a different screen index than LG (IDE). Confirm visually.

## Screen-only capture (silent UI; mux VO later)

```bash
# Replace N with Comet's screen index; out path under evidence/
ffmpeg -y -f avfoundation -capture_cursor 1 -i "N:none" \
  -r 30 -c:v libx264 -pix_fmt yuv420p \
  .cursor/skills/<owner>/references/evidence/<demo-id>/take.mp4
```

## Mux TTS / VO

```bash
ffmpeg -y -i take.mp4 -i vo.wav -c:v copy -c:a aac -shortest \
  .cursor/skills/<owner>/references/evidence/<demo-id>/demo-final.mp4
```

## macOS TTS VO (optional Mode B)

```bash
say -o vo.aiff "…"   # or pipe script lines
# convert to wav if needed for mux
```

## During take

1. Focus Comet on the recorded display (`macos-cua` if needed).  
2. Replay the **same** Hermes cursor script as dry-run.  
3. Do not improvise `evaluate` clicks.  
4. Spot-check: extract mid frames and **Read** images for pointer + outcome.

## After

Upload unlisted Loom/YouTube → paste URL into form / curated answers. Keep local MP4 under evidence; avoid committing huge blobs unless required.
