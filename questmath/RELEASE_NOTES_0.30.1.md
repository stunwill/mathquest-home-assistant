# MathQuest 0.30.1

## Worksheet quality corrective release

This release fixes issues identified during real worksheet testing after v0.30.0 Visual Mathematics.

### Completion recommendations

- **Strongest** now comes from broader persisted learner mastery evidence rather than only the topic represented in the worksheet just completed.
- **Practise next** uses the adaptive next-session recommendation and can therefore point to a different learning area.
- When there is not enough cross-category history for a meaningful comparison, MathQuest shows neutral guidance rather than inventing a ranking.

### Question variety

- Parameter-only variants from the same question template are now treated as one question family.
- Probability worksheets avoid repeating the same coin-toss variation question with only different heads/tails counts when another suitable family is available.
- The family guard applies generally to short worksheets and retains a safe fallback for genuinely constrained question pools.

### Fraction number lines

- Fraction number-line questions now derive their subdivisions from the denominator.
- `8/10` is displayed on a 0-to-1 line with ten equal intervals.
- Intermediate fractional values are no longer rounded into misleading integer labels such as `0, 0, 1`.

### Visual relevance

- Probability questions no longer recommend an unrelated number-line teaching model.
- When a compatible interactive Probability model is not available, the teaching-model action is withheld instead of showing irrelevant support.

### Compatibility

- Preserves v0.30.0 Visual Mathematics and all v0.29.1 corrective safeguards.
- Preserves Math Mentor, optional retry-first tutoring, keyboard answer flow, prerequisite evidence, misconception evidence and spaced retrieval.
- No destructive database migration is required.
