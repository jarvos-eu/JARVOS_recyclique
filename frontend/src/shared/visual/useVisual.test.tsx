/**
 * Tests useVisual — Story 10.1.
 */
import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DisplayServicesProvider } from '../display-services';
import { layoutConfigStub } from '../layout';
import { visualProviderStub } from './visual-provider.stub';
import { useVisual } from './useVisual';

function ShowVisual() {
  const provider = useVisual();
  const [result, setResult] = React.useState<{ url?: string; alt?: string } | null>(null);
  React.useEffect(() => {
    provider.getVisual({ slotId: 'test.slot' }).then(setResult);
  }, [provider]);
  if (!result) return <div data-testid="loading">Loading</div>;
  return (
    <div data-testid="visual-result">
      <span data-testid="has-url">{String(!!result.url)}</span>
      <span data-testid="alt">{result.alt ?? ''}</span>
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

describe('useVisual', () => {
  it('retourne un provider qui expose getVisual', async () => {
    renderWithProvider(<ShowVisual />);
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    const visualNode = await screen.findByTestId('visual-result');
    expect(visualNode).toBeInTheDocument();
    expect(screen.getByTestId('has-url')).toHaveTextContent('true');
    expect(screen.getByTestId('alt')).toHaveTextContent('Placeholder: test.slot');
  });

  it('getVisual résout vers un VisualResult avec url et alt', async () => {
    const provider = visualProviderStub;
    const result = await provider.getVisual({ slotId: 'header.logo' });
    expect(result).toHaveProperty('url');
    expect(result.url).toBeTruthy();
    expect(result.alt).toBe('Placeholder: header.logo');
  });
});
