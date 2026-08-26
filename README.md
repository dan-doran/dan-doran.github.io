# Dan Doran Consulting site

```
index.html                     fully static site
css/site.css                   the design system
case-studies/                  long-form pages
  midpoint-tmobile-api-migration.html
  filmpac-platform-modernization.html
  blue-mountain-hay-warehouse-system.html
  filmpac-hybrid-data-architecture.html
  governed-ai-assisted-development.html
sheets/                        the print views
  capability.html
  case-midpoint.html
  case-filmpac-modernization.html
  case-blue-mountain-hay.html
  case-filmpac-data.html
  case-governed-ai.html
css/sheet.css                  the print design system
pdf/                           built output (downloadables)
tools/build-sheets.sh          PDF builder
tools/night-gradient.py        regenerates the complex gradient
```
---

## How the design system works

### The rhythm unit

One expression governs all vertical space:

```css
--vertical-rhythm: calc(var(--font-size-base) * var(--line-height-base));
```

17px × 1.618 ≈ 27.5px. Margins, padding, and gap throughout the site is a whole
multiple of it, exposed as `--r1` through `--r6`. Heading leading is
set in whole multiples too.

### The grid

Every band is a `.canvas`: the classical asymmetric spread of a narrow left
margin, a text column capped at 65ch, and a wide right column for marginalia.

```css
grid-template-columns: minmax(100px, 1fr) minmax(auto, 65ch) minmax(150px, 1.618fr);
```

Members are placed on it directly--there are no wrapper divs. Content is set in a column with one of `.col-text` (2), `.col-spread` (2–3),
`.col-margin` (3), or `.col-full`. Layout changes only happen by mutating the parent grid inside one of four
discrete gates: 860, 1200, 1920, and print. Nothing scales "fluidly," in the contemporary way; there is no
`clamp()` or `vw` type on the site.

### Marginalia

Asides are placed by grid auto-flow.

### Type

While the aesthetic is Tschicholdian, neoclassical, yet no fonts need to be loaded;
the following are resident on Mac and Windows.

| Role | Face | Why                                                                                      |
|---|---|------------------------------------------------------------------------------------------|
| Display | **Palatino** | Zapf, cut by D. Stempel AG / Linotype, 1949–50.                                          |
| Text | **Georgia** | Carter's screen face, descended from the "news Romans" Linotype ran in the same decades. |
| Labels | **Futura / Avenir** | Standing in for Metro and Spartan, Dwiggins' geometric sans faces.                       |

### Color

**The "night" gradient is complex**, and is generated with a Python script. The ramp is defined in OKLCH (lightness and chroma on separate axes)
and sampled down to eleven sRGB stops. Using so many stops matters, for avoiding
the desaturated-middle problem. Pace Josh Comeau--see
[Make Beautiful Gradients](https://www.joshwcomeau.com/css/make-beautiful-gradients/). The script fails
if any adjacent color would drop below AA against the brightest stop. "Brass" is the tightest at
5.7:1; white is 13.9:1; and "jewel" links, 7.9:1.

`--night-low` is used where the gradient
ends. For example, the overscroll area is `--night-low`;
this can then join to the gradient with no visible seam. `--night-fallback` is used if gradients don't render.
`--ink-reverse` is dark lettering on the green buttons.

**The portrait treatment is also complex.** As the only raster element on
the site, in its original color it would appear almost pasted on. So it is gray-scaled, navy screened on the shadow end, brass
soft-lit on the highlights; the originally black ground becomes navy in a way the face appears to emerge from the gradient.

**Accent colors** are cream, brass, and a jewel-green. Two green ramps exist with different applications for WCAG purposes. Everything on the site clears 5.3:1; most of it clears AAA.

## PDFs

The case studies double as one-page downloadables. In the print design system, the night
gradient simplifies to white, and text re-flows to a two-column page with
the asides in a margin.
