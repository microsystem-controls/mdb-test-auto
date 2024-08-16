/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: 'class',
  content: ["../templates/**/*.html"],
  theme: {
    extend: {
			colors: {
				'microcoin-purple': "#4e2683",
				'microcoin-blue': "#006c7d",
				'microcoin-blue1': "#00718f",
				'microcoin-blue-dark': "#023368",
				'microcoin-red': "#ec1c24",
			}
		},
  },
  plugins: [],
}

