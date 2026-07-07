# Guide d'installation kDrive Desktop en mode headless sur VPS Linux

**Date :** 2026-07-07  
**Statut :** chantier à part · **pas encore déployé**  
**Nature :** runbook infra VPS — accès fichiers La Clique (K-Drive kSuite gratuit) pour agents / scripts

**Liens :**

- Bot Discord pilote (accès doc futur, mode AIDE) : [`2026-07-05_02_cadrage-bot-discord-la-clique-pilote.md`](2026-07-05_02_cadrage-bot-discord-la-clique-pilote.md) · kanban [`IDEA-2026-07-05-002`](../../docs/ideas/kanban/IDEA-2026-07-05-002.md)
- Chantier politique documentaire : [`2026-02-25_02_chantier-fichiers-politique-documentaire.md`](2026-02-25_02_chantier-fichiers-politique-documentaire.md)
- Référence VPS Ombre (même hôte cible) : [`2026-07-07_02_reference-sdk-cursor-local-vps-architecte-ombre.md`](2026-07-07_02_reference-sdk-cursor-local-vps-architecte-ombre.md)

Destiné aux agents de développement (Cursor, Hermes, scripts d'automatisation). Contexte : **Jarvos.eu** — clone local K-Drive sur le VPS pour lecture/écriture via système de fichiers (plan gratuit, sans API REST ni WebDAV).

---

## 0. Contexte et contraintes

- Compte kDrive : **kSuite gratuit / my kSuite** (pas de plan payant).
- L'API REST Infomaniak Developer Portal **n'est PAS accessible** sur ce plan (nécessite kDrive payant, ~5€/mois).
- Le protocole **WebDAV est INDISPONIBLE** sur kSuite gratuit (confirmé officiellement par Infomaniak).
- Solution retenue : **l'application desktop kDrive officielle** (AppImage Linux), qui utilise le protocole de synchronisation propriétaire d'Infomaniak (distinct de l'API développeur et de WebDAV) et reste disponible sur tous les plans, y compris gratuits.
- Objectif final : obtenir un dossier local sur le VPS, synchronisé en bidirectionnel avec le kDrive, exploitable par des scripts Python/Node.js comme un système de fichiers classique (list, read, mkdir, move, copy).

---

## 1. Prérequis système

```bash
# Vérifier la distribution (Ubuntu/Debian recommandé)
cat /etc/os-release

# Dépendances système nécessaires pour faire tourner un AppImage Qt en headless
sudo apt update
sudo apt install -y libfuse2 xvfb x11-utils libxcb-cursor0 \
  libxcb-xinerama0 libxkbcommon-x11-0 libgl1 libegl1 \
  libnss3 libxcomposite1 libxrandr2 libxdamage1 libxfixes3 \
  libasound2 wget
```

Notes :
- `libfuse2` est requis pour exécuter tout AppImage.
- Le client desktop kDrive est une application Qt avec interface graphique. Sur un VPS sans serveur X, il faut soit :
  - a) un **serveur X virtuel** (`Xvfb`) pour lui donner un écran factice, soit
  - b) forcer le mode plateforme **offscreen/xcb** via une variable d'environnement (`QT_QPA_PLATFORM`).
- L'option (b) est plus légère et recommandée pour un usage 100% automatisé sans besoin d'interagir avec l'UI après la configuration initiale.

---

## 2. Téléchargement du client kDrive

```bash
mkdir -p ~/apps/kdrive
cd ~/apps/kdrive

# Récupérer la dernière version depuis les releases GitHub officielles
# (vérifier la version la plus récente sur https://github.com/Infomaniak/desktop-kDrive/releases)
wget https://download.storage.infomaniak.com/kdrive-desktop/kDrive-latest-x86_64.AppImage -O kDrive.AppImage

chmod +x kDrive.AppImage
```

> Astuce agent : script un check de version automatique en parsant l'API GitHub releases :
> `curl -s https://api.github.com/repos/Infomaniak/desktop-kDrive/releases/latest | jq -r '.tag_name'`

