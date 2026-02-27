/**
 * Context d'injection pour LayoutConfigService et VisualProvider (v1 stubs, v2+ réels).
 * Les composants consomment via useLayoutConfig() / useVisual() uniquement.
 */
import React, { createContext, useContext } from 'react';
import type { LayoutConfigService } from '../layout';
import type { VisualProvider } from '../visual';

export interface DisplayServicesValue {
  layoutConfigService: LayoutConfigService;
  visualProvider: VisualProvider;
}

const DisplayServicesContext = createContext<DisplayServicesValue | null>(null);

export interface DisplayServicesProviderProps {
  layoutConfigService: LayoutConfigService;
  visualProvider: VisualProvider;
  children: React.ReactNode;
}

export function DisplayServicesProvider({
  layoutConfigService,
  visualProvider,
  children,
}: DisplayServicesProviderProps) {
  const value: DisplayServicesValue = { layoutConfigService, visualProvider };
  return (
    <DisplayServicesContext.Provider value={value}>
      {children}
    </DisplayServicesContext.Provider>
  );
}

export function useDisplayServices(): DisplayServicesValue {
  const ctx = useContext(DisplayServicesContext);
  if (!ctx) {
    throw new Error('useDisplayServices must be used within DisplayServicesProvider');
  }
  return ctx;
}
