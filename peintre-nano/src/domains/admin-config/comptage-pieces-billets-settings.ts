export type ComptagePiecesBilletsSettings = {
  enabled: boolean;
  skipAllowed: boolean;
  requireDenominationGrid: boolean;
  showImages: boolean;
};

export const COMPTAGE_PIECES_BILLETS_DEFAULTS: ComptagePiecesBilletsSettings = {
  enabled: false,
  skipAllowed: true,
  requireDenominationGrid: false,
  showImages: true,
};

export type ComptagePiecesBilletsPayloadApi = {
  readonly enabled: boolean;
  readonly skip_allowed: boolean;
  readonly require_denomination_grid: boolean;
  readonly show_images: boolean;
};

export function comptagePayloadToSettings(payload: ComptagePiecesBilletsPayloadApi): ComptagePiecesBilletsSettings {
  return {
    enabled: payload.enabled,
    skipAllowed: payload.skip_allowed,
    requireDenominationGrid: payload.require_denomination_grid,
    showImages: payload.show_images,
  };
}

export function comptageSettingsToPayload(settings: ComptagePiecesBilletsSettings): ComptagePiecesBilletsPayloadApi {
  return {
    enabled: settings.enabled,
    skip_allowed: settings.skipAllowed,
    require_denomination_grid: settings.requireDenominationGrid,
    show_images: settings.showImages,
  };
}

export function mergeComptagePiecesBilletsSettings(
  base: ComptagePiecesBilletsSettings,
  partial: Partial<ComptagePiecesBilletsSettings>,
): ComptagePiecesBilletsSettings {
  return {
    enabled: partial.enabled ?? base.enabled,
    skipAllowed: partial.skipAllowed ?? base.skipAllowed,
    requireDenominationGrid: partial.requireDenominationGrid ?? base.requireDenominationGrid,
    showImages: partial.showImages ?? base.showImages,
  };
}

export const COMPTAGE_PIECES_BILLETS_SCHEMA_VERSION = '1.0.0' as const;
