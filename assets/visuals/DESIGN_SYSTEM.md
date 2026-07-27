# Scientific Swiss Bento V11 visual system

This design system applies the current UI/UX Pro Max priority model to the static README illustrations in TsaoSciComputation.

## Product and audience

- Product type: scientific developer tool and evidence-bound orchestration platform.
- Audience: researchers, simulation engineers, software reviewers and technical decision makers.
- Context: GitHub README, source archives and offline documentation.
- Primary task: understand capability, execution order, evidence strength, failure boundaries and review authority quickly.

## Design dials

- Variance: 6/10 — one coherent system with multiple information structures.
- Motion: 0/10 — repository SVGs are static and make no interaction claim.
- Density: 7/10 — technical information remains compact but readable.

## Layout families

| Layout | Purpose | Typical use |
|---|---|---|
| Hero | Establish product scope and the principal evidence narrative | Repository hero |
| Bento | Compare layers, registries, systems and governance responsibilities | Architecture and capability maps |
| Workflow | Explain ordered computation and cross-scale handoffs | Quantum, materials, CFD and process workflows |
| Loop | Show iterative learning, updating, validation or evidence feedback | Active learning, inverse design, twins and acceptance loops |
| Risk | Separate initiating conditions, barriers, consequences and authority | Safety, degradation, failure recovery and operational controls |

The layout is selected from the information model, not chosen decoratively. All layouts share the same tokens, type hierarchy, stroke system and evidence vocabulary.

## Style

- Swiss minimalism for alignment, typography and hierarchy.
- Bento composition for dense scientific information.
- Restrained AI-native accents for routing and evidence states.
- Flat surfaces, 2 px structural strokes and 3 px focal glyph strokes.
- Direction and status are expressed through labels, numbering and geometry, never color alone.

## Tokens

| Role | Token |
|---|---|
| Canvas | `#0B1220` |
| Surface | `#111827` |
| Raised surface | `#172033` |
| Border | `#334155` |
| Primary text | `#F8FAFC` |
| Secondary text | `#CBD5E1` |
| Muted text | `#94A3B8` |
| Blue | `#3B82F6` |
| Cyan | `#06B6D4` |
| Teal | `#14B8A6` |
| Green | `#22C55E` |
| Amber | `#F59E0B` |
| Orange | `#F97316` |
| Risk red | `#EF4444` |

## Accessibility and trust rules

- Normal text uses high-contrast foreground/background pairs.
- Body labels are at least 13 px in the SVG coordinate system.
- Every illustration has a unique accessible `<title>` and `<desc>`.
- Every diagram identifies its layout and scientific family in machine-readable attributes.
- Evidence stages remain visible as text and geometry when color is unavailable.
- No external fonts, scripts, raster images, network resources, event handlers or tracking.
- Diagrams explain architecture and scientific boundaries; they are not solver screenshots, benchmark plots or live-execution evidence.

## Anti-patterns

- Forty-two copies of one diagram template with only labels changed.
- Purple/pink AI gradients, neon glow, glass decoration or simulated dashboards.
- Random radii, shadows, stroke weights or icon styles.
- Tiny labels, color-only status, unlabeled arrows or decorative complexity.
- Fabricated scientific curves, numerical values or external-engine screenshots.
