// dashboard-web/svelte.config.js
import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    kit: {
        adapter: adapter({
            // Opsi ini penting untuk Firebase Hosting
            fallback: 'index.html'
        })
    }
};

export default config;