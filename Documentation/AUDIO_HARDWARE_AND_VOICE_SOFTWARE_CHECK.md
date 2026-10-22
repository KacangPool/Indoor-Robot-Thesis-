# Audio hardware and copied voice software

## Current evidence boundary

The copied workspace contains `xf_mic_asr_offline`, an offline voice-command package apparently intended for a WHEELTEC-compatible USB/HID microphone array. This proves that optional voice software was copied; it does **not** prove that this robot has a microphone or speaker installed.

The 2026-09-10 terminal report now shows a PulseAudio capture source named `alsa_input.usb-ORBBEC_ASTRA_S-01.analog-stereo`, using signed 16-bit stereo at 48 kHz. This confirms that Ubuntu exposes an audio-input endpoint associated with the Astra S. It is strong evidence for an available camera audio interface, but a short recording/playback test is still required to prove that a physical microphone captures intelligible sound. `SUSPENDED` means the source was idle at that moment, not necessarily faulty.

The package contains a Chinese wake word and fixed Chinese command phrases for forward/backward motion, turning, stopping, navigation points, LiDAR following, colour following, mapping, and navigation. This is command recognition, not general rescue-sound recognition such as detecting cries, screams, knocking, breathing, or calls for help.

## Safe hardware identification

With the robot stationary, run:

```bash
lsusb
arecord -l
aplay -l
pactl list short sources 2>/dev/null
```

Save or photograph the complete output. `arecord -l` lists ALSA recording devices; `aplay -l` lists playback devices. `pactl` may be absent on the older Ubuntu installation. A readable label on the microphone unit remains stronger identity evidence than a generic USB-audio name.

Use a lowercase letter **L** in `arecord -l` and `aplay -l`. The earlier report used the number `1`, so ALSA rejected those two commands.

If a capture device appears, make a short ordinary audio test only after substituting the actual card/device from `arecord -l`:

```bash
mkdir -p ~/thesis_audio_test
cd ~/thesis_audio_test
arecord -D plughw:CARD=ACTUAL_CARD,DEV=ACTUAL_DEVICE -f S16_LE -r 16000 -c 1 -d 5 mic_test.wav
aplay mic_test.wav
```

Do not literally enter `ACTUAL_CARD` or `ACTUAL_DEVICE`; replace them with the reported values. If the device is only exposed through the package's custom HID interface, it may not appear as a normal ALSA recorder.

## ROS package check

```bash
rospack find xf_mic_asr_offline
```

Finding the package still does not confirm the hardware. The package's `mic_init.launch` appears limited to microphone/recognizer initialization, whereas its `base.launch` includes the physical base, LiDAR, localization/navigation, and motion-command nodes.

**Do not run `roslaunch xf_mic_asr_offline base.launch` merely to test audio.** It is motion-capable. The legacy recognizer may also depend on a particular array, bundled resources, and old credentials/licensing.

## Thesis relevance

Audio could be a separate future sensor experiment, but it is not a substitute for the required RGB detector. Before adding it, confirm the hardware, define the sound classes, collect or license an appropriate audio dataset, evaluate false alarms from motors/room noise, and justify the extra thesis scope. For now, record it as an unconfirmed optional capability.
