import { createContext, useContext, useState, ReactNode } from 'react'

interface FilterPanelContextType {
  filterPanel: ReactNode | null
  setFilterPanel: (panel: ReactNode | null) => void
}

const FilterPanelContext = createContext<FilterPanelContextType | undefined>(undefined)

export const FilterPanelProvider = ({ children }: { children: ReactNode }) => {
  const [filterPanel, setFilterPanel] = useState<ReactNode | null>(null)

  return (
    <FilterPanelContext.Provider value={{ filterPanel, setFilterPanel }}>
      {children}
    </FilterPanelContext.Provider>
  )
}

export const useFilterPanel = () => {
  const context = useContext(FilterPanelContext)
  if (!context) {
    return { filterPanel: null, setFilterPanel: () => {} }
  }
  return context
}

