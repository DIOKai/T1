---
name: correction-memory
description: Remember the user's corrections so the same mistake never needs pointing out twice. Use whenever the user says something was wrong or tells you how they want it done next time — "不对", "错了", "不是这样", "我说过了", "又来了", "下次…", "以后…", "记住…", "别再…", "you got this wrong", "remember that" — and whenever you notice you repeated a mistake listed in LESSONS.md. Fixes the problem first, then writes one short lesson into LESSONS.md (loaded into every session through CLAUDE.md) and commits it.
---

# Correction memory

Every session starts from zero; the only thing that carries over is what's in the repository. `LESSONS.md` at the repo root is imported by `CLAUDE.md`, so whatever is written there is in context at the start of every future session. This skill keeps that file accurate, short and useful.

## When the user corrects you

1. **Fix the actual problem first.** The user wants the thing done right; the lesson comes second.
2. **Work out the general rule.** Not "the commit on Tuesday had no PR" but "after finishing a batch of work, open a PR to main and merge it". Ask yourself: in what future situation should this change what I do? If the correction only applies to this one task (a typo in a name, a one-off preference for this file), don't record it.
3. **Check `LESSONS.md` for an existing entry** on the same topic. Update or sharpen it instead of adding a near-duplicate. If the new correction contradicts an old lesson, the newer one wins — replace the old one.
4. **Write the lesson** under the matching section, in Chinese, in this shape:

   ```markdown
   - **规则**（一句话，用祈使句）。原因：用户怎么说的 / 为什么重要。（YYYY-MM-DD）
   ```

   Keep it to one or two lines. Concrete beats vague: name the tool, file, command or wording.
5. **Tell the user in one line** what you recorded, e.g. `已记下：做完一批工作后直接开 PR 合并到 main。`
6. **Which `LESSONS.md`**: inside the T1 repo, the one at its root. In a local session in another folder (your FiveM server, a Blender project), use the T1 path written in the `T1:begin` block of `~/.claude/CLAUDE.md` (set up by `scripts/install_local.py`) and commit there with `git -C "<T1 path>"`. Locally the change takes effect in the next session straight away, because `~/.claude/CLAUDE.md` imports the local T1 copy.
7. **Commit it** with whatever you're working on (or on its own: `Lessons: <short rule>`), and push. A new cloud session clones `main`, so in the cloud the lesson only takes effect after the branch is merged — it rides along with the next PR the user asks you to open and merge. If the session is ending with the lesson unmerged, say so in your final message.

## Also record

- Explicit "记住 X" / "以后都 X" instructions, even if nothing went wrong.
- A mistake you catch yourself repeating that the user had corrected before (sharpen that lesson — it wasn't clear enough).

## Don't record

- Things already stated in `CLAUDE.md` (point to them instead — or, if you broke a CLAUDE.md rule, sharpen the wording in CLAUDE.md rather than duplicating it).
- Secrets, passwords, tokens, personal data.
- One-off details of a single task, or your own guesses about what the user might want.

## Housekeeping

- Keep `LESSONS.md` under ~60 lessons; it is read every session and costs tokens. When it grows, merge overlapping lessons and move stable, important ones into `CLAUDE.md`'s rules.
- Never delete a lesson just because it's inconvenient; delete it only if the user reverses it.
- When starting a task, scan the relevant section of `LESSONS.md` (it is already in context) and follow it without being told.
