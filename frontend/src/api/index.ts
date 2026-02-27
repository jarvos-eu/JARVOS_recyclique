/**
 * API client — appels REST vers l’API RecyClique.
 * À implémenter dans les stories métier (auth, caisse, réception, admin).
 */
export { getCashRegistersStatus } from './caisse';
export type { CashRegisterStatusItem } from './caisse';
export { postPinUnlock } from './auth';
export type { UserInToken, PinLoginResponse } from './auth';
export {
  getSites,
  getCashRegisters,
  startCashRegister,
  openPosteReception,
  createSite,
  updateSite,
  deleteSite,
  createCashRegister,
  updateCashRegister,
  deleteCashRegister,
} from './admin';
export type { Site, CashRegister, PosteReceptionResponse } from './admin';
