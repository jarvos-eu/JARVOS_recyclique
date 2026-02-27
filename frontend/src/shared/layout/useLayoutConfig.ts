/**
 * Hook pour accéder au LayoutConfigService injecté (interface uniquement, pas d'import stub).
 */
import { useDisplayServices } from '../display-services';

export function useLayoutConfig() {
  const { layoutConfigService } = useDisplayServices();
  return layoutConfigService;
}
