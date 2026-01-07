import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// Import translations
import commonEn from './locales/en/common.json'
import commonRu from './locales/ru/common.json'
import navigationEn from './locales/en/navigation.json'
import navigationRu from './locales/ru/navigation.json'
import authEn from './locales/en/auth.json'
import authRu from './locales/ru/auth.json'
import eventsEn from './locales/en/events.json'
import eventsRu from './locales/ru/events.json'
import usersEn from './locales/en/users.json'
import usersRu from './locales/ru/users.json'
import ticketsEn from './locales/en/tickets.json'
import ticketsRu from './locales/ru/tickets.json'
import ordersEn from './locales/en/orders.json'
import ordersRu from './locales/ru/orders.json'
import supportEn from './locales/en/support.json'
import supportRu from './locales/ru/support.json'
import staffEn from './locales/en/staff.json'
import staffRu from './locales/ru/staff.json'
import musicEn from './locales/en/music.json'
import musicRu from './locales/ru/music.json'
import settingsEn from './locales/en/settings.json'
import settingsRu from './locales/ru/settings.json'
import qrScannerEn from './locales/en/qrScanner.json'
import qrScannerRu from './locales/ru/qrScanner.json'

const resources = {
  en: {
    common: commonEn,
    navigation: navigationEn,
    auth: authEn,
    events: eventsEn,
    users: usersEn,
    tickets: ticketsEn,
    orders: ordersEn,
    support: supportEn,
    staff: staffEn,
    music: musicEn,
    settings: settingsEn,
    qrScanner: qrScannerEn,
  },
  ru: {
    common: commonRu,
    navigation: navigationRu,
    auth: authRu,
    events: eventsRu,
    users: usersRu,
    tickets: ticketsRu,
    orders: ordersRu,
    support: supportRu,
    staff: staffRu,
    music: musicRu,
    settings: settingsRu,
    qrScanner: qrScannerRu,
  },
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'ru', // default language
    fallbackLng: 'ru',
    defaultNS: 'common',
    interpolation: {
      escapeValue: false, // React already handles escaping
    },
    react: {
      useSuspense: false,
    },
  })

export default i18n

