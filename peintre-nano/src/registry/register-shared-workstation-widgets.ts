import { registerWidget } from './widget-registry';
import { SharedWorkstationEnrollmentWidget } from '../domains/shared-workstation/SharedWorkstationEnrollmentWidget';

/** Epic 27.4 — enrôlement terrain poste partagé (`/shared-workstation/enroll`). */
export function registerSharedWorkstationWidgets(): void {
  registerWidget('shared-workstation.enrollment', SharedWorkstationEnrollmentWidget);
}
