---
name: rewrite-part
description: Rewrites one part of an article. Called by the pipeline as /article:rewrite-part <input> <output>.
disable-model-invocation: true
---

# Rewrite one part (mock)

Mock: replace with the real skill. For now it copies the part unchanged, so the pipeline can be tested end to end.

Arguments: `$ARGUMENTS`

The first argument is the part to read and the second is the file to write. Both paths are relative to the current folder.

1. Read the input file.
2. Write its contents to the output file exactly as they are. Don't change, add or remove anything.
3. Reply with one line: the output path.
