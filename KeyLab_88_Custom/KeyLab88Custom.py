from __future__ import absolute_import, print_function, unicode_literals
import Live
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.Layer import Layer
import KeyLab.KeyLab as KeyLab_Module
from KeyLab.KeyLab import (
    BUTTON_HARDWARE_AND_MESSAGE_IDS,
    PAD_CHANNEL,
    get_button_identifier_by_name,
)
from KeyLab_88.KeyLab88 import KeyLab88

# Bank 2 MIDI CC numbers from Arturia KeyLab 88 factory defaults:
# Encoders 1-8: Device Parameter controls (Macros 1-8 in Ableton)
# Encoder 9: Horizontal scroll (Track select)
# Encoder 10: Vertical scroll (Scene select)
BANK2_ENCODER_MSG_IDS = (35, 36, 37, 38, 40, 41, 42, 43, 39, 44)

# Sliders 1-8: Volume controls for Ableton tracks 1-8
# Slider 9: Master Track Volume
BANK2_SLIDER_MSG_IDS = (67, 68, 69, 70, 87, 88, 89, 90, 92)


class KeyLab88Custom(KeyLab88):
    """
    Custom KeyLab 88 Control Surface script:
    - BANK 1 (Knobs CC 74, 71... and Faders CC 73, 75, 79...):
      NOT registered in this script at all. Zero elements exist in self.controls
      for Bank 1, guaranteeing that Ableton never intercepts Bank 1 messages
      and passes 100% of them through to the armed track directly for Analog Lab Pro.
    - BANK 2 (Knobs CC 35..44 and Faders CC 67..92):
      Mapped to Ableton Device macros (Blue Hand), track volumes (1-8), master volume,
      track select scroll (P5), and selected track pan (P10).
    - ENCODER SWITCHES 1-10:
      Switches 1 & 2: Device Previous / Next
      Switch 3: Device On/Off toggle
      Switch 4: Device Lock toggle
      Switch 5: Metronome toggle
      Switch 6: Track Activate (Mute) toggle for selected track
      Switch 7: Track Solo toggle for selected track
      Switches 8 & 9: Scene Up / Down navigation
      Switch 10: Scene Launch
    - TRANSPORT CONTROLS:
      Play, Stop, Rewind, Fast Forward, Loop (CC 55),
      and Record configured for Session Record (instead of Arrangement Record).
    - ZERO intrusive hardware SysEx:
      Does not overwrite working memory on startup.
    """

    def _create_controls(self):
        encoder_channel = getattr(KeyLab_Module, 'ENCODER_CHANNEL', 0)

        # 1. Device encoders (Bank 2 Encoders 1-8) in standard ABSOLUTE mode (0-127)
        self._device_encoders = ButtonMatrixElement(rows=[
            [
                EncoderElement(
                    MIDI_CC_TYPE,
                    encoder_channel,
                    identifier,
                    Live.MidiMap.MapMode.absolute,
                    name=('Device_Encoder_%d_%d' % (col_index, row_index))
                )
                for col_index, identifier in enumerate(row)
            ]
            for row_index, row in enumerate((
                BANK2_ENCODER_MSG_IDS[:4],
                BANK2_ENCODER_MSG_IDS[4:8]
            ))
        ])

        # 2. Scroll encoder (Bank 2 P5) for track navigation in Relative mode
        self._horizontal_scroll_encoder = EncoderElement(
            MIDI_CC_TYPE,
            encoder_channel,
            BANK2_ENCODER_MSG_IDS[-2],
            Live.MidiMap.MapMode.relative_smooth_binary_offset,
            name='Horizontal_Scroll_Encoder'
        )

        # 2b. Track Pan encoder (Bank 2 P10, CC 44) for selected track pan in Relative mode
        self._track_pan_encoder = EncoderElement(
            MIDI_CC_TYPE,
            encoder_channel,
            BANK2_ENCODER_MSG_IDS[-1],
            Live.MidiMap.MapMode.relative_smooth_binary_offset,
            name='Track_Pan_Encoder'
        )
        self._vertical_scroll_encoder = self._track_pan_encoder

        # 3. Volume sliders (Bank 2 Sliders 1-8)
        self._volume_sliders = ButtonMatrixElement(rows=[
            [
                SliderElement(MIDI_CC_TYPE, encoder_channel, identifier)
                for identifier in BANK2_SLIDER_MSG_IDS[:-1]
            ]
        ])

        # 4. Master slider (Bank 2 Slider 9)
        self._master_slider = SliderElement(
            MIDI_CC_TYPE,
            encoder_channel,
            BANK2_SLIDER_MSG_IDS[-1]
        )

        # 5. Buttons (Transport, navigation, scene)
        def make_keylab_button(name):
            return ButtonElement(
                True,
                MIDI_CC_TYPE,
                0,
                get_button_identifier_by_name(name),
                name=name.title()
            )

        for button_name in BUTTON_HARDWARE_AND_MESSAGE_IDS.keys():
            setattr(self, '_' + button_name, make_keylab_button(button_name))

        # 5b. Encoder Switches 3-7 (Custom mapped functions)
        # Switch 3 (CC 24): Device On/Off toggle
        self._device_on_off_button = ButtonElement(
            True, MIDI_CC_TYPE, 0, 24, name='Device_On_Off_Button'
        )
        # Switch 4 (CC 25): Device Lock toggle
        self._device_lock_button = ButtonElement(
            True, MIDI_CC_TYPE, 0, 25, name='Device_Lock_Button'
        )
        # Switch 5 (CC 26): Metronome toggle
        self._metronome_button = ButtonElement(
            True, MIDI_CC_TYPE, 0, 26, name='Metronome_Button'
        )
        # Switch 6 (CC 27): Track Activate (Mute) toggle for selected track
        self._track_activate_button = ButtonElement(
            True, MIDI_CC_TYPE, 0, 27, name='Track_Activate_Button'
        )
        # Switch 7 (CC 28): Track Solo toggle for selected track
        self._track_solo_button = ButtonElement(
            True, MIDI_CC_TYPE, 0, 28, name='Track_Solo_Button'
        )

        # 6. Drum pads (4x4 matrix on PAD_CHANNEL)
        pad_channel = getattr(KeyLab_Module, 'PAD_CHANNEL', 9)
        self._pads = ButtonMatrixElement(rows=[
            [
                ButtonElement(
                    True,
                    MIDI_CC_TYPE,
                    pad_channel,
                    col_index + row_offset,
                    name=('Pad_%d_%d' % (col_index, row_index))
                )
                for col_index in range(4)
            ]
            for row_index, row_offset in enumerate(range(48, 35, -4))
        ])

    def _create_device(self):
        super(KeyLab88Custom, self)._create_device()
        self._device.layer = Layer(
            parameter_controls=self._device_encoders,
            on_off_button=self._device_on_off_button,
            lock_button=self._device_lock_button,
        )

    def _create_transport(self):
        super(KeyLab88Custom, self)._create_transport()
        # Exclude self._record_button so transport does not trigger arrangement record.
        self._transport.layer = Layer(
            play_button=self._play_button,
            stop_button=self._stop_button,
            loop_button=self._loop_button,
            metronome_button=self._metronome_button,
        )

    def _create_session(self):
        super(KeyLab88Custom, self)._create_session()
        # Switches 8 & 9 handle scene navigation; disconnect encoder so P10 is free for Pan.
        if hasattr(self._session, 'set_scene_select_control'):
            self._session.set_scene_select_control(None)

    def _create_session_recording(self):
        super(KeyLab88Custom, self)._create_session_recording()
        # Bind the hardware Record button (CC 90) to Session Record
        self._session_recording.layer = Layer(record_button=self._record_button)

    def _create_mixer(self):
        super(KeyLab88Custom, self)._create_mixer()
        self._mixer.selected_strip().layer = Layer(
            pan_control=self._track_pan_encoder,
            mute_button=self._track_activate_button,
            solo_button=self._track_solo_button,
        )
        self._mixer.selected_strip().set_invert_mute_feedback(True)

    def _collect_setup_messages(self):
        # Do NOT send hardware-overwriting SysEx setup messages.
        # Leaving the KeyLab's working memory untouched prevents RAM corruption
        # and lets the KeyLab rely on its own stored preset.
        pass

    def handle_sysex(self, midi_bytes):
        # Handle MIDI Machine Control (MMC) transport messages from KeyLab 88:
        # Format: (0xF0, 0x7F, <device_id>, 0x06, <command>, 0xF7)
        if len(midi_bytes) == 6 and midi_bytes[0] == 240 and midi_bytes[1] == 127 and midi_bytes[3] == 6 and midi_bytes[5] == 247:
            cmd = midi_bytes[4]
            song = self.song()
            if cmd == 1:  # MMC Stop
                if song.is_playing:
                    song.is_playing = False
                else:
                    song.current_song_time = 0.0
                return
            elif cmd in (2, 3):  # MMC Play / Deferred Play
                song.is_playing = True
                return
            elif cmd == 6:  # MMC Record -> Session Record
                try:
                    if hasattr(self, '_session_recording') and self._session_recording is not None:
                        self._session_recording._on_record_button_value(127)
                    else:
                        song.session_record = not song.session_record
                except Exception:
                    song.session_record = not song.session_record
                return
            elif cmd == 4:  # MMC Fast Forward (jump forward 1 bar)
                song.current_song_time = song.current_song_time + 4.0
                return
            elif cmd == 5:  # MMC Rewind (jump backward 1 bar)
                song.current_song_time = max(0.0, song.current_song_time - 4.0)
                return
            elif cmd == 9:  # MMC Pause
                song.is_playing = not song.is_playing
                return

        super(KeyLab88Custom, self).handle_sysex(midi_bytes)
