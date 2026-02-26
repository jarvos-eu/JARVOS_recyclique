# BMAD Autopilot - Hook stop / subagentStop
# Appele depuis .cursor/hooks.json (chemins relatifs au fichier hooks.json).
# Usage: informatif uniquement - peut logger ou ecrire next-action.json pour un prochain demarrage.
param([string]$Event = "stop")

$artifactsPath = Join-Path $PSScriptRoot "..\..\_bmad-output\implementation-artifacts"
$sprintStatusPath = Join-Path $artifactsPath "sprint-status.yaml"
$nextActionPath = Join-Path $artifactsPath "next-action.json"

# Optionnel : ecrire un indicateur pour l'orchestrateur (next story, etc.)
# L'orchestrateur peut lire ce fichier au demarrage pour savoir quoi faire.
$payload = @{
    at = (Get-Date).ToString("o")
    event = $Event
    sprintStatusPath = $sprintStatusPath
} | ConvertTo-Json

try {
    $payload | Set-Content -Path $nextActionPath -Encoding UTF8
} catch {
    # Silencieux si echec (dossier absent, permissions)
}

exit 0
