import { de } from './de.js';
import { en } from './en.js';

const dictionaries = { de, en };

const browserLang = navigator.language.split('-')[0]; // "de-DE" -> "de"
const currentLocale = dictionaries[browserLang] ? browserLang : 'en';
const currentDictionary = dictionaries[currentLocale];

export const i18n = {
  get locale() {
    return currentLocale;
  },

  t(path, params = {}) {
    let text = path.split('.').reduce((obj, key) => obj?.[key], currentDictionary);
    
    if (typeof text !== 'string') return path;

    Object.keys(params).forEach(key => {
      text = text.replaceAll(`{${key}}`, params[key]);
    });

    return text;
  }
};
