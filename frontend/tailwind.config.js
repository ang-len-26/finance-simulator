import { hover } from 'framer-motion';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        /* Botones-sidebar */
        'btn-sidebar': {
          default: 'var(--color-btn-sidebar-default)',
          hover: 'var(--color-btn-sidebar-hover)',
          active: 'var(--color-btn-sidebar-activate)',
          disabled: 'var(--color-btn-sidebar-disable)',
        },
        'btn-sidebar-text': {
          default: 'var(--color-btn-text-sidebar-default)',
          hover: 'var(--color-btn-text-sidebar-hover)',
          active: 'var(--color-btn-text-sidebar-activate)',
          disabled: 'var(--color-btn-text-sidebar-disable)',
        },
        /* Botones-navbar */
        'btn-navbar': {
          default: 'var(--color-btn-navbar-default)',
          hover: 'var(--color-btn-navbar-hover)',
          active: 'var(--color-btn-navbar-activate)',
          disabled: 'var(--color-btn-navbar-disable)',
        },
        'btn-navbar-text': {
          default: 'var(--color-btn-text-navbar-default)',
          hover: 'var(--color-btn-text-navbar-hover)',
          active: 'var(--color-btn-text-navbar-activate)',
          disabled: 'var(--color-btn-text-navbar-disable)',
        },
        /* Botones-principal */
        'btn-primary': {
          default: 'var(--color-btn-primary-default)',
          hover: 'var(--color-btn-primary-hover)',
          active: 'var(--color-btn-primary-activate)',
          disabled: 'var(--color-btn-primary-disable)',
        },
        'btn-primary-text': {
          default: 'var(--color-btn-text-primary-default)',
          disabled: 'var(--color-btn-text-primary-disable)',
        },
        /* Botones-secundario */
        'btn-secondary': {
          default: 'var(--color-btn-secondary-default)',
          hover: 'var(--color-btn-secondary-hover)',
          active: 'var(--color-btn-secondary-activate)',
          disabled: 'var(--color-btn-secondary-disable)',
        },
        'btn-secondary-text': {
          default: 'var(--color-btn-text-secondary-default)',
          disabled: 'var(--color-btn-text-secondary-disable)',
        },
        /* Estados */
        'state-success': 'var(--color-state-success)',
        'state-error': 'var(--color-state-error)',
        'state-alert': 'var(--color-state-alert)',
        /* Texto */
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        'text-secondary-hover':'var(--color-text-secondary-hover)',
        'text-secondary-disabled':'var(--color-text-secondary-disabled)',
        'text-secondary-error':'var(--color-text-secondary-error)',
        'text-secondary-alert':'var(--color-text-secondary-alert)',
        'text-footer': 'var(--color-text-footer)',
        /*background*/
        'bg-main': 'var(--color-bg-main)',
        'bg-secondary': 'var(--color-bg-secondary)',
        'bg-tertiary': 'var(--color-bg-tertiary)',
        'bg-card': 'var(--color-bg-card)',
        'bg-main-disabled': 'var(--color-bg-main-disabled)',
        'bg-secondary-disabled': 'var(--color-bg-secondary-disabled)',
        'bg-tertiary-disabled': 'var(--color-bg-tertiary-disabled)',
        /*bordes*/
        'border': 'var(--color-border)',
        'border-hover': 'var(--color-border-hover)',
        'border-focus': 'var(--color-border-focus)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'sm': '0 1px 2px 0 var(--color-shadow)',
        'md': '0 4px 6px -1px var(--color-shadow)',
        'lg': '0 8px 15px -3px var(--color-shadow)',
      },
      animation: {
        'slide-in': 'slideIn 0.2s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}