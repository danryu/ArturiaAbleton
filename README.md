# Arturia KeyLab 88 & Ableton Live: Custom Control Surface & Template Guide

## 1. Executive Summary

This setup integrates the **Arturia KeyLab 88 (mk1)** with **Ableton Live 12** and the **Arturia Analog Lab Pro** plugin.

### Key Operational Goals Achieved
* **Bank 1 (Dedicated Plugin Mode)**: Encoders (P1–P10) and Faders (F1–F9) pass through 100% cleanly to the armed track for **Analog Lab Pro**, without Ableton hijacking faders for track volumes.
* **Bank 2 (Ableton Mixer & Device Mode)**: 
  * Encoders P1–P4 and P6–P9 control Ableton Device Macros (1–8, "Blue Hand") in standard Absolute mode (0–127).
  * Encoder P5 controls **Track Selection Scroll** in Relative mode (endless scrolling without clamping at `Value 00`).
  * Encoder P10 controls **Selected Track Pan** in Relative mode (smooth, pickup-free panning).
  * Faders F1–F8 control Track Volumes 1–8; Fader F9 controls Master Volume.
* **Encoder Switches 1–10**: Repurposed from unused snapshot buttons into immediate DAW navigation, device control, and track controls (Device Left/Right, Device On/Off, Device Lock, Metronome, Track Activate, Track Solo, Scene Up/Down, Scene Launch).
* **Transport Controls**: Restored full transport functionality for native KeyLab MMC SysEx commands (Play, Stop, Rewind, Fast Forward), CC 55 for Loop, and re-routed Record to trigger **Session Record**.
* **Search / Preset Browsing**: Resolved the hardware CC 114 conflict between Category and Preset knobs, and enabled firmware `Knob Fix` to eliminate relative encoder lockup.

---

## 2. Hardware Mapping Reference

### 2.1 Rotary Encoders (P1–P10)

| Hardware | Physical Label | Bank 1 (Analog Lab Pro) | Bank 2 (Ableton Live) | Mode (AbletonFix) |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | L1 / Cutoff | CC 74 (Cutoff) | Macro 1 (Blue Hand) | Absolute (0–127) |
| **P2** | L2 / Resonance | CC 71 (Resonance) | Macro 2 (Blue Hand) | Absolute (0–127) |
| **P3** | L3 / LFO Rate | CC 76 (LFO Rate) | Macro 3 (Blue Hand) | Absolute (0–127) |
| **P4** | L4 / LFO Amt | CC 77 (LFO Amt) | Macro 4 (Blue Hand) | Absolute (0–127) |
| **P5** | L5 / Chorus | CC 18 (Chorus) | **Track Select Scroll** | **Relative 1** (Binary Offset) |
| **P6** | R1 / Param 1 | CC 19 (Param 1) | Macro 5 (Blue Hand) | Absolute (0–127) |
| **P7** | R2 / Param 2 | CC 16 (Param 2) | Macro 6 (Blue Hand) | Absolute (0–127) |
| **P8** | R3 / Param 3 | CC 17 (Param 3) | Macro 7 (Blue Hand) | Absolute (0–127) |
| **P9** | R4 / Param 4 | CC 93 (Param 4) | Macro 8 (Blue Hand) | Absolute (0–127) |
| **P10** | R5 / Delay | CC 91 (Delay) | **Selected Track Pan** | **Relative 1** (Binary Offset) |

* **Bank 1 Pass-Through**: Omitted from `KeyLab88Custom.py` control surface registry so Ableton never intercepts Bank 1 messages; they pass directly to the armed track for Analog Lab Pro.
* **Bank 2 P5 (Track Scroll)**: Set to `Relative 1` in MCC and `relative_smooth_binary_offset` in Python. Clockwise moves to next track (+1); counter-clockwise moves to previous track (-1). Does not clamp at `00` or `127`.
* **Bank 2 P10 (Track Pan)**: Adjusts pan on the currently selected track smoothly without parameter jumps when changing tracks.

