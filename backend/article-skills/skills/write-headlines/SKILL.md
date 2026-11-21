---
name: write-headlines
description: Writes three short, catchy, slightly clickbaity headlines for every part of an article, faithful to the science, and saves them as JSON. Called by the pipeline as /article:write-headlines <parts folder> <output file> <article id> <abstract file>.
disable-model-invocation: true
---

# Write headlines for each part

The app shows an article as a series of parts. Each part needs **3 alternative headlines**: short, catchy hooks that make a reader tap the part, in the spirit of a popular science magazine. A little clickbait is welcome. Lies are not.

Arguments: `$ARGUMENTS`

1. **The parts folder:** the rewritten parts, `part_1.md`, `part_2.md`, and so on.
2. **The output file:** the JSON file to write.
3. **The article id:** copy it into the JSON exactly.
4. **The abstract file:** the article's abstract, as context about the whole story.

All paths are relative to the current folder. Read only these files, and write only the output file.

## Steps

1. Read the abstract.
2. Find every `part_<number>.md` in the parts folder with Glob, and read every one of them, in order. You write all the headlines together, so they can differ from each other across the article.
3. For each part, find its story (see "Find the hook"), then write 3 headlines that follow the rules.
4. Check everything against the checklist at the end.
5. Write the output file.
6. Reply with one line: how many parts got headlines.

## Find the hook

Don't describe what the part discusses. Find the most interesting thing in it and make the reader want the answer:

- a surprise, a paradox, or something that seems obvious but turns out to be wrong
- a conflict: ship against weather, speed against fuel, safety against cost
- a dilemma or a trade-off with stakes
- an unexpected consequence, or a hidden problem
- a concrete, striking result

Then open an information gap: show the stakes, and leave the answer to the part.

## Rules

### 1. Short

- **At most 60 characters, ideally 3 to 9 words.** The pipeline rejects any headline over 70 characters.
- One sentence or one short phrase. At most one colon or dash.
- Cut every word that doesn't add punch.

### 2. Catchy, a little clickbaity

- Punchy, playful, dramatic or mischievous, written in natural, idiomatic language.
- Tease rather than tell: "The Shortcut That Cost More Fuel" beats "Comparing Route Fuel Use".
- Give things personality: the wind as a rival, the engine as an exhausted workhorse, a model as a detective. Use this selectively.
- Comparisons from everyday life, business, sport, games, crime stories or pop culture are welcome when they fit the content.
- Avoid tired clickbait: "You Won't Believe…", "This Changes Everything", "Scientists Are Shocked", "The Amazing Truth About…".
- Never sound like an academic section heading: "Analysis of Engine Power Under Weather Conditions" is wrong.

Good, for a ship-routing article:
- "The Wind Changed. So Did the Fuel Bill."
- "Fast, Cheap or Safe? Pick Two."
- "The Shortest Route Isn't the Cheapest"
- "Beaufort 4 and a Very Tired Engine"

### 3. True to the part

Clickbait may tease, but must never mislead:

- Every headline is about its own part, and the part delivers what the headline promises.
- Never invent results, events, dangers or numbers. A number may appear only if it's in that part or the abstract, written the same way. The pipeline rejects any other number.
- Never imply that something hypothetical actually happened, or that a model proved more than it did.
- A metaphor must not change the scientific meaning.

### 4. Three different ideas per part

The 3 headlines for a part must take genuinely different angles, not rephrase one idea. For example, one witty or ironic, one dramatic or suspenseful, one with an unexpected comparison. Don't use that pattern mechanically; choose angles that suit the part.

### 5. Variety across the article

- Don't repeat a headline, and don't start two headlines with the same words.
- Don't lean on one device: rhetorical questions, "What if…", "Why…", "When X meets Y", "The X that…", "The price of…", lists of three, and colon constructions are each fine occasionally, never as a habit.
- Vary the rhythm, the length, the opening words, the humour and the imagery from part to part.

### 6. Language and style

- Write in the language of the parts.
- Use title case in English, or the normal capitalization of the parts' language.
- No quotation marks around the headline, no emoji, no hashtags. A final full stop is optional; be consistent within the article.

## The output file

Write JSON in exactly this shape, with one entry per part, keyed by the file name without `.md`:

```json
{
  "article_id": "<article id>",
  "headers": {
    "part_1": [
      {"title": "The Wind Changed. So Did the Fuel Bill."},
      {"title": "Fast, Cheap or Safe? Pick Two."},
      {"title": "A Tanker, a Storm and a Very Long Detour"}
    ]
  }
}
```

Every part gets exactly 3 objects, and each object has only the `title` field.

## Checklist before writing

- [ ] Every part has exactly 3 headlines, and the keys match the part files.
- [ ] Every headline is at most 60 characters, and none is over 70.
- [ ] Every headline is a hook, not a description or an academic heading.
- [ ] Every headline is true to its part, and every number in it is in that part or the abstract.
- [ ] The 3 headlines of each part take different angles.
- [ ] No headline repeats, no two start with the same words, and no device is overused.
- [ ] `article_id` is copied exactly, and the file is valid JSON.