---

## 3. Première configuration (nécessite une session graphique une seule fois)

L'authentification OAuth de première connexion nécessite un navigateur. Deux approches possibles :

### Option A — Configuration via Xvfb + VNC (recommandé pour setup initial)

```bash
sudo apt install -y tigervnc-standalone-server

# Démarrer un display virtuel
Xvfb :1 -screen 0 1280x800x24 &
export DISPLAY=:1

# Lancer l'app dans ce display
./kDrive.AppImage &

# Exposer le display via VNC pour se connecter depuis son poste local
x11vnc -display :1 -passwd VOTRE_MDP_TEMPORAIRE -forever &
```

Puis depuis ta machine locale (Windows/macOS), ouvrir un tunnel SSH et se connecter en VNC :

```bash
ssh -L 5900:localhost:5900 user@votre-vps
# Se connecter avec un client VNC (ex: RealVNC, TigerVNC Viewer) sur localhost:5900
```

Dans l'interface kDrive qui apparaît : se connecter avec le compte Infomaniak, choisir le dossier kDrive à synchroniser, valider le chemin local (ex: `/home/jarvos/kdrive-sync`).

### Option B — Mode offscreen (si l'authentification par token est possible sans navigateur)

```bash
export QT_QPA_PLATFORM=offscreen
./kDrive.AppImage
```

> Limitation connue : certains flux OAuth Infomaniak nécessitent l'ouverture d'un navigateur web pour valider la connexion. Dans ce cas, Option A (VNC) reste indispensable pour le setup initial. Une fois la configuration sauvegardée dans `~/.config/kDrive/`, les lancements suivants n'ont plus besoin d'interaction graphique.

---

## 4. Lancement automatique en tant que service systemd (mode daemon, sans UI)

Une fois la première synchronisation configurée, créer un service systemd pour que le client tourne en permanence en arrière-plan.

```bash
sudo nano /etc/systemd/system/kdrive-sync.service
```

Contenu :

```ini
[Unit]
Description=kDrive Desktop Sync Client (headless)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=jarvos
Environment=QT_QPA_PLATFORM=offscreen
Environment=HOME=/home/jarvos
ExecStart=/home/jarvos/apps/kdrive/kDrive.AppImage
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
```

Activation :

```bash
sudo systemctl daemon-reload
sudo systemctl enable kdrive-sync
sudo systemctl start kdrive-sync
sudo systemctl status kdrive-sync
```

Vérification de la synchronisation :

```bash
ls -la /home/jarvos/kdrive-sync
journalctl -u kdrive-sync -f
```

---

## 5. Interfaçage avec les agents / scripts (Python)

Une fois le dossier synchronisé actif, il se comporte comme un dossier local classique. Aucun appel API n'est nécessaire.

### 5.1 Lister les documents

```python
import os

KDRIVE_ROOT = "/home/jarvos/kdrive-sync"

def list_documents(subpath=""):
    target = os.path.join(KDRIVE_ROOT, subpath)
    return [
        {"name": f, "path": os.path.join(target, f), "is_dir": os.path.isdir(os.path.join(target, f))}
        for f in os.listdir(target)
    ]

print(list_documents("Documents/Projets"))
```

### 5.2 Lire le contenu d'un document

```python
def read_document(relative_path):
    full_path = os.path.join(KDRIVE_ROOT, relative_path)
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

content = read_document("Documents/Projets/notes.md")
```

Pour les formats binaires (PDF, DOCX), utiliser des libs dédiées :

```python
# PDF
from pypdf import PdfReader
reader = PdfReader(os.path.join(KDRIVE_ROOT, "Documents/rapport.pdf"))
text = "\n".join(page.extract_text() for page in reader.pages)

# DOCX
from docx import Document
doc = Document(os.path.join(KDRIVE_ROOT, "Documents/compte-rendu.docx"))
text = "\n".join(p.text for p in doc.paragraphs)
```

