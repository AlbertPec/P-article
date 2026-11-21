---
name: rewrite-part
description: Rewrites one part of a scientific article for the app's readers, in the style set by a settings file, without changing any data, graphic or equation, and keeps the style of the parts before it through a shared notes file. Called by the pipeline as /article:rewrite-part <parts folder> <output folder> <part file> <notes file> <abstract file> <settings file>.
disable-model-invocation: true
---

# Rewrite one part of an article

The app shows a scientific article as a series of parts, each taking a few minutes to read. Your job is to rewrite one part so the readers in the settings can follow it easily. You change **how** it's said, never **what** it says.

Arguments: `$ARGUMENTS`

1. **The parts folder:** the original parts, `part_1.md`, `part_2.md`, and so on. Read only. Never write, edit or delete anything in it.
2. **The output folder:** the rewritten parts go here, under the same file names.
3. **The part file** to rewrite now, for example `part_3.md`.
4. **The notes file**, shared by every part of this article.
5. **The abstract file:** the article's abstract, as context about the whole article. Don't rewrite it.
6. **The settings file:** the style to write in, as JSON.

All paths are relative to the current folder. You see only one part. The previous rewritten part and the notes are how this part stays consistent with the rest of the article.

## Steps

1. Read the settings file.
2. Read the abstract file, so you know where this part fits in the whole article.
3. If the notes file exists, read it. It records what earlier parts decided: terms, what has already been explained, metaphors and tone.
4. If the part number is greater than 1, read the previous rewritten part, `<output folder>/part_<number - 1>.md`.
5. Read the part to rewrite from the parts folder.
6. Rewrite it, following the rules below, most important first.
7. Check your draft against the checklist at the end.
8. Write it to `<output folder>/<part file>`.
9. Update the notes file (see "The notes file").
10. Reply with one line: the output path and roughly how many words the part has.

If the message says a previous attempt failed its check, read your earlier output in the output folder, fix exactly the problems named, write it again and update the notes if needed. Don't start the style over.

## The settings file

```json
{
  "audience": "curious adults with no background in the field",
  "language": "same as the original",
  "style": "friendly",
  "explanation": "moderate",
  "metaphors": "occasional",
  "sentences": "shorter",
  "length": {"min_ratio": 0.85, "max_ratio": 1.3},
  "extra_instructions": "",
  "word_budget": {"part_1.md": {"original_words": 812, "min_words": 690, "max_words": 1056}}
}
```

Ignore `model`, if it's there; it's for the pipeline.

- **`audience`:** who you write for. Decide what they already know from this.
- **`language`:** the language to write in. `same as the original` means the article's language. When translating, still copy every number, symbol, unit abbreviation and citation exactly (rule 1).
- **`style`:**
  - `formal`: an academic but clear register. No contractions, no addressing the reader, no jokes.
  - `neutral`: plain, factual popular-science prose, like a good encyclopedia.
  - `friendly`: warm and conversational. You may address the reader ("you"), use contractions and ask an occasional question, but stay precise.
  - `catchy`: lively, like a good science magazine. Vivid verbs, strong first sentences, some rhythm and surprise. Never hype: no exaggeration, no claims stronger than the article's, no clickbait.
- **`explanation`:** how much to add for readers who don't know the field.
  - `none`: add nothing. Only make the existing text clearer.
  - `light`: a few words for the most important specialist terms, the first time they appear, for example "the Froude number (a measure of how fast a ship moves for its length)".
  - `moderate`: a sentence for each important term and concept the first time it appears, and a short plain-words summary after a dense passage or a derivation, saying what it shows.
  - `thorough`: explain every specialist term, say in words what each equation calculates and why it matters, and give the reader the background they need to follow the argument.
- **`metaphors`:** comparisons and images that make an idea concrete.
  - `none`: no metaphors or analogies.
  - `occasional`: at most one or two in the part, only where an idea is hard to picture.
  - `frequent`: use them wherever they help understanding, but never one that is misleading.
- **`sentences`:**
  - `as_original`: keep the original sentence structure where it's clear, and only untangle confusing sentences.
  - `shorter`: split long sentences, prefer the active voice, one idea per sentence where possible.
  - `short_and_simple`: short sentences, everyday words, very few clauses.
- **`length` and `word_budget`:** how long the rewritten text may be. `word_budget` has this part's numbers: the original text has `original_words` words, and the rewritten text must have between `min_words` and `max_words`. Graphics, equations and captions don't count; only your text does. The pipeline counts the words and fails the part if it's outside the range.
- **`extra_instructions`:** anything else the editor wants. Follow it, unless it conflicts with rules 1 or 2.

## Rules, most important first

### 1. Never change the data

You may change the wording, the order of sentences within a paragraph, and how ideas are explained. Never change what the article states:

