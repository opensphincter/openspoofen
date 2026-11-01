/** @type {import('tailwindcss').Config} */
export default {
  content: ["./frontend/**/*.{js,jsx}", "./src/openspoofen/templates/dashboard.html"],
  theme: {
    extend: {
      colors: {
        shell: {
          950: "#071018",
          900: "#0c1822",
          800: "#122434",
          700: "#183246",
        },
        brass: {
          300: "#f8d47a",
          400: "#efbb42",
          500: "#c58b1e",
        },
        coral: {
          400: "#f77865",
          500: "#d65a48",
        },
        mint: {
          300: "#89efce",
          400: "#3ac899",
          500: "#168e6a",
        },
      },
      boxShadow: {
        shell: "0 28px 120px rgba(3, 8, 12, 0.55)",
        screen: "0 18px 50px rgba(12, 118, 255, 0.18)",
      },
      fontFamily: {
        display: ['Aptos Display', 'Segoe UI Variable Display', 'Trebuchet MS', 'sans-serif'],
        body: ['Aptos', 'Segoe UI Variable Text', 'Trebuchet MS', 'sans-serif'],
      },
    },
  },
  plugins: [],
};