### 5.3 Créer un nouveau dossier et réorganiser

```python
import shutil

def create_folder(relative_path):
    full_path = os.path.join(KDRIVE_ROOT, relative_path)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def move_document(src_relative, dst_relative):
    src = os.path.join(KDRIVE_ROOT, src_relative)
    dst = os.path.join(KDRIVE_ROOT, dst_relative)
    shutil.move(src, dst)

def copy_document(src_relative, dst_relative):
    src = os.path.join(KDRIVE_ROOT, src_relative)
    dst = os.path.join(KDRIVE_ROOT, dst_relative)
    shutil.copy2(src, dst)

# Exemple : nouvelle organisation par année
create_folder("Documents/Archives/2026")
move_document("Documents/Projets/notes.md", "Documents/Archives/2026/notes.md")
```

> Important : toute modification faite dans ce dossier local est automatiquement propagée vers le kDrive cloud par le service systemd en arrière-plan (synchronisation bidirectionnelle). Pas besoin d'appel API supplémentaire — c'est le client desktop qui gère l'upload/download en tâche de fond.

---

## 6. Watcher temps réel (optionnel, pour agents événementiels)

Pour déclencher des actions d'agent dès qu'un fichier change sur le kDrive (upload externe, modification via l'app mobile, etc.), utiliser `watchdog` :

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class KDriveEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"Nouveau fichier détecté : {event.src_path}")
        # -> déclencher un agent, un pipeline de classement, etc.

    def on_modified(self, event):
        print(f"Fichier modifié : {event.src_path}")

observer = Observer()
observer.schedule(KDriveEventHandler(), KDRIVE_ROOT, recursive=True)
observer.start()
```

---

## 7. Points de vigilance pour les agents

- **Latence de sync** : la synchronisation n'est pas instantanée (quelques secondes à ~1 minute selon la taille et le nombre de fichiers). Prévoir un court délai ou un mécanisme de retry après une écriture avant de considérer le fichier comme propagé côté cloud.
- **Conflits d'édition** : si un fichier est modifié simultanément côté cloud (via navigateur) et côté VPS, le client kDrive crée généralement une copie de conflit (`nom (conflit).ext`) — prévoir une détection de ce pattern dans les scripts de nettoyage automatique.
- **Quota gratuit** : le plan gratuit kSuite est limité en espace de stockage (généralement 15 Go) — surveiller l'espace disponible avant des opérations de copie massive.
- **Redémarrage du service** : en cas de désynchronisation prolongée (`journalctl -u kdrive-sync` montrant des erreurs répétées), un simple `systemctl restart kdrive-sync` résout la majorité des cas.
- **Sécurité** : le dossier `/home/jarvos/kdrive-sync` contient une copie complète et en clair des documents — s'assurer que les permissions Unix (`chmod 700`) restreignent l'accès au seul utilisateur de service.
- **Pas d'API REST disponible** : ne pas tenter d'appeler `api.infomaniak.com/2/drive/...` avec ce compte, cela renverra une erreur 403 (plan insuffisant). Toute interaction doit passer par le système de fichiers local synchronisé.

---

## 8. Alternative si le VPS ne peut pas exécuter d'application Qt/AppImage

Si l'environnement VPS est trop restreint (conteneur minimal, pas de libs graphiques), deux pistes de secours :

1. **Upgrade vers kDrive payant** (~5€/mois) pour débloquer l'API REST officielle et/ou WebDAV — solution la plus robuste et "propre" pour un usage agent intensif, sans dépendance à un client desktop.
2. **Machine relais** : faire tourner le client kDrive desktop sur une machine locale (ou un petit VPS dédié avec libs graphiques), puis exposer ce dossier synchronisé au VPS principal via un partage réseau (SSHFS, NFS, Syncthing) — ajoute une couche de complexité mais évite l'upgrade payant.
