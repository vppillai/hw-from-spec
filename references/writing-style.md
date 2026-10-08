# Writing style — every document the skill holds or produces

Owner rule: follow the Google developer documentation style guide, use ASD-STE100 derived precision rules, and apply Zinsser's four
principles: clarity, simplicity, brevity, humanity. This page turns the three sources into rules you can check. `scripts/style_lint.py`
checks the measurable ones on the skill's own text; the smoke runs it. Apply the same rules to project READMEs, records, kit texts, replies
to a vendor, and chat reports.

## 1. Sentences (ASD-STE100)
- One instruction per sentence. One topic per sentence.
- An instruction sentence has at most 20 words. A description sentence has at most 25. The lint fails a sentence over 40 words today and
  reports every sentence over 25; the cap tightens as the text improves.
- Write instructions in the imperative: "Run the gate." Write descriptions in the present tense: "The gate reads the cell."
- Keep a sentence to one clause where you can. Replace an em-dash or a semicolon with a full stop.
- Do not stack more than three nouns. "The vendor file review step" becomes "the step where the vendor reviews the file".
- Use the same word for the same thing in the whole document. No synonyms for a technical term.
- Use a word with one meaning. "Check" is a verb. "Record" is a noun for a file under `90-log/`.

## 2. Voice and person (Google)
- Second person: "you". The reader is the person who runs the step, or the agent that runs it.
- Active voice. "The census flags the wall", not "the wall is flagged by the census".
- Present tense. "The script writes", not "the script will write".
- Plain words. "Use", not "utilize". "Because", not "due to the fact that". "To", not "in order to". <!-- style: ok -->
- No Latin abbreviations: write "for example", "that is", and end a list without "etc.". <!-- style: ok -->
- Not "via": write "through" or "with". Not "and/or": pick one, or write both cases. <!-- style: ok -->
- No "please", "simply", "easily", "obviously", "of course", "basically", "actually", "note that". <!-- style: ok -->
- Sentence-case headings. UI labels in **bold**. Code, paths, keys and commands in `code font`.
- Numbers: digits for measurements and counts in tables; words for counts up to nine in running text when the count is not a measurement.
- The serial comma. One space after a full stop.

## 3. Clarity, simplicity, brevity, humanity (Zinsser)
- Lead with the result or the action. The reader learns what to do in the first sentence.
- Cut every word that does no work. Read the sentence without the word; if the meaning holds, the word goes.
- One idea per paragraph. A list for parallel items, prose for one line of argument.
- Say what you do not know. "Not measured" is better than a hedge.
- Write to a person. Say who did what: "The owner sends the reply." Never "it was decided".
- Keep the reason for a rule as one short clause. The episode behind it goes to `references/pitfalls.md` as a dated line.

## 4. Where the rules apply
- The skill: `SKILL.md`, `README.md`, every reference, every template. `scripts/style_lint.py` and `scripts/doc_voice_lint.py` gate them;
  `scripts/generic_lint.py` keeps them free of project names.
- A project: folder READMEs (`references/project-yaml.md` §Layout), kit texts (`references/print-kit.md` §3), records under `90-log/`,
  order records, vendor replies (`references/vendor-review.md`), and the chat report at the end of a task (`references/agent-ops.md` §6).
- Not the owner's own words. A quoted owner sentence keeps its wording; mark the line `<!-- style: ok -->` when the lint trips on it.

## 5. How to fix a hit
- A long sentence: find the second verb and start a new sentence there. Move a parenthesis into its own sentence.
- A passive: name the actor. If no actor exists, the sentence states a fact: "The file is empty" is fine.
- A clutter word: delete it. If the sentence loses meaning, the meaning was elsewhere; write that.
- A Latin abbreviation: "for example" or "that is", or restructure the list.
- A dash chain: one fact per sentence. Keep the order of facts.
