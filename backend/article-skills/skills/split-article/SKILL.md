---
name: split-article
description: Plans how to split a parsed scientific article into parts of 4-5 minutes of reading, each ending on a finished thought, drops journal headers, logos and other page furniture, extracts the abstract, and records the article's metadata. Called by the pipeline as /article:split-article <article> <outline> <plan file> <metadata file> <abstract file>.
disable-model-invocation: true
---

# Plan the parts of an article

The app shows an article as a series of parts, each taking 4 to 5 minutes to read. Your job is to decide:

- where each part starts and ends
- which blocks are page furniture to delete, such as journal headers and logos
- the article's metadata

You also extract the abstract into its own file.

You don't write the parts yourself: you write a plan, and the pipeline cuts the article along it exactly, so the text and every graphic you keep stay exactly as they are.

Arguments: `$ARGUMENTS`

1. **The article:** Markdown made from a PDF.
2. **The outline:** the article split into numbered blocks (`B1`, `B2`, …).
3. **The plan file** to write.
4. **The metadata file** to write.
5. **The abstract file** to write.

All paths are relative to the current folder.

## The outline

Each block is a paragraph, a heading, a graphic, or a `pic-text` block. A `pic-text` block is the parser's text version of the graphic right before it, usually an equation.

Each outline row gives:
- the block's lines in the article, its kind, words and graphics
- its reading time in seconds
- the running reading time from the start of the article to the end of the block
- a preview. For a graphic, the preview also shows the image's size in pixels.

The reading time is already calculated. Use those numbers, and don't count words yourself.

A part is a run of whole blocks. You can only cut between blocks, and you can only delete whole blocks.

## Steps

1. Read the whole outline.
2. Read the whole article. If it's long, read it in chunks with `offset` and `limit` until you've seen every line. You need the actual text to judge where a thought ends; the previews aren't enough.
3. Find the abstract (see "The abstract file" below). If it's a graphic, open it with Read.
4. Decide which blocks to delete (rule 1). The abstract's blocks are among them. Open with Read any graphic whose purpose isn't clear from the text around it.
5. Find where the back matter starts (rule 5).
6. Choose the parts, following rules 2 to 4.
7. Check everything against the checklist at the end.
8. Write the abstract file.
9. Write the metadata file.
10. Write the plan file.
11. Reply with one line: how many parts, their reading times, and how many blocks you deleted.

## Rules, most important first

### 1. Delete what isn't part of the article itself

The PDF's pages carry things that belong to the journal or the page layout, not to the article. Delete them by listing them in `drop`:

- **The journal masthead:** journal name and cover, publisher logos, "Contents lists available at …", the journal homepage, volume and page numbers.
- **Badges and decorations:** "Check for updates" (CrossMark), open-access icons, publisher logos, divider lines.
- **Running headers and footers** repeated on each page, such as `_W. Du et al._`, the journal name with a volume and page, and page numbers.
- **Publishing boilerplate:** DOI lines; received, revised, accepted and available-online dates; copyright and licence lines; "All rights reserved".
- **Contact details:** corresponding-author footnote markers and e-mail addresses.
- **Author names and affiliations:** these go into the metadata file instead (see below), so delete their blocks from the text.
- **The abstract and keywords:** these go into the abstract file instead (see below), so delete their blocks from the text, with the reason `abstract, in the abstract file`. Delete the "Abstract" and "Keywords" headings too.

Keep everything that is the article's content:
- the title
- section text, headings, figures, tables and equations
- captions and `pic-text` blocks
- footnotes that explain the content

**Open a graphic before deleting it.** The parser sometimes saves a whole text box as an image. In one article, the "Table 1" graphic on the first page was really the abstract and keywords, and the abstract's text appeared nowhere else. Small images on the first page, roughly under 200 px on each side, are usually logos, journal covers or badges. But read any graphic whose role you aren't sure of, and keep it if it carries content. When in doubt, keep it. The abstract is the one content graphic you delete, because its text goes into the abstract file.

