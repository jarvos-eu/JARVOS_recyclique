/**
 * Tests useLayoutConfig — Story 10.1.
 */
import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DisplayServicesProvider } from '../display-services';
import { layoutConfigStub } from './layout-config.stub';
import { visualProviderStub } from '../visual';
import { useLayoutConfig } from './useLayoutConfig';

function ShowLayoutConfig() {
  const service = useLayoutConfig();
  const [config, setConfig] = React.useState<unknown>(null);
  React.useEffect(() => {
    service.getLayout().then(setConfig);
  }, [service]);
  if (!config) return <div data-testid="loading">Loading</div>;
  return (
    <div data-testid="layout-config">
      <span data-testid="has-layout">{String(Array.isArray((config as { layout?: unknown }).layout))}</span>
      <span data-testid="has-breakpoints">{String(!!(config as { breakpoints?: unknown }).breakpoints)}</span>
    </div>
  );
}

function renderWithProvider(ui: React.ReactElement) {
  return render(
    <DisplayServicesProvider
      layoutConfigService={layoutConfigStub}
      visualProvider={visualProviderStub}
    >
      {ui}
    </DisplayServicesProvider>
  );
}

describe('useLayoutConfig', () => {
  it('retourne un service qui expose getLayout', async () => {
    renderWithProvider(<ShowLayoutConfig />);
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    const layoutNode = await screen.findByTestId('layout-config');
    expect(layoutNode).toBeInTheDocument();
    expect(screen.getByTestId('has-layout')).toHaveTextContent('true');
    expect(screen.getByTestId('has-breakpoints')).toHaveTextContent('true');
  });

  it('getLayout résout vers un LayoutConfig avec layout et breakpoints', async () => {
    const service = layoutConfigStub;
    const config = await service.getLayout();
    expect(config).toHaveProperty('layout');
    expect(config).toHaveProperty('breakpoints');
    expect(Array.isArray(config.layout)).toBe(true);
    expect(config.breakpoints).toEqual(expect.objectContaining({ lg: 1200, md: 996, sm: 768 }));
  });
});
