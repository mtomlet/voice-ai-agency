/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark luxury palette
        'noir': {
          900: '#0a0a0a',
          800: '#121212',
          700: '#1a1a1a',
          600: '#2a2a2a',
          500: '#3a3a3a',
        },
        'gold': {
          DEFAULT: '#c9a227',
          light: '#d4af37',
          dark: '#b8941f',
          muted: 'rgba(201, 162, 39, 0.1)',
        },
        'cream': '#f5f5f5',
      },
      fontFamily: {
        'serif': ['Playfair Display', 'serif'],
        'sans': ['Outfit', 'sans-serif'],
      },
      letterSpacing: {
        'ultra': '0.2em',
        'mega': '0.3em',
      },
      animation: {
        'shimmer': 'shimmer 2s linear infinite',
        'pulse-gold': 'pulse-gold 2s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'fade-in': 'fade-in 0.6s ease-out forwards',
        'slide-up': 'slide-up 0.6s ease-out forwards',
        'waveform': 'waveform 0.5s ease-in-out infinite alternate',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'pulse-gold': {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(201, 162, 39, 0.4)' },
          '50%': { boxShadow: '0 0 0 20px rgba(201, 162, 39, 0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        waveform: {
          '0%': { transform: 'scaleY(0.3)' },
          '100%': { transform: 'scaleY(1)' },
        },
      },
      backgroundImage: {
        'gradient-gold': 'linear-gradient(135deg, #c9a227 0%, #d4af37 50%, #b8941f 100%)',
        'gradient-dark': 'linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%)',
      },
    },
  },
  plugins: [],
}
