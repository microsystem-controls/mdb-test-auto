/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: 'class',
  content: ["../templates/**/*.html"],
  theme: {
    extend: {
			colors: {
				'microcoin-purple': "#4e2683",
				'microcoin-blue': "#006c7d",
			}
		},
  },
  plugins: [],
}

