# Flow2Lyrics AI — MVP 0.1

A runnable English phonetic phrase-ranking demo. This is NOT yet audio-aware.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture
Input text or audio -> phoneme recognition / editable phoneme transcription -> candidate phrase generation -> phoneme edit-distance ranking -> lyrics editor.

Current MVP implements **editable demo phonemes**, a small candidate phrase dictionary, CMUdict English word pronunciations via `pronouncing`, and normalized Levenshtein distance via `rapidfuzz`.

## Limitations
- The default phonemes are a rough subjective interpretation of the example, not an automatic transcription of the text box.
- Only the first two comma-separated phrases are ranked, using the two editable phoneme inputs.
- No beat detection, melody analysis, audio upload, phoneme recognition, large phrase search, or language model yet.
- Prototype similarity is a normalized edit-distance heuristic, not calibrated acoustic confidence.

## Next steps
1. Add mic/file input and a phoneme recognizer, with manual correction.
2. Build candidate phrases from a large licensed English lexicon and beam search.
3. Rank with phonetic feature-aware alignment, vowel duration and stress.
4. Add beat/onset alignment and user auditioning.
5. Add the Meaningful Sound Match mode as a separate reranker.