---

### 2.2 Faders (F1–F9)

| Hardware | Physical Label | Bank 1 (Analog Lab Pro) | Bank 2 (Ableton Live) | Mode |
| :--- | :--- | :--- | :--- | :--- |
| **F1** | Fader 1 / Attack 1 | CC 73 | Track 1 Volume | Absolute (0–127) |
| **F2** | Fader 2 / Decay 1 | CC 75 | Track 2 Volume | Absolute (0–127) |
| **F3** | Fader 3 / Sustain 1 | CC 79 | Track 3 Volume | Absolute (0–127) |
| **F4** | Fader 4 / Release 1 | CC 72 | Track 4 Volume | Absolute (0–127) |
| **F5** | Fader 5 / Attack 2 | CC 80 | Track 5 Volume | Absolute (0–127) |
| **F6** | Fader 6 / Decay 2 | CC 81 | Track 6 Volume | Absolute (0–127) |
| **F7** | Fader 7 / Sustain 2 | CC 82 | Track 7 Volume | Absolute (0–127) |
| **F8** | Fader 8 / Release 2 | CC 83 | Track 8 Volume | Absolute (0–127) |
| **F9** | Master / Master Vol | CC 85 | **Master Track Volume** | Absolute (0–127) |

---

### 2.3 Encoder Switches 1–10 (Tactile Push Buttons Below Knobs)

| Switch # | Hardware | MIDI CC | Assigned Function | Description |
| :---: | :---: | :---: | :--- | :--- |
| **1** | Snap 1 | CC 22 | **Device Left** | Select previous device/plugin on active track |
| **2** | Snap 2 | CC 23 | **Device Right** | Select next device/plugin on active track |
| **3** | Snap 3 | CC 24 | **Device On/Off** | Toggle bypass / active state of selected device |
| **4** | Snap 4 | CC 25 | **Device Lock** | Lock / unlock "Blue Hand" to active device |
| **5** | Snap 5 | CC 26 | **Metronome** | Toggle Ableton Metronome (click track) on / off |
| **6** | Snap 6 | CC 27 | **Track Activate** | Toggle Mute / Unmute (Speaker icon) on active track |
| **7** | Snap 7 | CC 28 | **Track Solo** | Toggle Solo (Blue **S** icon) on active track |
| **8** | Snap 8 | CC 29 | **Scene Up** | Move Session scene selection Up |
| **9** | Snap 9 | CC 30 | **Scene Down** | Move Session scene selection Down |
| **10** | Snap 10 | CC 31 | **Scene Launch** | Launch currently selected Scene |

*Dynamic Tracking*: Switches 6 and 7 automatically apply to whichever track is currently highlighted in Ableton (whether selected with mouse or scrolled via knob P5).

---

### 2.4 Transport Controls

| Button | KeyLab Output Format | Python Script Action | Target Function |
| :--- | :--- | :--- | :--- |
| **Play** | MMC SysEx (`cmd = 0x02` / `0x03`) | `song.is_playing = True` | Play / Resume playback |
| **Stop** | MMC SysEx (`cmd = 0x01`) | `song.is_playing = False` / rewind | 1st press: Pause; 2nd press: Rewind to 1.1.1 |
| **Record** | MMC SysEx (`cmd = 0x06`) & CC 90 | `_session_recording._on_record_button_value(127)` | **Session Record** (punch clips in Session View) |
| **Rewind** | MMC SysEx (`cmd = 0x05`) | `song.current_song_time -= 4.0` | Jump backward 1 bar |
| **Fast Fwd** | MMC SysEx (`cmd = 0x04`) | `song.current_song_time += 4.0` | Jump forward 1 bar |
| **Loop** | MIDI CC 55 | `TransportComponent.set_loop_button` | Toggle Arrangement Loop on / off |

---

### 2.5 Sound Browsing Controls

| Knob / Button | MIDI CC | Mode | Description |
| :--- | :--- | :--- | :--- |
| **Category Search** | **CC 112** (reassigned from 114) | Relative 1 | Scroll instrument categories |
| **Preset Search** | **CC 114** | Relative 1 | Scroll individual presets |

