# Flow2Lyrics AI v0.2

## What's new
- Record your voice using Streamlit's microphone control (`st.audio_input`).
- Upload WAV vocal files, listen back, and estimate duration / vocal activity.
- Upload and play an instrumental (MP3 or WAV).
- Match **manually entered ARPABET phonemes** against a small list of English phrases.

## Honest limitations
This is **not** yet an automatic phoneme recognizer. The audio is used for playback,
duration, and activity measurements. It does not drive the lyric suggestions.
The default phoneme sequences are rough interpretations of the demo.
Typed notes do not automatically convert to phonemes. No live synchronized recording
over a beat. The Meaningful Sound Match mode is a placeholder.

## Deploy to Streamlit Community Cloud
1. Extract this ZIP.
2. Open your existing Flow2Lyrics-AI GitHub repository.
3. Replace the root-level `app.py`, `requirements.txt`, and `README.md`
   with the corresponding files in this ZIP (commit the changes).
4. Your deployed Streamlit app should rebuild automatically. If not,
   use the Streamlit app management page to reboot/redeploy.
5. Open your app's HTTPS URL on Samsung Chrome and grant microphone permission.

## Local run
```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Next development milestone
Use a singing-capable phone/phoneme recognizer and a much larger candidate
generation index, then add onset and melody alignment.
