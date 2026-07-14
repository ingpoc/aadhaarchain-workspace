# Evidence template (per ask)

```markdown
### <ID> — <ask>
- **Result:** Pass | Fail | Skip
- **Screenshot path:** references/evidence/<id>-<ts>.jpeg (required for Pass)
- **Screenshot shows:** (what the agent saw when Reading the image)
- **URL before → after:**
- **Tools (`__samanthaTools`):**
- **AG outcome:** allow | need_approval | deny | n/a
- **Background:** none | handoff | completion | FAIL /agent
- **Watched:** yes
```

## Hard doctrine

**Claim → screenshot → Read image → only then Pass.**

No screenshot path / unread image = cannot Pass. Orb text alone = Fail.
