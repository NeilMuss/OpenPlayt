# Playt Physical Format Specification

This document defines the physical form of a Playt—the object the listener holds, displays, and taps to the player.

---

## 1. Overview

A Playt is a thin square cartridge with:
- A 2.5" × 2.5" front art area  
- A wraparound **2.5" × 5"** label (front → spine → back)  
- An NFC tag on the back  
- An optional SD card slot at the bottom  

The format emphasizes tactility, collectability, and simple manufacturability.

---

## 2. Dimensions

### **2.1 Core Dimensions**
- **Width:** 70 mm  
- **Height:** 70 mm  
- **Depth (including spine):** **5.08 mm** (0.2" spine)  
- Material wall thickness: 1–1.5 mm recommended  

These revised dimensions make the Playt more compact and elegant while keeping enough spine width for the wraparound label.

---

## 2.2 Art Areas

Because the Playt body is 70 mm × 70 mm:

#### **Front art panel**
- **63.5 mm × 63.5 mm** (2.5")
- **Border:** ~3 mm on each side

This border produces a comfortable frame while ensuring 2.5" labels center cleanly.

#### **Back art panel**
- Also supports **63.5 mm height**  
- Width ≈ **(70 mm – 5 mm spine – 3 mm border × 2)**  
  → ~ **58–59 mm usable width**

#### **Spine**
- **5 mm** (0.2")  
- Label covers full spine height (63.5 mm)  
- Optional text or color coding

---

## 2.3 Label

Standard label size: **2.5" × 5"** (63.5 mm × 127 mm)

Wrap path:
- **Front:** 63.5 mm  
- **Spine:** 5 mm  
- **Back:** Remaining ≈ 58.4 mm  

This matches well with the revised 70 × 70 mm body.

---

## 3. Materials

### **3.1 Body**
Recommended:
- Translucent polypropylene  
- PETG  
- ABS  
- Acrylic (with rounded corners)

Colors often used:
- Indigo (semi-transparent)
- Smoke  
- Frosted  
- Clear  

### **3.2 Label Stock**
- Vinyl or matte paper  
- Can be printed at home or ordered in bulk  
- Die-cut optional but unnecessary  

---

## 4. NFC Integration

### **4.1 Tag Type**
- NTAG215 or NTAG216  
- Memory: enough for UUID + reference data  
- Format: NDEF  
- Placement: Back, lower third  
- Use standard NFC sticker rolls  

### **4.2 Purpose**
The NFC tag provides:
- A unique Playt ID  
- Optional lightweight metadata  

It does *not* store the audio itself.

---

## 5. Optional SD Slot

### **Purpose**
Allows:
- Offline commercial releases  
- Mix tapes  
- Hi-res audio  
- Additional content layers beyond NFC  

### **Slot Specification**
- MicroSD card  
- Bottom insertion  
- Width opening ≈ **15 mm**  
- Height opening ≈ **1.2 mm**  
- Insertion depth ≈ **12 mm**  
- Spring-loaded or friction-fit  

Not required for all Playts.

---

## 6. Manufacturing Notes

- Corner radius: 2–3 mm recommended  
- Assembly via ultrasonic weld, snap-fit, or solvent bonding  
- NFC should sit under ≤1.5 mm material for reliable reading  
- Label alignment should visually center the front 2.5" square  

---

## 7. Aesthetic Guidelines

- Front remains art-dominant  
- Back can contain tracklists or minimal branding  
- NFC area may be subtly indicated or left blank  
- Spine text optional but helpful for collectors  

---

## 8. Durability

A Playt should withstand:
- NFC tapping  
- Pocket transport  
- Label reapplication  
- Humidity variation  

Expected lifespan: **20+ years** with normal use.

---
