# Project design specification

This project-local specification records design intent. Update it as the brief becomes concrete. Direct user instructions, AGENTS.md and the selected agent mode take precedence. Preserve existing work and use this project’s actual foundations rather than assuming a generic style.

## Product and audience
- Product purpose and key task: to be defined from the brief.
- Intended audience, content and representative screen sizes: to be defined.
- Choose a coherent visual direction suited to the product; maintain established brand decisions.

## Foundations
- Define semantic palette roles such as surface, text, muted text, border, accent and status; check readable contrast.
- Define typography roles such as display, heading, body, label and caption. Preserve existing font choices when present.
- Use a consistent spacing scale with explicit container padding and gaps. Record chosen token values here as the design evolves.

## Layout and alignment
- Buttons: use a horizontal auto-layout frame, intentional padding/gap and requested alignment. Auto-width labels hug their text; minimum control dimensions belong to the container. Check label/icon alignment in screenshots.
- Cards: use nested rows/columns, stretch or fill children deliberately, and let auto-height paragraphs wrap at their assigned width. Hug content height where appropriate; fixed height requires a deliberate clipping/overflow decision.
- Avoid per-child position nudges to compensate for incorrect container sizing. Verify narrow and wide representative sizes for wrapping, clipping and stable alignment.

## Reusable design system
- Inspect existing components, collections, modes, variable values and bindings first.
- Create semantic foundation variables, then reusable component masters, bind applicable properties to variables and compose screens from instances. Keep stable identities and reuse existing tokens/components.
- Record component roles, states, variants, and chosen theme modes here. Verify that mode changes resolve the intended bound values.

## Images and vectors
- Reuse supplied project assets. Offer generated imagery or SVG artwork when it materially improves the requested design and the brief leaves it open; ask about intent before preparing a generation request.
- Generation preparation opens the existing composer for review. It does not submit a paid request or promise an unavailable model.

## Acceptance checks
- Save complete valid FNX documents and inspect parser diagnostics.
- Verify screenshots of changed frames at representative sizes; fix misalignment, overlaps, clipping, typography and contrast before reporting completion.
- Check component reuse and bound variable modes. Preserve user content and existing project rules.
