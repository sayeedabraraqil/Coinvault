# COINVAULT Design System v1.0
*Esports Trading Terminal Meets Luxury Sports Heritage*

---

## 1. Aesthetic Thesis & Philosophy
COINVAULT rejects generic crypto templates, purple-on-white gradients, and uninspired Bootstrap tables. The interface treats eFootball coins not as casual game points, but as sovereign esports capital. 

The visual experience blends:
1. **The Tactical Night Pitch**: Deep `#07090C` void black, atmospheric floodlight gradients, micro-mesh pitch grids, and high-frequency live data streams.
2. **Fintech Precision**: Fixed-width tabular figures (`font-variant-numeric: tabular-nums`), sub-pixel 1px borders, real-time tick animations, and interactive sparklines.
3. **Luxury Athletic Accents**: Aureum Gold (`#F5C451`) reserved strictly for coin currency and top-tier podium ranks; Electric Turf (`#00F084`) for positive yield and verified status; Crimson Negative (`#FF3B56`) for drawdowns and spending.

---

## 2. Color Tokens

### 2.1 Dark Mode (Default)
| Token | Variable | Hex / Value | Purpose |
|---|---|---|---|
| `bg-void` | `--color-bg-void` | `#07090C` | Ultimate canvas background (Night Pitch) |
| `bg-deep` | `--color-bg-deep` | `#0D1117` | Structural containers, sidebar, footer |
| `bg-card` | `--color-bg-card` | `rgba(19, 25, 34, 0.75)` | Frosted glass card surface |
| `bg-card-hover`| `--color-bg-card-hover` | `rgba(26, 34, 48, 0.90)` | Interactive card hover state |
| `bg-elevated` | `--color-bg-elevated` | `#1B2433` | Dropdowns, tooltips, flyout menus |
| `bg-modal` | `--color-bg-modal` | `#0F141C` | Focused dialogs and balance entry modal |
| `border-subtle`| `--color-border-subtle` | `rgba(255, 255, 255, 0.08)` | Baseline structural separators |
| `border-strong`| `--color-border-strong` | `rgba(255, 255, 255, 0.18)` | Active input borders, prominent cards |
| `border-active`| `--color-border-active` | `rgba(245, 196, 81, 0.45)` | Focus ring and highlighted rows |
| `gold-coin` | `--color-gold-coin` | `#F5C451` | eFootball Coin primary accent |
| `gold-glow` | `--color-gold-glow` | `rgba(245, 196, 81, 0.18)` | Ambient glow under gold cards |
| `turf-green` | `--color-turf-green` | `#00F084` | Positive delta, growth streaks, verified badge |
| `crimson-loss`| `--color-crimson-loss` | `#FF3B56` | Negative delta, spend alerts, anti-cheat flag |
| `script-cyan` | `--color-script-cyan` | `#00D8F6` | Tampermonkey userscript verification stream |

### 2.2 True Light Mode
| Token | Variable | Hex / Value | Purpose |
|---|---|---|---|
| `bg-void` | `--color-bg-void` | `#F8FAFC` | Daylight Court crisp base |
| `bg-deep` | `--color-bg-deep` | `#F1F5F9` | Section surfaces |
| `bg-card` | `--color-bg-card` | `rgba(255, 255, 255, 0.85)`| Polished translucent paper |
| `text-primary`| `--color-text-primary` | `#0F172A` | Slate 900 high-contrast typography |
| `gold-coin` | `--color-gold-coin` | `#D98214` | Deep Amber gold for WCAG AA contrast |
| `turf-green` | `--color-turf-green` | `#059669` | Emerald 600 for bright ambient reading |

---

## 3. Typography Scale & Families

### 3.1 Font Families
- **Display Face**: `Syne` (Weights: 700 Bold, 800 ExtraBold). Used for hero titles, section headers, podium names.
- **Interface Face**: `Inter` (Weights: 400 Regular, 500 Medium, 600 SemiBold, 700 Bold). Used for UI controls, navigation, labels.
- **Tabular Mono Face**: `JetBrains Mono` (Weights: 400, 700). Used for all numeric data, coin values, percentages, timestamps, and rank badges.

