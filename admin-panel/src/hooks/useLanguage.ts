import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { authService } from '../services/auth'
import api from '../services/api'

export const useLanguage = () => {
  const { i18n } = useTranslation()
  const [loading, setLoading] = useState(false)

  // Initialize language from user settings
  useEffect(() => {
    const initLanguage = async () => {
      try {
        const token = localStorage.getItem('token')
        if (token) {
          const adminInfo = await authService.getMe()
          if (adminInfo.language && adminInfo.language !== i18n.language) {
            await i18n.changeLanguage(adminInfo.language)
          }
        }
      } catch (error) {
        console.error('Failed to initialize language:', error)
      }
    }

    initLanguage()
  }, [i18n])

  const changeLanguage = async (newLanguage: string) => {
    setLoading(true)
    try {
      // Update language on backend
      await api.put('/admin/accounts/me/language', { language: newLanguage })
      
      // Update i18n language
      await i18n.changeLanguage(newLanguage)
      
      return { success: true }
    } catch (error) {
      console.error('Failed to change language:', error)
      return { success: false, error }
    } finally {
      setLoading(false)
    }
  }

  const toggleLanguage = async () => {
    const newLanguage = i18n.language === 'ru' ? 'en' : 'ru'
    return await changeLanguage(newLanguage)
  }

  return {
    currentLanguage: i18n.language,
    changeLanguage,
    toggleLanguage,
    loading,
  }
}

