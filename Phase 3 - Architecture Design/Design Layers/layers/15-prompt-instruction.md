← [Back to Design Layers overview](../README.md)

# Layer 15 — Prompt and Instruction Layer

This is another missing layer. Prompts are not just text — in production, prompts become managed assets.

## Prompt architecture includes

- system prompt
- developer instructions
- task-specific prompts
- tool descriptions
- output schemas
- few-shot examples
- refusal rules
- business constraints
- style rules
- version control

## For enterprise

You should manage prompts like code:

- versioned
- tested
- reviewed
- measurable
- rollback-able

For example, an IDD generator should not just have one huge prompt. It should have separated instructions:

1. Template understanding prompt
2. Source extraction prompt
3. Section mapping prompt
4. Placeholder handling prompt
5. Table generation prompt
6. Final validation prompt
7. Formatting/export prompt

That is much more reliable.
