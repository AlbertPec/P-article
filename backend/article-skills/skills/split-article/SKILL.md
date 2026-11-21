---
name: split-article
description: Splits a parsed article into numbered parts. Called by the pipeline as /article:split-article <input> <output folder>.
disable-model-invocation: true
---

# Split an article into parts (mock)

Mock: replace with the real skill. For now it cuts the article at its numbered top-level sections without changing any text, so the pipeline can be tested end to end.

Arguments: `$ARGUMENTS`

The first argument is the Markdown file to split and the second is the folder to write the parts to. Both paths are relative to the current folder.

1. Find the lines to cut before. Use Grep on the input file with line numbers shown, output mode `content`, and the pattern `^#+\s*[*_]*\d+\.\s`. It matches numbered top-level section headings such as `### **1. Introduction**`, but not sub-sections such as `2.1.`. If it finds nothing, use the pattern `^## ` instead.
2. Work out each part's line range from those line numbers:
   - Part 1 runs from line 1 to the line before the first cut.
   - Each later part runs from its cut line to the line before the next cut.
   - The last part runs to the end of the file.
3. For each part in order, Read exactly its lines with `offset` and `limit`. Write them to `<output folder>/part_<number>.md`: `part_1.md`, `part_2.md`, and so on.
4. Copy the text exactly, without the line numbers that Read shows. Don't edit, summarize, reorder or drop anything, and keep image links such as `![...](images/...)` exactly as they are.
5. Reply with one line: how many parts you wrote.
