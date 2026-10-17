# TTS and application audio

Use the exact model's [Qwen3-TTS documentation](https://github.com/QwenLM/Qwen3-TTS). CustomVoice, Base and VoiceDesign checkpoints have different capabilities; a feature in the family overview may not apply to the 0.6B variant. Record language, speaker/voice, model revision and generation settings. Do not promise a benchmark latency on the user's device.

Preserve generated sample rate/encoding, check output duration and listen to a representative clip. Test punctuation, numbers, abbreviations and sentence boundaries. Do not autoplay private answers or start a microphone from a background workflow without the application's intended user action.

For Expo apps follow the installed SDK's [expo-audio](https://docs.expo.dev/versions/latest/sdk/audio/) API, microphone permission flow, audio-session configuration and cleanup. Cache recordings may be evicted; persistent user-approved recordings require an explicit storage/retention policy. A server-side WAV test is not mobile playback verification.

Include permission denial, interruption, headset disconnection, cancellation, app restart and stale-result cases. Distinguish unit/fixture checks, actual model inference and actual device playback. This skill supplies workflow instructions, not an installed audio runtime or a recording service.
