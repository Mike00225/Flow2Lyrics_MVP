
import re
import streamlit as st
from pronouncing import phones_for_word
from rapidfuzz.distance import Levenshtein

st.set_page_config(page_title="Flow2Lyrics AI", page_icon="🎵")
st.title("🎵 Flow2Lyrics AI")
st.caption("Prototype 0.1 • English • Exact Sound Match • text input")

LEXICON = """my little one|my little one
my only one|my only one
my lady now|my lady now
my love you know|my love you know
may lay your name|may lay your name
mama let me|mama let me
she might lead way|she might lead way
she might go away|she might go away
she made her way|she made her way
shine a light away|shine a light away
she my lady|she my lady
see my love wait|see my love wait
she might love me|she might love me
my lady oh no|my lady oh no
may leave your name|may leave your name
she made a way|she made a way
she might stay|she might stay
she my only one|she my only one
""".strip().splitlines()
PHRASES=[line.split("|")[0] for line in LEXICON]

# User-entered romanization has no single objectively correct pronunciation.
# This approximation is deliberately editable in the interface.
def approximate_phones(s):
    s=s.lower().replace("é","ay")
    replacements=[("shima","shee ma"),("lé","lay"),("yo","yo"),("ma ","mah ")]
    for a,b in replacements: s=s.replace(a,b)
    s=re.sub(r"[^a-z ]"," ",s)
    return s.split()

def word_phones(word):
    variants=phones_for_word(word.lower())
    if variants:
        return re.sub(r"\d","",variants[0]).split()
    return [word.lower()]

def candidate_phones(phrase):
    return [p for word in phrase.split() for p in word_phones(word)]

# Simplified phonetic encoding of the example. Replace with audio transcription
# and a phoneme recognizer for production-quality matching.
EXAMPLE_PHONES=[
    ["M","AA","L","EY","Y","OW","N","AH"],
    ["SH","IY","M","AH","L","EY","W","EY"]
]

def rank(phonemes, phrases, limit=8):
    source=" ".join(phonemes)
    scores=[]
    for p in phrases:
        target=" ".join(candidate_phones(p))
        dist=Levenshtein.normalized_distance(source,target)
        scores.append((1-dist,p))
    return sorted(scores,reverse=True)[:limit]

st.subheader("Your imaginary lyrics")
raw=st.text_area("Enter your sounds", "Ma lé yo na, shima lé way")
st.radio("Mode", ["Exact Sound Match"], horizontal=True)
st.selectbox("Language",["English"])
st.info("This MVP uses a manually approximated phoneme sequence for the supplied demo. It does not analyze recorded audio or an instrumental.")
with st.expander("Advanced: editable source phonemes"):
    a=st.text_input("Phrase 1 (ARPABET, separated by spaces)", " ".join(EXAMPLE_PHONES[0]))
    b=st.text_input("Phrase 2 (ARPABET, separated by spaces)", " ".join(EXAMPLE_PHONES[1]))
if st.button("Find closest-sounding lyrics", type="primary"):
    chunks=[x.strip() for x in raw.split(",") if x.strip()]
    for i,chunk in enumerate(chunks):
        st.markdown(f"**Original:** {chunk}")
        if i < 2:
            phones=(a if i==0 else b).upper().split()
            for score,phrase in rank(phones,PHRASES,5):
                st.write(f"{phrase} — prototype similarity {score:.0%}")
        else:
            st.warning("For additional phrases, add phoneme transcription support.")
st.caption("Scores compare phoneme-token sequences, not actual singing or audio similarity.")
