# Flow2Lyrics AI v0.3

Two paths: (1) upload a song already containing vocals and instrumental, or (2) upload an instrumental and record vocals in the browser.

A small Whisper speech-recognition model drafts English lyrics. Users correct the transcript, see words that aren't in the English pronunciation dictionary, and receive preliminary spelling-based replacement suggestions. **This is not yet acoustic phonetic matching**, and unknown dictionary words are not necessarily invented. Mixed audio is not separated into vocals and beat. Browser recording is not synchronized to the instrumental.

## Update existing Streamlit deployment
Replace root-level `app.py`, `requirements.txt`, and `README.md` in your existing GitHub repository. Commit changes and wait for Streamlit to rebuild. First transcription may download the model and take time. A free cloud instance may be slow or run out of memory.

## Local
```
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Next milestone
Separate vocals from instrumental, extract phonemes directly from vocals without forcing dictionary words, compare with candidates by acoustic/phonetic edit distance and syllable timing, and let users audition aligned suggestions.
