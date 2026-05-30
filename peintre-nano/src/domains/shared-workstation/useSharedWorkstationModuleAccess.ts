import { useSharedWorkstationEffectiveModules } from './SharedWorkstationEffectiveModulesProvider';

export type SharedWorkstationModuleAccess = {
  readonly effectiveModuleKeys: readonly string[];
  readonly loading: boolean;
  readonly isModuleEffective: (moduleKey: string) => boolean;
};

/** Hook projection modules effectifs poste partagé (Story 27.7). */
export function useSharedWorkstationModuleAccess(): SharedWorkstationModuleAccess {
  const { effectiveModuleKeys, loading } = useSharedWorkstationEffectiveModules();
  return {
    effectiveModuleKeys,
    loading,
    isModuleEffective: (moduleKey: string) => effectiveModuleKeys.includes(moduleKey),
  };
}