- **Every number stays exactly as written:** values, units, percentages, dates, years, counts, and the numbers of figures, tables, equations and sections. `36.58 h` stays `36.58 h`; it never becomes `36.6 h`, `about 37 hours`, `over a day and a half` or `thirty-six`. Write numbers in digits, as the original does. You may add words around a number, such as "36.58 hours (h)".
- **No new numbers.** Don't add values, examples with numbers, conversions (knots to km/h, tonnes to pounds) or counts that aren't in the part or the abstract. The pipeline rejects any number that isn't in the original part or the abstract. Background explanations must be in words only.
- **Every result, comparison and direction stays the same:** which route is shorter, what increases or decreases, what is greater than what, under which conditions. Don't make a claim stronger or weaker: "may", "about", "in this case" and other hedges stay.
- **Names stay:** methods, models, ships, places, datasets, and the authors cited. Keep each citation, such as "(Kwon, 2008)" or "Townsin and Kwon (1993)", with the claim it supports.
- **Symbols stay where the equations need them.** The equations are images, and they use symbols like `Vs,i` or `CB`. When the original says what a symbol means, keep the symbol in that sentence so the reader can match it to the equation, and add the meaning in words as the explanation setting asks.
- **Add no facts about this study.** Explanations may use widely known general knowledge (what the Beaufort scale is, what a Froude number measures), but never claims about this article's data, method or results that the part doesn't make.
- **If the text is garbled or a piece is missing** because of the PDF conversion, don't guess what was lost. Join what's there as smoothly as you can without adding information.

### 2. Graphics, equations and captions stay exactly as they are

These blocks are protected:

- every image line, such as `![](images/test-article.pdf-0002-27.png)` or `![Table 2](images/table_002.png)`
- every `<!-- Start of picture text -->` … `<!-- End of picture text -->` block, the parser's text version of the equation or table before it
- every caption: blocks starting with `**Fig. N.**`, `**Figure N**`, `**Table N**` and similar, and a table's title, the text block right after its `**Table N**` label

Copy each protected block **byte for byte**, including spaces, `<br>`, underscores and odd spacing, as its own block with a blank line before and after it. Keep them all, in their original order. Don't explain inside them, translate them, fix typos in them or merge them with your text.

You may move a protected block only to repair a sentence. The PDF's page breaks sometimes put a figure, a table or an equation in the middle of a sentence. Then join the sentence and put the protected blocks, still in their order, after the paragraph that contains that sentence. Otherwise leave each protected block where it is in relation to the text around it, so equations stay between the sentences that introduce and explain them.

### 3. Keep the length

Stay within `min_words` to `max_words` of `word_budget`. Explanations take space, so make room by cutting repetition and wordiness, not content. If the explanation setting asks for more than fits, explain the most important terms and keep the others brief. A part that is a few minutes long in the original should still be roughly that long.

### 4. Write in the style of the settings

Follow `audience`, `style`, `explanation`, `metaphors`, `sentences` and `extra_instructions` as described above. The rewritten text should read as one natural piece of writing, not as the original with explanations bolted on.

### 5. Stay consistent with the earlier parts

- Use the same voice and register as the previous rewritten part.
- Use the terms the notes record, in the same form. Don't rename a concept that earlier parts named.
- Don't explain again what the notes say was already explained. A brief reminder of a few words is fine when a term returns after a long gap.
- Reuse a metaphor from the notes when its idea comes back, rather than inventing a different image for it. Don't start a new metaphor that clashes with an earlier one.
- Don't add a summary of earlier parts or a preview of later ones, and don't write about the parts themselves ("in this part…"). The app shows the headlines.

### 6. Keep the structure

- Keep every heading, its level (`###`) and its number. You may make its wording plainer, in the same style, but don't add, remove or merge headings.
- Keep the paragraphs in their order. You may split a long paragraph or turn an enumeration into a bulleted list.
- Fix the PDF's leftovers in the text: hyphens split across lines ("i- th" becomes "i-th"), stray spaces before punctuation, and `<sup>`/`<sub>` tags, which you may write as Unicode (`m³`, `CO₂`). Don't change protected blocks while doing this.
- Keep Markdown simple: headings, paragraphs, lists, `_italics_` and `**bold**`.

## The notes file

The notes are the memory passed from part to part. Each agent sees only its own part, the previous rewritten part and these notes. Write them for the agent that rewrites the next part.

After writing the part, rewrite the whole notes file so it holds everything later parts need, and nothing they don't. Merge what's there with what this part decided, rather than only appending. Keep it under about 6000 characters; the pipeline fails the part at 8000.

Use these sections:

```markdown
## Voice
- How the text sounds: register, how the reader is addressed, typical sentence length.

## Terms
- Froude number (Fr): explained in part_2 as "how fast a ship moves for its length".

## Explained already
- Calm-water resistance and its three parts (part_1).

## Metaphors used
- Added resistance as "a headwind tax on every mile" (part_2).

## Open threads
- Part 4 ended before the results for Route 2; the next part picks them up.
```

If a previous attempt at this part already added notes for it, replace them instead of adding them again.

## Checklist before writing

- [ ] Every number in the original text is in your text, written exactly the same.
- [ ] You added no number that isn't in the original part or the abstract, including in explanations.
- [ ] Every result, comparison, hedge, name and citation is unchanged.
- [ ] Every image line, picture-text block and caption is copied byte for byte, as its own block, in the original order.
- [ ] The text without graphics has between `min_words` and `max_words` words.
- [ ] Every heading is kept, with its level and number.
- [ ] The style, explanation level, metaphors and sentence length follow the settings.
- [ ] Terms, voice and metaphors match the notes and the previous part.
- [ ] You wrote only to the output folder and the notes file, never to the parts folder.
