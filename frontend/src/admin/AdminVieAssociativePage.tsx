/**
 * Page placeholder Vie associative — Story 8.7.
 * Écran Mantine avec titre et texte « Contenu vie associative à venir ».
 */
import React from 'react';
import { Stack, Title, Text } from '@mantine/core';

export function AdminVieAssociativePage() {
  return (
    <Stack gap="md" data-testid="page-vie-associative">
      <Title order={1}>Vie associative</Title>
      <Text>Contenu vie associative à venir.</Text>
    </Stack>
  );
}
