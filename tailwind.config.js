/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        pitch: {
          void: 'var(--color-bg-void)',
          deep: 'var(--color-bg-deep)',
          card: 'var(--color-bg-card)',
          cardHover: 'var(--color-bg-card-hover)',
          elevated: 'var(--color-bg-elevated)',
        },
        brand: {
          gold: 'var(--color-gold-coin)',
          goldLight: 'var(--color-gold-light)',
          goldDark: 'var(--color-gold-dark)',
          goldGlow: 'var(--color-gold-glow)',
          turf: 'var(--color-turf-green)',
          turfGlow: 'var(--color-turf-glow)',
          crimson: 'var(--color-crimson-loss)',
          crimsonGlow: 'var(--color-crimson-glow)',
          cyan: 'var(--color-script-cyan)',
        },
        txt: {
          primary: 'var(--color-text-primary)',
          secondary: 'var(--color-text-secondary)',
          muted: 'var(--color-text-muted)',
          inverted: 'var(--color-text-inverted)',
        },
        borderUi: {
          subtle: 'var(--color-border-subtle)',
          strong: 'var(--color-border-strong)',
          active: 'var(--color-border-active)',
        }
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        'glow-gold': '0 0 25px -4px rgba(245, 196, 81, 0.25)',
        'glow-turf': '0 0 25px -4px rgba(0, 240, 132, 0.25)',
        'glow-crimson': '0 0 25px -4px rgba(255, 59, 86, 0.25)',
        'terminal': '0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 0 1px var(--color-border-subtle)',
      },
      animation: {
        'pulse-subtle': 'pulseSubtle 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2.5s linear infinite',
      },
      keyframes: {
        pulseSubtle: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.7 },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        }
      }
    },
  },
  plugins: [],
}
