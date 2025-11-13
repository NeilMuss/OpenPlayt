# Playt Concept  
A Hybrid Physical–Digital Music Format

Playt is a physical token that unlocks or contains a complete digital album environment.  
Each cartridge can store or reference audio, artwork, commentary, video, and interactive layers, while remaining a collectible physical object.  
Playt supports three paths: global releases, secure commercial releases, and local mixtapes.

---

## 1. Creation Phase

### 1.1 Mastering and Preparation
Artists finalize audio and metadata in standard formats (`.flac`, `.wav`, `metadata.json`).

### 1.2 Manifest and Playt Type
The authoring tool builds a manifest that defines the Playt’s behavior:

- `GLOBAL` — permanent, decentralized, open-access release  
- `SECURE` — authenticated, limited-use release  
- `LOCAL-MIX` — personal, device-local mixtape

The manifest is stored inside the `.playt` package and referenced by the cartridge.

### 1.3 Packaging
The Playt Builder tool assembles all content:

- GLOBAL: produces an unencrypted archive, pinned to IPFS/Arweave (CID returned).  
- SECURE: encrypts files and produces a contract-linked identifier.  
- LOCAL-MIX: creates a local folder; no network components required.

### 1.4 Writing to the Cartridge
The manufacturer or maker writes NFC data:

- GLOBAL: immutable CID  
- SECURE: contract address and token ID  
- LOCAL-MIX: UID and local flag  

An optional SD card may hold the full archive for offline-only scenarios.

---

## 2. Validation Phase

### 2.1 Cartridge Detection
Player reads the NFC chip and extracts type, UID, and header data.

### 2.2 Type Identification
Each cartridge encodes a simple prefix:

- `GLOB-`  
- `SECR-`  
- `MIX-`

### 2.3 Validation Logic
- GLOBAL: resolves content via IPFS/Arweave using CID.  
- SECURE: queries the smart contract to confirm allowed hardware IDs.  
- LOCAL-MIX: verifies that the cartridge’s UID is known to this device.

### 2.4 Confirmation
Once validated, the cartridge is bound to its corresponding content in the local archive registry.

---

## 3. Storage Phase

### 3.1 Caching and Import
- GLOBAL/SECURE: downloaded or decrypted files are cached locally.  
- LOCAL-MIX: the maker’s chosen folder becomes the album source.

### 3.2 Binding
The device stores a UID→folder mapping so the album can be played even when the cartridge is not present.

### 3.3 Backup (Optional)
GLOBAL and SECURE builds may optionally be mirrored to the user's personal decentralized vault.

---

## 4. Listening Phase

### 4.1 Direct Mode
Cartridge present; data is resolved and played from cache or network.

### 4.2 Walkman Mode
Cartridge absent; player uses local cache.

- GLOBAL: always allowed  
- SECURE: allowed based on token rules  
- LOCAL-MIX: allowed only on the device where the mix was created

### 4.3 Offline SD Mode
Content is read directly from the SD card embedded in the cartridge; no network required.

### 4.4 Revalidation (Secure Only)
Secure builds may require periodic contract checks to maintain playback rights.

---

## 5. Mixtape Flow

### 5.1 Blank Cartridge
Maker writes a `LOCAL-MIX` flag and UID to a blank NFC tag.

### 5.2 Mix Assembly
Maker chooses audio files and places them in a folder.

### 5.3 Linking
Playt OS binds that folder to the cartridge’s UID.

### 5.4 Gifting
Cartridge is passed to a friend; no cloud storage or identifier resolution involved.

### 5.5 Playback
Friend inserts cartridge; player recognizes the UID and plays the linked folder.

### 5.6 Duplication
Receivers may derive new mixes using UID lineage (optional).

---

## 6. Optional Layers

Playt supports a modular set of optional layers.  
Layers are defined in the manifest or inferred from folder structure.

### 6.1 Commentary
Artist-recorded spoken commentary or track-specific introductions.  
Located in `commentary/` or referenced in `manifest.yml`.

### 6.2 Introduction
A first-launch audiovisual intro.  
Configured with `intro.json` and supporting files.

### 6.3 Slideshow
A sequence of still images synchronized with tracks or independent playback.  
Provided through a `slideshow/` folder.

### 6.4 Video Interludes
Linked or standalone videos.  
Located in `video/` with optional `video_map.json`.

### 6.5 DJ Set or Continuous Mix
Alternate sequenced version of the album.  
Provided as `djmix.flac` or with cue metadata in `djmix.json`.

### 6.6 Generative Art
Processing sketches or lightweight real-time visual code in `processing/`.

### 6.7 Visualizer Theme
Custom motion-graphics themes controlled by `theme.json` or shader folders.

### 6.8 Liner Notes
Digital booklet or extended text in `notes/` or `booklet.pdf`.

### 6.9 Alternate Versions
Demos, remasters, stems, or bonus material in `alternate/`.

Playt is intentionally open-ended. New layer types can be added using the folder-based convention and a small manifest entry.

---

## 7. Example Lifecycles

### Example: Global Release
1. Artist uploads FLACs to IPFS and obtains a CID.  
2. CID written to NFC.  
3. User taps the cartridge; files are cached locally.  
4. Playback works with or without the cartridge present.

### Example: Secure Release
1. Artist encrypts archive and issues ownership token.  
2. Cartridge stores contract location and ID.  
3. Player checks ownership before granting playback.  
4. Cached playback allowed per contract rules.

### Example: Mixtape
1. Maker writes `LOCAL-MIX` flag and UID.  
2. Maker selects files and links them to the UID.  
3. Cartridge passed to friend.  
4. Playback works locally on recipient’s device without network access.

---

Playt is a new physical format designed with clear goals: permanence, freedom, collectibility, and artist agency.  
It treats music not as a subscription, but as a lasting, portable creation anchored by a physical artifact.
