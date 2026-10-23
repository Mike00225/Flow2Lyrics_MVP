import io, re, tempfile, os
from pathlib import Path
import streamlit as st
import pronouncing
from rapidfuzz.distance import Levenshtein

st.set_page_config(page_title='Flow2Lyrics AI v0.3',page_icon='🎵')
st.title('🎵 Flow2Lyrics AI')
st.caption('Version 0.3 · English · Existing-song or record-new workflow')

WORDS = set(w.lower() for w in pronouncing.cmudict.words())
# Words outside this lexicon are only flagged as 'unrecognized', never definitively nonsense.
PHRASES = ['my little one','my only one','my lady now','my love you know','my lady you know',
 'she made her way','she might go away','she might lead the way','she may lead the way',
 'she made a way','she might stay','she might love me','she my lady',
 'my love is on the way','shine a light away','my lady wait','my love you know',
 'may lay your name','she made me wait','she might be away','she may love you']

def phonemes(word):
    p=pronouncing.phones_for_word(word.lower())
    return re.sub(r'\d','',p[0]).split() if p else []

def similar(word, n=8):
    # Approximate orthographic fallback for unknown words: not an acoustic/phonetic match.
    candidates = sorted(WORDS)
    # Avoid scanning full dictionary repeatedly by using short, similarly sized candidates.
    candidates = [w for w in candidates if w.isalpha() and abs(len(w)-len(word))<=2 and w[:1]==word[:1]]
    scored = [(Levenshtein.normalized_similarity(word.lower(), w), w) for w in candidates]
    return sorted(scored, reverse=True)[:n]

def transcript_tokens(text):
    return re.findall(r"[A-Za-zÀ-ÿ]+(?:'[A-Za-z]+)?|[^\w\s]+",text)

@st.cache_resource(show_spinner='Loading English speech model (first run may take a few minutes)…')
def model():
    from faster_whisper import WhisperModel
    return WhisperModel('tiny.en', device='cpu', compute_type='int8')

def transcribe(upload):
    suffix=Path(upload.name).suffix.lower() if hasattr(upload,'name') else '.wav'
    with tempfile.NamedTemporaryFile(suffix=suffix,delete=False) as f:
        f.write(upload.getvalue())
        filename=f.name
    try:
        segments, info=model().transcribe(filename,language='en',beam_size=3,word_timestamps=True,
                                           vad_filter=False)
        segments=list(segments)
        text=' '.join(s.text.strip() for s in segments)
        timed=[]
        for s in segments:
            for w in (s.words or []):
                timed.append((w.word.strip(),round(w.start,2),round(w.end,2),round(w.probability,2)))
        return text,timed
    finally:
        os.unlink(filename)

path=st.radio('How would you like to start?', ['I already recorded my song with the instrumental',
                                             'I only have an instrumental and want to record'],index=0)
if path.startswith('I already'):
    st.subheader('1. Upload your existing song')
    recording=st.file_uploader('Song with vocals and instrumental (MP3, WAV, M4A)',type=['mp3','wav','m4a'])
    if recording: st.audio(recording)
    st.warning('A mixed song is harder to transcribe than isolated vocals. This prototype does not separate vocals from the beat; results may be inaccurate.')
else:
    st.subheader('1. Upload your instrumental')
    beat=st.file_uploader('Instrumental (MP3 or WAV)',type=['mp3','wav'])
    if beat: st.audio(beat)
    st.subheader('2. Record imaginary vocals')
    recording=st.audio_input('Tap to record your singing')
    if recording: st.audio(recording)
    st.info('Play the beat and record vocals. Browser microphone capture is not synchronized with beat playback in this version; headphones and a second device may help.')

st.subheader('Transcribe and correct your lyrics')
if 'pending_lyrics' in st.session_state:
    st.session_state.lyrics = st.session_state.pop('pending_lyrics')
if 'lyrics' not in st.session_state: st.session_state.lyrics='Ma lé yo na, shima lé way'
if 'timed' not in st.session_state: st.session_state.timed=[]
if recording and st.button('Analyze recording',type='primary'):
    try:
        with st.spinner('Transcribing audio…'):
            txt,timed=transcribe(recording)
        st.session_state.lyrics=txt
        st.session_state.timed=timed
        st.success('Draft transcription ready. Review and correct invented sounds below.')
    except Exception as exc:
        st.error(f'Could not transcribe this recording: {exc}')

lyrics=st.text_area('Editable transcription — preserve invented syllables as you heard them',key='lyrics',height=130)
st.caption('Speech recognition may invent ordinary English words for nonsense sounds. Please correct the draft before matching.')
if st.session_state.timed:
    with st.expander('Approximate word timing and model confidence'):
        st.dataframe([{'word':w,'start (s)':s,'end (s)':e,'model confidence':p} for w,s,e,p in st.session_state.timed],hide_index=True)

st.subheader('Identify unfamiliar words')
tokens=transcript_tokens(lyrics)
unknown=list(dict.fromkeys(t for t in tokens if re.fullmatch(r"[A-Za-zÀ-ÿ]+(?:'[A-Za-z]+)?",t) and t.lower() not in WORDS))
known=list(dict.fromkeys(t for t in tokens if t.lower() in WORDS))
st.write('**Recognized dictionary words:** '+(', '.join(known) if known else 'None found'))
st.write('**Not found in English pronunciation dictionary:** '+(', '.join(unknown) if unknown else 'None found'))
st.caption('Unrecognized does not mean nonexistent: names, slang, other languages and mis-transcriptions may be flagged.')

st.subheader('Find sound-preserving replacements')
if unknown:
    target=st.selectbox('Select a word to replace',unknown)
else:
    target=st.text_input('Enter an invented word or sound to replace','shima')
st.info('Unknown words have no reliable dictionary phonemes. Suggestions below use spelling similarity as a rough fallback, NOT a verified sound match.')
if st.button('Suggest replacements') and target.strip():
    st.session_state['suggestions']=similar(target.strip())
    st.session_state['target']=target.strip()
if st.session_state.get('suggestions') and st.session_state.get('target')==target.strip():
    for score,word in st.session_state['suggestions']:
        st.write(f'{word} — approximate spelling score {score:.0%}')
    replacement=st.text_input('Choose or type replacement')
    if st.button('Replace selected word') and replacement:
        st.session_state.pending_lyrics=re.sub(r'\b'+re.escape(target)+r'\b',replacement,st.session_state.lyrics,count=1,flags=re.I)
        st.rerun()

with st.expander('Current limitations and next milestones'):
    st.markdown('''- Uses a **tiny English Whisper model** to draft a transcript. Accuracy on music and invented sounds is limited.
- Does **not** perform vocal separation, phoneme recognition of nonsense sounds, beat alignment, or melodic preservation.
- Unknown-word detection uses a dictionary, so it can miss invented words that Whisper replaces with known ones.
- Replacement suggestions for unknown words use **spelling similarity**, not true sound similarity.
- Next: source separation, acoustic phoneme recognition, phoneme-distance search, and syllable/duration alignment.''')
