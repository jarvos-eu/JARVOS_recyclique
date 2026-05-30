import { useCallback, useState, type ReactNode } from 'react';
import { Button, Group, Paper, Stack, Text, Title } from '@mantine/core';
import type { ReceptionDraftSummary } from '../../api/shared-workstation-reception-draft-client';
import {
  abandonSharedWorkstationReceptionDraft,
  resumeSharedWorkstationReceptionDraft,
} from '../../api/shared-workstation-reception-draft-client';

export type SharedWorkstationReceptionDraftResumePanelProps = {
  readonly accessToken: string;
  readonly summary: ReceptionDraftSummary;
  readonly onResumed: (posteId: string, ticketId: string) => void;
  readonly onAbandoned: () => void;
};

function formatLocalTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

export function SharedWorkstationReceptionDraftResumePanel({
  accessToken,
  summary,
  onResumed,
  onAbandoned,
}: SharedWorkstationReceptionDraftResumePanelProps): ReactNode {
  const [busy, setBusy] = useState<'resume' | 'abandon' | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmAbandon, setConfirmAbandon] = useState(false);

  const onResume = useCallback(async () => {
    setError(null);
    setBusy('resume');
    try {
      const result = await resumeSharedWorkstationReceptionDraft(accessToken);
      if (!result.ok) {
        setError(result.message);
        return;
      }
      if (result.poste_id && result.ticket_id) {
        onResumed(result.poste_id, result.ticket_id);
      }
    } finally {
      setBusy(null);
    }
  }, [accessToken, onResumed]);

  const onAbandon = useCallback(async () => {
    if (!confirmAbandon) {
      setConfirmAbandon(true);
      return;
    }
    setError(null);
    setBusy('abandon');
    try {
      const result = await abandonSharedWorkstationReceptionDraft(accessToken);
      if (!result.ok) {
        setError(result.message);
        return;
      }
      onAbandoned();
    } finally {
      setBusy(null);
      setConfirmAbandon(false);
    }
  }, [accessToken, confirmAbandon, onAbandoned]);

  const timeLabel = formatLocalTime(summary.started_at);

  return (
    <Paper p="md" withBorder data-testid="shared-workstation-reception-draft-panel">
      <Stack gap="md">
        <Title order={4}>Reprise de session réception</Title>
        <Text size="sm">
          Brouillon commencé par {summary.started_by_display}
          {timeLabel ? ` à ${timeLabel}` : ''}
          {summary.line_count > 0 ? ` — ${summary.line_count} ligne(s)` : ''}.
        </Text>
        {error ? (
          <Text size="sm" c="red" role="alert">
            {error}
          </Text>
        ) : null}
        <Group>
          <Button
            data-testid="reception-draft-resume"
            onClick={() => void onResume()}
            loading={busy === 'resume'}
            disabled={busy !== null}
          >
            Reprendre
          </Button>
          <Button
            data-testid="reception-draft-abandon"
            variant="outline"
            color="red"
            onClick={() => void onAbandon()}
            loading={busy === 'abandon'}
            disabled={busy !== null}
          >
            {confirmAbandon ? 'Confirmer abandon' : 'Abandonner'}
          </Button>
        </Group>
      </Stack>
    </Paper>
  );
}
