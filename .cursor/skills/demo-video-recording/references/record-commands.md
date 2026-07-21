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

## Generate OpenAI narration (Mode B)

For a bounded narration file, use the OpenAI Speech API rather than opening a
Realtime session. Realtime remains the product voice runtime demonstrated by
Samantha. Keep the API key out of scripts and evidence.

```bash
curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @voice-request.json \
  --output vo.mp3
```

`voice-request.json` is a temporary local file containing the approved script:

```json
{
  "model": "gpt-4o-mini-tts",
  "voice": "coral",
  "input": "Approved narration text",
  "instructions": "Calm, precise Indian English; confident but not promotional; approximately 135 words per minute. Pause briefly between paragraphs. Do not add or paraphrase words."
}
```

Delete the temporary request file after generation if it is not part of the
approved evidence set. Clearly disclose that the narration is AI-generated.

## Mux narration / VO

```bash
ffmpeg -y -i take.mp4 -i vo.mp3 -c:v copy -c:a aac -shortest \
  .cursor/skills/<owner>/references/evidence/<demo-id>/demo-final.mp4
```

If the durations differ by more than five percent, revise the narration or redo
the take. Do not conceal a timing problem with aggressive time stretching.

## During take

1. Focus Chrome on the recorded display with `@Computer` if needed.
2. Replay the **same** Chrome-plugin journey as the dry-run.
3. Do not improvise `evaluate` clicks.  
4. Spot-check: extract mid frames and **Read** images for pointer + outcome.

## After

Upload unlisted Loom/YouTube → paste URL into form / curated answers. Keep local MP4 under evidence; avoid committing huge blobs unless required.
