// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // SPA mode — sem SSR para simplificar auth com sessionStorage
  ssr: false,

  // Habilita convenções do Nuxt 4 (srcDir = app/)
  future: {
    compatibilityVersion: 4,
  },

  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt'],

  runtimeConfig: {
    public: {
      apiBaseUrl: 'http://localhost:8000',
    },
  },

  app: {
    head: {
      title: 'Agenda Fácil',
      htmlAttrs: { lang: 'pt-BR' },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Sistema de agendamento de consultas médicas' },
      ],
      link: [
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com',
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.gstatic.com',
          crossorigin: '',
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
        },
      ],
    },
  },

  vite: {
    build: {
      cssMinify: false,
      minify: false,
    },
  },

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: '~/../tailwind.config.cjs',
  },

  typescript: {
    strict: true,
    typeCheck: false,
  },
})
