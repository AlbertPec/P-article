---
name: write-headlines
description: Writes three headlines for every part of an article. Called by the pipeline as /article:write-headlines <parts folder> <output file> <article id>.
disable-model-invocation: true
---

# Write headlines for each part (mock)

Mock: replace with the real skill. For now it writes placeholder titles from each part's first heading, so the pipeline can be tested end to end.

Arguments: `$ARGUMENTS`

The first argument is the folder that holds `part_1.md`, `part_2.md`, and so on. The second is the JSON file to write. The third is the article id. Paths are relative to the current folder.

1. Find every `part_<number>.md` file in the parts folder with Glob.
2. Use Grep on the parts folder with the pattern `^#`, output mode `content` and line numbers shown. Each result line starts with the file it came from.
3. For each part, take the first heading that Grep found in that part's own file. Remove the leading `#` characters, any `*` or `_` around the text, and surrounding spaces. If the file has no heading, use `Part <number>`.
4. Write the output file as JSON in exactly this shape, with one entry per part, keyed by the file name without `.md`:

   ```json
   {
     "article_id": "<article id>",
     "headers": {
       "part_1": [
         {"title": "Mock 1: <heading>"},
         {"title": "Mock 2: <heading>"},
         {"title": "Mock 3: <heading>"}
       ]
     }
   }
   ```

   Every part gets exactly 3 objects, and each object has only the `title` field.
5. Reply with one line: how many parts got headlines.
