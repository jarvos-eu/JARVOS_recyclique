// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  addTicketLine,
  attachCashflowDraftSessionPersistence,
  CASHFLOW_DRAFT_SESSION_STORAGE_PREFIX,
  getCashflowDraftSnapshot,
  resetCashflowDraft,
} from '../../src/domains/cashflow/cashflow-draft-store';

describe('cashflow draft session persistence', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    sessionStorage.clear();
    resetCashflowDraft();
  });

  afterEach(() => {
    vi.useRealTimers();
    sessionStorage.clear();
    resetCashflowDraft();
  });

  it('persiste puis réhydrate le brouillon (simulation F5)', () => {
    const detach = attachCashflowDraftSessionPersistence('qa-user');

    addTicketLine({
      category: 'EEE-1',
      quantity: 1,
      weight: 1,
      unitPrice: 5,
      totalPrice: 5,
    });

    vi.advanceTimersByTime(400);
    detach();

    resetCashflowDraft(false);
    expect(getCashflowDraftSnapshot().lines.length).toBe(0);

    attachCashflowDraftSessionPersistence('qa-user');
    expect(getCashflowDraftSnapshot().lines.length).toBe(1);
    expect(getCashflowDraftSnapshot().lines[0]?.category).toBe('EEE-1');
  });

  it('reset puis réattach ne réhydrate pas un ticket fantôme (REV-02)', () => {
    const detach = attachCashflowDraftSessionPersistence('qa-user');
    addTicketLine({
      category: 'EEE-1',
      quantity: 1,
      weight: 1,
      unitPrice: 5,
      totalPrice: 5,
    });
    vi.advanceTimersByTime(400);
    detach();

    const key = `${CASHFLOW_DRAFT_SESSION_STORAGE_PREFIX}:qa-user`;
    expect(sessionStorage.getItem(key)).not.toBeNull();

    resetCashflowDraft();
    expect(getCashflowDraftSnapshot().lines.length).toBe(0);
    expect(JSON.parse(sessionStorage.getItem(key)!).lines).toEqual([]);

    attachCashflowDraftSessionPersistence('qa-user');
    expect(getCashflowDraftSnapshot().lines.length).toBe(0);
  });

  it('flush persist au detach si debounce en attente', () => {
    const detach = attachCashflowDraftSessionPersistence('qa-user');
    addTicketLine({
      category: 'EEE-2',
      quantity: 1,
      weight: 1,
      unitPrice: 3,
      totalPrice: 3,
    });
    detach();

    const key = `${CASHFLOW_DRAFT_SESSION_STORAGE_PREFIX}:qa-user`;
    const raw = sessionStorage.getItem(key);
    expect(raw).not.toBeNull();
    expect(JSON.parse(raw!).lines.length).toBe(1);
  });

  it('ne mélange pas deux utilisateurs sur la même origine sessionStorage', () => {
    const detachA = attachCashflowDraftSessionPersistence('user-a');
    addTicketLine({
      category: 'A',
      quantity: 1,
      weight: 1,
      unitPrice: 1,
      totalPrice: 1,
    });
    vi.advanceTimersByTime(400);
    detachA();

    resetCashflowDraft();
    attachCashflowDraftSessionPersistence('user-b');
    expect(getCashflowDraftSnapshot().lines.length).toBe(0);
  });
});
