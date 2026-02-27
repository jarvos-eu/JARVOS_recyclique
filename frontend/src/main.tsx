/**
 * Point d'entrée React — Story 3.5.
 * Monte AuthProvider, CaisseProvider, puis App (Router + Guard + Nav + routes).
 * Mantine (Story 6.1 review) : styles + MantineProvider.
 */
import '@mantine/core/styles.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import { AuthProvider } from './auth/AuthContext';
import { CaisseProvider } from './caisse';
import { App } from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MantineProvider>
      <AuthProvider>
        <CaisseProvider>
          <App />
        </CaisseProvider>
      </AuthProvider>
    </MantineProvider>
  </React.StrictMode>
);
