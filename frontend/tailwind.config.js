/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./**/*.{html,js}",
        "!./node_modules/**"
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            colors: {
                brand: {
                    50: '#f0fdfa',
                    100: '#ccfbf1',
                    500: '#14b8a6', // Teal for trust/cleanliness
                    600: '#0d9488',
                    900: '#134e4a',
                }
            }
        },
    },
    plugins: [],
}
