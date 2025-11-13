# OpenPlayt

**OpenPlayt** is an open-source standard and player design for physical–digital music releases. It combines collectible, NFC-encoded “Playt” cartridges with open audio formats and optional local storage to give artists and listeners a permanent, tangible way to exchange and archive music.

---
<img width="350" alt="playt-render-002" src="https://github.com/user-attachments/assets/c3ae868f-69ad-4ebd-90ac-b132ef939f62" />

## Overview

The Playt system reimagines the album as a hybrid physical–digital artifact.  
Each cartridge contains a readable ID (via NFC or QR) linking to audio data stored either on a decentralized network or on the listener’s local device.  
When inserted into a Playt-compatible player, the cartridge activates playback and metadata display without the need for accounts, ads, or intermediaries.

Playts can be:

- **Commercial releases** — linked to permanent decentralized storage (e.g. IPFS/Arweave).
- **Personal mixtapes** — locally authored cartridges with private, offline playback.

---

## Goals

- Preserve music ownership in an open, artist-controlled format.  
- Support both online and fully offline playback.  
- Encourage collectible and expressive physical design.  
- Maintain interoperability with standard audio formats (FLAC, WAV, MP3).  
- Provide simple tools for encoding, authoring, and playback.

---

## Components

| Component | Function |
|------------|-----------|
| **Playt Cartridge** | Physical token with label art, NFC chip, and optional SD slot. |
| **OpenPlayt Player** | Reference hardware using a Raspberry Pi and NFC reader. |
| **.playt Format** | Metadata structure defining album identity, media source, and playback rules. |
| **Authoring Tools** | Scripts for generating cartridges and managing music archives. |

---

## Getting Started

1. Clone this repository.  
   ```bash
   git clone https://github.com/NeilMuss/OpenPlayt.git
   cd OpenPlayt