Deleting a block doesn't move anything else. The rest of the part stays exactly as it is.

### 2. Every part ends on a finished thought

A part must end where a reader can stop: the end of a section, the end of an argument, a result that has just been explained, or a paragraph that wraps something up. It must never end:

- in the middle of a sentence
- between a statement and its explanation, or between a claim and its evidence
- after a sentence ending with `:`, before the list or equation it introduces
- between a graphic and the text that explains it, or between a graphic and its caption or `pic-text` block
- on a heading, because a heading always belongs with the text after it

Boundaries have different strengths. From strongest to weakest:
1. just before a section heading (`2.`, `3.`)
2. just before a subsection heading (`2.2.`, `2.2.1.`)
3. between paragraphs where the topic clearly changes, such as moving from one route or one result to the next

**Never cut inside a derivation:** a chain of equations and the text that builds one step on the previous, such as "is calculated using…", "substituting… gives…" or "where X is…", followed by the next formula. The steps of one calculation belong in one part.

**Choose the strongest boundary within the allowed length (rule 3), not the one closest to the target.** A subsection heading at 3:40 beats a paragraph break at 4:20. Use a weaker boundary only when no stronger one falls within roughly 3:30 to 6:00.

**Watch for page furniture in the middle of the text.** Running headers and footers sit where the PDF page ended, often in the middle of a sentence. The sentence continues in the next text block, usually starting in lowercase. You delete the furniture, but the two halves of the sentence still belong to the same part. Never cut between them.

### 3. Each part takes 4 to 5 minutes

Add up the seconds of the blocks a part keeps; deleted blocks don't count. The running time column helps: a part's length is the running time at its last block minus the running time at the block before its first, minus the blocks you delete in it.

Finishing a thought matters more than equal length. A part that ends at 3:40 on a finished section is better than one that reaches 4:00 by cutting the next thought in half. In the same way, 5:30 is better than splitting an argument. Stay within roughly 3:30 to 6:00. Go outside that only when the alternative breaks rule 2, and only as far as needed. A short section is a reason to join it with its neighbour, not to make a short part.

Don't make parts equal for the sake of it. Avoid tiny leftover parts, though: if the last stretch of a section is very short, give it to the part before or after it, wherever it fits the thought.

### 4. Graphics stay with the text about them

Graphics are images in the article: figures, tables and equations. Keep every graphic in the same part as the text that introduces it or discusses it ("Fig. 3", "Table 2", "Eq. (5)", or the sentence just before it). Keep its caption and its `pic-text` block with it as well.

Prefer cuts where a part neither starts nor ends with a graphic, so that some text comes before the first graphic and after the last one. A heading followed directly by a graphic counts as starting with a graphic. This is a preference: rule 2 still wins.

You don't have to copy or describe graphics. Because the pipeline cuts the article as it is, every graphic you keep stays exactly as in the original, in the part where it appears.

### 5. Front matter and back matter

**Front matter:** after deleting the masthead, authors, boilerplate and abstract, only the title is left. It stays at the start of part 1, followed by the introduction. Part 1 then runs until a point that satisfies rule 2.

**Back matter** is everything after the last section of the article itself: author contribution statements (CRediT), declarations of competing interest, acknowledgements, funding, data availability and the reference list. It isn't reading material, so it isn't split into parts. Set `back_matter_first_block` to its first block; the pipeline saves it separately. Don't list back-matter blocks in `drop`. Appendices that explain the work are content, not back matter. If the article has no back matter, use `null`.

## The metadata file

Write JSON in exactly this shape:

```json
{
  "title": "Estimation of ship routes considering weather and constraints",
  "authors": ["Wei Du", "Yanjun Li"],
  "affiliations": ["College of Power and Energy Engineering, Harbin Engineering University, Harbin, 150001, Heilongjiang, China"],
  "topic": "Choosing fuel-efficient ship routes under weather and engine-power constraints"
}
```

