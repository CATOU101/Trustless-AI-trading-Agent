/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f3f4f6",
        card: "#ffffff",
        ink: "#0f172a",
        accent: "#0ea5e9"
      }
    }
  },
  plugins: []
};
