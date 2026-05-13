/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./pages/templates/**/*.html",
    "./users/templates/**/*.html",
  ],
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light"],
  },
};