- **`title`:** the article's title, word for word as the article gives it, as plain text. Leave out Markdown (`#`, `**`), HTML, footnote markers and a final period. Keep its capitalization. If the title runs over several lines, join them with single spaces. The title also stays as the heading at the start of part 1.
- **`authors`:** every author's full name, in the article's order, as written in the article. Leave out superscripts, footnote markers (`a`, `*`, `**`) and HTML such as `<sup>`.
- **`affiliations`:** every distinct affiliation, in the order they first appear, written out in full, without the letter or number marker.
- **`topic`:** one short plain-English phrase, about 5 to 15 words, saying what the article is about. Write it for a general reader rather than copying the title.

Take authors and affiliations only from the article. If the article doesn't give affiliations, use an empty list.

## The abstract file

Later stages read this file as context about the whole article while they work on one part. Write the abstract as plain Markdown:

```markdown
Taking a T300k VLCC oil tanker as the research object, the ship route estimation model …

**Keywords:** Weather conditions; Constraints; Ship speed loss; Route estimation
```

- **Copy the abstract word for word.** Don't summarize, shorten, correct or rewrite it. Keep its paragraphs.
- **If the abstract is an image,** open it with Read and transcribe it exactly. Write subscripts and superscripts as plain text or Unicode (`CO2` or `CO₂`). Leave out the box's labels, such as "ARTICLE INFO" and "ABSTRACT".
- **Leave out headings.** Don't add an "Abstract" heading or any other heading.
- **If the article lists keywords,** add them on a last line, as shown above, separated by semicolons. If it doesn't, leave that line out.
- **If the article has no abstract,** write only `_The original article has no abstract._`.

## The plan file

Write JSON in exactly this shape:

```json
{
  "parts": [
    {"first_block": 1, "last_block": 20, "minutes": 3.9, "ends_with": "end of the introduction, before section 2"},
    {"first_block": 21, "last_block": 48, "minutes": 4.2, "ends_with": "calm-water resistance fully explained, before section 2.2.2"}
  ],
  "drop": [
    {"block": 1, "reason": "publisher logo"},
    {"block": 18, "reason": "running header"}
  ],
  "back_matter_first_block": 210
}
```

- **`parts`** cover the article in order with no gaps or overlaps:
  - The first part starts at `B1`.
  - Each part starts right after the previous one ends.
  - The last part ends right before `back_matter_first_block`, or at the last block if there is no back matter.
  - Deleted blocks stay inside the part range they fall in; listing them in `drop` is what removes them.
- **`drop`** lists every deleted block, each with a short reason. Every part must keep at least one block.
- **Block numbers** are written without the `B`.
- **`minutes` and `ends_with`** are for the people reviewing the plan. The pipeline recalculates the minutes itself, and they don't change the cut.

## Checklist before writing the files

- [ ] Every masthead, logo, badge, running header, footer, boilerplate, contact-detail, author, affiliation and abstract block is in `drop`.
- [ ] Every graphic you drop has been opened, or is plainly decoration from its size and position. The only content graphic you drop is the abstract.
- [ ] The abstract file has the abstract word for word, plus the keywords if there are any.
- [ ] Each part ends on a finished thought, not inside a sentence, list, explanation, argument or derivation.
- [ ] Each cut is the strongest boundary available within roughly 3:30 to 6:00. A heading is never passed over for a paragraph break just to get closer to 4-5 minutes.
- [ ] No part ends on a heading, and no part splits a sentence interrupted by page furniture.
- [ ] Every graphic you keep is in the same part as its text, caption and `pic-text`.
- [ ] Each part takes 4-5 minutes without its deleted blocks, or has a rule-2 reason not to.
- [ ] Each part starts and ends with text where possible.
- [ ] The parts are contiguous, from `B1` to the back matter or the last block.
- [ ] The metadata has the title, every author and affiliation, and a topic phrase.
