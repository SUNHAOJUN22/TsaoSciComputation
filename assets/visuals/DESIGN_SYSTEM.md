# Scientific Swiss Bento V12 visual system

This design system applies the current UI/UX Pro Max priority model to GitHub README illustrations for TsaoSciComputation.

## Product and audience

- Product type: scientific developer tool and evidence-bound orchestration platform.
- Audience: researchers, simulation engineers, software reviewers and technical decision makers.
- Primary context: GitHub README at desktop, tablet and narrow browser widths.
- Primary task: understand scope, execution order, evidence strength and failure boundaries without zooming the page.

## Design dials

- Variance: 6/10 — five governed information layouts remain visually related.
- Motion: 0/10 — static repository SVGs make no interaction claim.
- Density: 5/10 — reduced from V11 so diagrams remain legible after GitHub scaling.

## Responsive presentation tiers

| Tier | README treatment | Visual purpose |
|---|---|---|
| Hero | Full width above the project title | Product scope and primary evidence narrative |
| Overview | At most two compact Bento diagrams in one row | Architecture and capability orientation |
| Detail | Full-width diagrams inside semantic `<details>` groups | Workflows, loops, risk and scientific evidence |

Detailed Workflow, Loop and Risk diagrams must never be placed in a 50% README column. Progressive disclosure keeps the first screen concise without removing any capability documentation.

## Layout families

| Layout | Purpose |
|---|---|
| Hero | Establish product scope and the principal evidence narrative |
| Bento | Compare architecture, registries and governance responsibilities |
| Workflow | Explain ordered computation and cross-scale handoffs |
| Loop | Show iterative learning, updating and evidence feedback |
| Risk | Separate initiating conditions, barriers, consequences and authority |

## Typography and spacing

- Minimum SVG text size: 16 px.
- Stage labels: 20–22 px; headings: 34–46 px.
- Detail copy is limited to two concise lines per stage.
- Structural spacing follows an 8 px rhythm.
- Full-width diagrams use a wide, shallow canvas to preserve readable type at GitHub scale.

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

- Information is never encoded by color alone.
- Every illustration has a unique accessible `<title>` and `<desc>`.
- Every SVG declares its design system, scientific family and information layout.
- No external fonts, scripts, raster images, network resources, event handlers or tracking.
- Diagrams explain architecture and scientific boundaries; they are not solver screenshots, benchmark plots or live-execution evidence.

## Anti-patterns

- Detailed diagrams placed in narrow two-column README cells.
- Body labels below 16 px or more than two dense detail lines per stage.
- Forty-two illustrations expanded at once with no progressive disclosure.
- Purple/pink AI gradients, neon glow, glass decoration or simulated dashboards.
- Fabricated curves, numerical values or external-engine screenshots.
