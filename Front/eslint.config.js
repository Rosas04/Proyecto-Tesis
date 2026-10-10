import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    rules: {
      // Reglas de optimización del React Compiler: señalan patrones de carga
      // inicial en efectos (setState al montar, funciones declaradas después
      // del efecto) que no producen errores en tiempo de ejecución. Se dejan
      // como advertencia hasta refactorizar esas páginas.
      'react-hooks/set-state-in-effect': 'warn',
      'react-hooks/immutability': 'warn',
      // Los contextos exportan su hook junto al Provider (patrón estándar).
      'react-refresh/only-export-components': 'warn',
    },
  },
])
