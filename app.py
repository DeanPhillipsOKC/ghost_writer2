import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from ghost_writer.contracts import StoryBible
from ghost_writer.planners.bible_planner import generate_story_bible
import json

load_dotenv()

st.set_page_config(page_title="Story Bible Builder", page_icon="📚", layout="centered")

st.title("📚 Story Bible Builder")
st.caption("Give me a pitch.  I will create a compact, validated Story Bible and save it to output/state/bible.json.")

# OpenAI key status
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not set.  Add it to your environment or a .env file.  Then reload.")
    st.stop()

pitch = st.text_area(
    "Story idea or pitch",
    placeholder="e.g., In a drowned city of glass, a jaded cartographer must guide refugees through shifting canals while a newborn AI learns to love.",
    value="Drowned glass city. Guild cartographer with trust issues. Newborn harbor AI with missing memories. Smuggler wants a living map called the Glass Atlas. Erratic tides as the city’s metronome. Survival through navigation.",
    height=180,
)

out_dir = st.text_input("Output directory", value="output")
col1, col2 = st.columns(2)
with col1:
    model_planner = st.selectbox("Planner model", options=["gpt-5", "gpt-5-mini", "gpt-5-nano"], index=0)
with col2:
    keep_existing = st.checkbox("Do not overwrite if bible exists", value=False)

go = st.button("Generate Story Bible", type="primary", use_container_width=True)

if go:
    if not pitch.strip():
        st.warning("Please enter a pitch.  Then try again.")
        st.stop()

    # Ensure directories
    base = Path(out_dir)
    (base / "state").mkdir(parents=True, exist_ok=True)

    bible_path = base / "state" / "bible.json"
    if keep_existing and bible_path.exists():
        st.info(f"A bible already exists at {bible_path}.  Skipping generation.")
    else:
        with st.spinner("Calling the planner model and validating JSON..."):
            bible: StoryBible = generate_story_bible(pitch)

        # Persist
        data = bible.model_dump()
        bible_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        st.success(f"Story Bible saved to {bible_path}")
        st.download_button(
            "Download bible.json",
            data=json.dumps(data, indent=2),
            file_name="bible.json",
            mime="application/json",
            use_container_width=True,
        )

        st.subheader("Preview")
        st.json(data, expanded=False)

st.divider()
st.markdown(
    "Tips:  Keep pitches concrete.  Name two to four core characters and the central tension.  "
    "You can rerun with the same pitch to iterate, or check **Do not overwrite** to preserve earlier runs."
)
