import { Alert, List, Text } from '@mantine/core';
import type { ReactNode } from 'react';

const RULES = [
  'Comptez tout le tiroir, fond compris',
  'Saisissez des quantités, jamais des montants',
  'Le total de la grille fait foi',
  'Commentez tout écart ou coupure rare',
] as const;

/** Story 9.12 — 4 règles terrain visibles en permanence sur le panel grille (Perplexity §D). */
export function CashflowDenominationRulesBanner(): ReactNode {
  return (
    <Alert color="blue" variant="light" data-testid="cashflow-denomination-rules">
      <Text size="sm" fw={600} mb={4}>
        Règles de comptage
      </Text>
      <List size="sm" spacing={2}>
        {RULES.map((rule) => (
          <List.Item key={rule}>{rule}</List.Item>
        ))}
      </List>
    </Alert>
  );
}
