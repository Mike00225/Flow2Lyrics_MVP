import io
import re
import numpy as np
import soundfile as sf
import streamlit as st
from rapidfuzz.distance import Levenshtein
import pronouncing

st.set_page_config(page_title="Flow2Lyrics AI 0.2", page_icon="🎤", layout="centered")
st.title("🎤 Flow2Lyrics AI")
st.caption("Version 0.2 • Record or upload vocals • English phonetic phrase matching")

PHRASES = [
    "my little one", "my only one", "my lady now", "my love you know",
    "may lay your name", "mama let me", "she might lead the way",
    "she might go away", "she made her way", "shine a light away",
    "she my lady", "see my love wait", "she might love me",
    "my lady oh no", "may leave your name", "she made a way",
    "she might stay", "she my only one", "she made me wait",
    "she may lead the way", "my lady wait", "my lady you know",
    "she may love you", "my love is on the way", "she might be away",
]
DEMO_PHONEMES = ["M AA L EY Y OW N AH", "SH IY M AH L EY W EY"]

def phones(phrase):
    out = []
    for word in phrase.lower().split():
        pronunciations = pronouncing.phones_for_word(re.sub(r"[^a-z']", "", word))
        if not pronunciations:
            return None
        out.extend(re.sub(r"\d", "", pronunciations[0]).split())
    return out

def rank(source, phrases, n=8):
    source_tokens = source.upper().strip().split()
    if not source_tokens:
        return []
    results = []
    for phrase in phrases:
        candidate = phones(phrase)
        if candidate is None:
            continue
        distance = Levenshtein.distance(source_tokens, candidate)
        similarity = 1 - distance / max(len(source_tokens), len(candidate), 1)
        results.append((similarity, phrase))
    return sorted(results, key=lambda row: (-row[0], row[1]))[:n]

def audio_features(upload):
    """Estimate duration, signal energy and rough vocal activity; not speech recognition."""
    upload.seek(0)
    data, sample_rate = sf.read(io.BytesIO(upload.read()), dtype="float32", always_2d=True)
    mono = data.mean(axis=1)
    if not len(mono):
        raise ValueError("Empty recording")
    duration = len(mono) / sample_rate
    rms = float(np.sqrt(np.mean(mono ** 2)))
    # Lightweight frame energy peaks are NOT a reliable count of syllables.
    frame = max(1, int(sample_rate * .04))
    levels = np.array([
        np.sqrt(np.mean(mono[i:i+frame] ** 2))
        for i in range(0, len(mono), frame)
    ])
    threshold = max(float(np.max(levels)) * .18, .005)
    active_seconds = float(np.sum(levels > threshold) * frame / sample_rate)
    return duration, rms, min(active_seconds, duration)

st.subheader("1. Optional instrumental")
beat = st.file_uploader("Upload an instrumental (MP3 or WAV)", type=["mp3", "wav"], key="beat")
if beat is not None:
    st.audio(beat)
    st.caption("Play the beat, then record your voice. This version does not synchronize the tracks.")

st.subheader("2. Record or upload your imaginary vocals")
st.write("On Samsung, allow microphone permission when Chrome asks.")
recording = st.audio_input("Record your invented sounds", key="voice")
vocal_upload = st.file_uploader("Or upload a WAV recording", type=["wav"], key="vocal")
vocal = recording if recording is not None else vocal_upload
if vocal is not None:
    st.audio(vocal)
    try:
        duration, energy, activity = audio_features(vocal)
        st.write(f"Recording duration: **{duration:.1f} seconds**")
        st.write(f"Estimated audible activity: **{activity:.1f} seconds**")
        st.caption("Audio analysis measures timing and energy only. It does NOT yet identify spoken or sung phonemes.")
    except Exception as exc:
        st.warning(f"Couldn't analyze the WAV recording: {exc}")

st.subheader("3. Guide the phonetic matcher")
st.info("Important: The audio is recorded and analyzed, but phoneme recognition is not yet automatic. Edit the phoneme strings below to match what you sang.")
imaginary = st.text_area("Optional written sound notes", "Ma lé yo na, shima lé way")
mode = st.radio("Matching mode", ["Exact Sound Match", "Meaningful Sound Match (coming later)"], index=0)
if mode != "Exact Sound Match":
    st.warning("Meaningful Sound Match is planned but not implemented.")
source_a = st.text_input("Sound segment 1 — ARPABET phonemes", DEMO_PHONEMES[0])
source_b = st.text_input("Sound segment 2 — ARPABET phonemes", DEMO_PHONEMES[1])
st.caption("The two default phoneme strings approximate the demo phrase. Typing different notes does not automatically update these strings.")

if st.button("Find closest-sounding English lyrics", type="primary"):
    for index, phoneme_string in enumerate([source_a, source_b], start=1):
        st.markdown(f"**Segment {index} suggestions**")
        for score, phrase in rank(phoneme_string, PHRASES):
            st.write(f"• {phrase} — phoneme similarity {score:.0%}")
    st.caption("Similarity is a phoneme edit-distance heuristic, not a confidence score or acoustic match.")

with st.expander("What works, and what is still missing?"):
    st.markdown("""
**Works:** Microphone recording in supported browsers, WAV upload and playback,
instrumental upload and playback, recording duration/activity estimates, manually guided English phoneme matching.

**Not yet implemented:** Automatic recognition of invented sung phonemes, recording over
synchronized beat playback, large-vocabulary lyric generation, melodic matching,
and meaningful lyric mode.

**Tip:** If recording does not work, ensure the deployed site uses HTTPS and allow
Chrome microphone permissions.
""")
