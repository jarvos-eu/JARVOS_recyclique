import { useSyncExternalStore } from 'react';

let posteOpened = false;
const listeners = new Set<() => void>();

function emit(): void {
  listeners.forEach((listener) => listener());
}

export function subscribeReceptionPosteUiState(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function getReceptionPosteUiStateSnapshot(): boolean {
  return posteOpened;
}

export function setReceptionPosteUiState(next: boolean): void {
  if (posteOpened === next) return;
  posteOpened = next;
  emit();
}

/** Story 27.8 — réinitialiser l’indicateur UI non autoritaire au verrouillage poste partagé. */
export function resetReceptionPosteUiState(): void {
  setReceptionPosteUiState(false);
}

export function useReceptionPosteUiState(): boolean {
  return useSyncExternalStore(
    subscribeReceptionPosteUiState,
    getReceptionPosteUiStateSnapshot,
    getReceptionPosteUiStateSnapshot,
  );
}
