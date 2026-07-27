# Scientific Swiss Bento visual system

This design system applies the priority rules from UI/UX Pro Max to the static README illustrations in TsaoSciComputation.

## Product and audience

- Product type: scientific developer tool and evidence-bound orchestration platform.
- Audience: researchers, simulation engineers, software reviewers and technical decision makers.
- Usage context: GitHub README, source archives and offline documentation.

## Design dials

- Variance: 4/10 — restrained and systematic rather than decorative.
- Motion: 0/10 — repository SVGs are static and make no interaction claim.
- Density: 7/10 — information-rich cards with explicit hierarchy and readable spacing.

## Style

- Swiss minimalism for typography, alignment and hierarchy.
- Bento-grid cards for dense scientific workflows.
- Restrained AI-native accents for routing and evidence states.
- Flat surfaces and consistent 2 px strokes; no glow-heavy or glass effects.

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
- Information is never encoded by color alone; numbered stages and text labels remain present.
- Body labels are at least 13 px in the SVG coordinate system.
- Every illustration has a unique accessible `<title>` and `<desc>`.
- No external fonts, scripts, raster images, network resources, event handlers or tracking.
- Diagrams explain architecture and evidence boundaries; they are not solver screenshots or live-execution evidence.

## Anti-patterns

- Purple/pink AI gradients and decorative neon glow.
- Randomly mixed visual styles, radii, shadows or stroke weights.
- Emoji icons, tiny text, color-only status, or dense unlabeled arrows.
- Decorative animation, simulated dashboards or fabricated scientific plots.
