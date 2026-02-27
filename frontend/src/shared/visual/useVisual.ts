/**
 * Hook pour accéder au VisualProvider injecté (interface uniquement, pas d'import stub).
 */
import { useDisplayServices } from '../display-services';

export function useVisual() {
  const { visualProvider } = useDisplayServices();
  return visualProvider;
}