---

## 3. Template Difference: `AbletonFix` vs Factory Default

The following table documents every parameter modification made to create the user template **`AbletonFix`** (`AbletonFix.keylab88`) compared to Arturia's factory default template (`Factory Default`):

| Parameter / Key | Hardware Control | Factory Default | `AbletonFix` Template | Technical Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **`49_3`** | Category Search CC | `114` | **`112`** | **Resolves CC Collision**: In factory firmware, both Category Search and Preset Search transmit on CC 114, making independent category filtering impossible. Moving Category Search to CC 112 isolates the two encoders. |
| **`13_64`** | Global Knob Fix | `0` (or `1` in older MCC) | **`127` (ON)** | **Fixes Relative Encoder Bug**: Enables KeyLab's internal relative value filter, fixing the issue where relative encoders would stop transmitting after a single tick or jump erratically. |
| **`41_6`** | Bank 2 P5 Mode | `0` (Absolute) | **`1` (Relative 1)** | **Infinite Track Navigation**: In Absolute mode (0–127), scrolling left hits CC value `00` and locks up. Relative 1 (Binary Offset) transmits continuous relative step increments (+1 / -1) with no boundaries. |
| **`42_6`** | Bank 2 P10 Mode | `0` (Absolute) | **`1` (Relative 1)** | **Pickup-Free Track Pan**: Allows endless, jump-free panning on the selected track without value jumps when switching between tracks with different pan settings. |

### Preserved Factory Parameters
All other parameters remain set to standard factory defaults:
* **Bank 1 Knobs P1–P10**: Absolute mode, CCs `74, 71, 76, 77, 18, 19, 16, 17, 93, 91` on Channel 1 (Ch 0 internally).
* **Bank 1 Faders F1–F9**: Absolute mode, CCs `73, 75, 79, 72, 80, 81, 82, 83, 85` on Channel 1.
* **Bank 2 Knobs P1–P4 & P6–P9**: Absolute mode, CCs `35, 36, 37, 38, 40, 41, 42, 43` on Channel 1.
* **Bank 2 Faders F1–F9**: Absolute mode, CCs `67, 68, 69, 70, 87, 88, 89, 90, 92` on Channel 1.
* **Switches 1–10**: Gate mode, CCs `22–31` on Channel 1.
* **Drum Pads 1–16**: Note messages on MIDI Channel 10 (Ch 9 internally), notes `36–51`.

---

## 4. File Locations & Installation

### Script Installation Path
```text
/Users/dan/Music/Ableton/User Library/Remote Scripts/KeyLab_88_Custom/
├── __init__.py
├── KeyLab88Custom.py
└── KeyLab88Custom.py.working_backup
```

### Template File Path
```text
/Users/dan/Documents/AbletonFix.keylab88
```
Also available in the repository at:
```text
~/code/ArturiaAbleton/templates/AbletonFix.keylab88
~/code/ArturiaAbleton/AbletonFix.keylab88
```

---

## 5. Ableton Live Configuration Guide

1. Open **Ableton Live 12**.
2. Open **Settings / Preferences** (`Cmd + ,`) and navigate to **Link, Tempo & MIDI**.
3. Under **MIDI Control Surfaces**:
   * **Control Surface**: Select `KeyLab_88_Custom`.
   * **Input**: Select `KeyLab 88`.
   * **Output**: Select `KeyLab 88`.
4. Under **MIDI Ports**:
   * `Input: KeyLab 88`: Ensure **Track = ON** (to play instruments) and **Remote = ON** (to receive control surface CCs).
   * `Output: KeyLab 88`: Set **Remote = ON** (for control feedback).
5. **Reloading After Updates**:
   To force Ableton to reload the script without restarting:
   * Set the Control Surface dropdown from `KeyLab_88_Custom` to `None`.
   * Switch it back to `KeyLab_88_Custom`.