### 3.2 Type Scale
| Step | Size | Line Height | Tracking | Usage |
|---|---|---|---|---|
| `display-2xl`| 3.75rem (60px) | 1.05 | -0.04em | Landing Hero Headline |
| `display-xl` | 2.50rem (40px) | 1.15 | -0.03em | Primary Dashboard Total Figures |
| `display-lg` | 1.875rem (30px)| 1.25 | -0.02em | Section Titles & Modal Headers |
| `body-lg` | 1.125rem (18px)| 1.50 | -0.01em | Subtitles & Lead Paragraphs |
| `body-base` | 1.000rem (16px)| 1.50 | 0.00em | Standard Form Controls & Text |
| `body-sm` | 0.875rem (14px)| 1.45 | 0.01em | Leaderboard Table Cells, Badges |
| `mono-xs` | 0.750rem (12px)| 1.35 | 0.05em | Timestamps, In-Game IDs, Tooltips |

---

## 4. Spacing, Radius & Elevation Scale

### 4.1 Spacing Scale (4px Base Unit)
- `space-1`: 4px
- `space-2`: 8px
- `space-3`: 12px
- `space-4`: 16px
- `space-6`: 24px
- `space-8`: 32px
- `space-12`: 48px
- `space-16`: 64px

### 4.2 Border Radius
- `radius-sm`: 4px (Buttons, badges, tags)
- `radius-md`: 8px (Form inputs, pill switches, table row hover bounds)
- `radius-lg`: 14px (Cards, modal dialogues, podium containers)
- `radius-full`: 9999px (Avatars, status pills, circular action triggers)

### 4.3 Elevation & Shadows
- `elevation-low`: `0 2px 8px -2px rgba(0, 0, 0, 0.4), 0 0 0 1px var(--color-border-subtle)`
- `elevation-mid`: `0 12px 24px -8px rgba(0, 0, 0, 0.6), 0 0 0 1px var(--color-border-strong)`
- `elevation-modal`: `0 24px 64px -12px rgba(0, 0, 0, 0.85), 0 0 0 1px var(--color-border-strong)`
- `shadow-gold`: `0 0 30px -4px rgba(245, 196, 81, 0.22)`
- `shadow-turf`: `0 0 30px -4px rgba(0, 240, 132, 0.22)`

---

## 5. Motion Tokens & Micro-Interactions

### 5.1 Easing Curves
- `ease-spring`: `cubic-bezier(0.34, 1.56, 0.64, 1)` (Popovers, badges, rank shifts)
- `ease-smooth`: `cubic-bezier(0.16, 1, 0.3, 1)` (Modal entry, drawer slides)
- `ease-terminal`: `cubic-bezier(0.2, 0.8, 0.2, 1)` (Number tickers, sparklines)

### 5.2 Durations
- `duration-micro`: `120ms` (Button press, toggle flip)
- `duration-quick`: `200ms` (Hover highlight, tooltip reveal)
- `duration-standard`: `350ms` (Card expand, modal backdrop fade)
- `duration-odometer`: `1200ms` (Rolling digit counter from 0 to balance)

### 5.3 Signature Micro-Interactions
1. **Spotlight Tracking**: Radial gradient follower on desktop mouse movements.
2. **3D Interactive Tilt**: Mouse position tilts top-3 podium cards with perspective (`transform: perspective(1000px) rotateX(...) rotateY(...)`).
3. **Live Odometer Counter**: When balances update, numbers spin upward using rolling digits instead of instantaneous text replacement.
4. **Optimistic Submit**: Balance logs update UI instantly with a subtle pulsing state while awaiting confirmation.
5. **Reduced-Motion Fallback**: Automatically turns off parallax, tilt, and continuous ambient rotations when `prefers-reduced-motion: reduce` is detected.
