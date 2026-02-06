/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'hsl(221, 83%, 95%)',
          100: 'hsl(221, 83%, 90%)',
          200: 'hsl(221, 83%, 80%)',
          300: 'hsl(221, 83%, 70%)',
          400: 'hsl(221, 83%, 60%)',
          500: 'hsl(221, 83%, 53%)',
          600: 'hsl(221, 83%, 45%)',
          700: 'hsl(221, 83%, 35%)',
          800: 'hsl(221, 83%, 25%)',
          900: 'hsl(221, 83%, 15%)',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
      },
    },
  },
  plugins: [],
}