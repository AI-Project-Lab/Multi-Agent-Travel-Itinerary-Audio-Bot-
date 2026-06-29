"""chatbot_gradio_runner.py — the web UI that ties everything together.

User flow (matches the original course, now powered by the agent team):

    1. Record your travel request with the microphone.
    2. The bot transcribes it (Whisper) into an editable text box — you can fix
       any mistakes. (This edit step is our simple "human-in-the-loop".)
    3. Click "Plan my trip". The LangGraph agent team builds an itinerary.
    4. Read the plan, listen to it spoken aloud, and peek at how the agents worked.

Launch it with:  poetry run RunChatBotScript
"""

import gradio as gr

from genai_voice.config.defaults import is_llm_configured
from genai_voice.graph.runner import run_itinerary
from genai_voice.processing.audio import speech_to_text, text_to_speech

# A message shown when the OpenAI key is missing, instead of a scary crash.
NO_KEY_MESSAGE = (
    "⚠️ No OpenAI API key found.\n\n"
    "Copy `.env_template` to `.env` and paste your key into it, then restart."
)


def transcribe(audio_path):
    """Step 2: turn the recorded audio into editable text."""
    if not audio_path:
        return ""
    if not is_llm_configured():
        return NO_KEY_MESSAGE
    return speech_to_text(audio_path)


def plan_trip(transcript, history):
    """Step 3: run the multi-agent team and return the plan + audio + trace.

    `history` is a gr.State value that lets follow-up questions keep context.
    """
    if not transcript.strip():
        return "Please record or type a travel request first.", None, "", history
    if not is_llm_configured():
        return NO_KEY_MESSAGE, None, "", history

    result = run_itinerary(transcript, history=history)
    itinerary = result["itinerary"]

    # Speak the itinerary back to the user.
    speech_path = text_to_speech(itinerary)

    # Show what each agent did (great for understanding orchestration).
    trace = "\n".join(result["trace"])

    # Remember this turn so the next request can build on it.
    updated_history = f"{history}\nUser: {transcript}\nBot: {itinerary}".strip()

    return itinerary, speech_path, trace, updated_history


def build_ui() -> gr.Blocks:
    """Construct the Gradio interface (layout + button wiring)."""
    with gr.Blocks(title="Multi-Agent Travel Itinerary Audio Bot") as demo:
        gr.Markdown(
            "# 🧭 Multi-Agent Travel Itinerary Audio Bot\n"
            "Speak your travel request and a *team of AI agents* "
            "(supervisor → transport, stay, activities, food → budget → writer) "
            "will plan your trip and read it back to you."
        )

        # gr.State holds per-session memory of the conversation (starts empty).
        history_state = gr.State(value="")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### 1) Record your request")
                mic = gr.Audio(sources=["microphone"], type="filepath", label="Tap to record")
                transcribe_btn = gr.Button("Transcribe ⤵️")

                gr.Markdown("### 2) Check the transcript (edit if needed)")
                transcript_box = gr.Textbox(
                    label="Your request",
                    placeholder='e.g. "Plan a 2-day trip to Goa with beach activities"',
                    lines=2,
                )
                plan_btn = gr.Button("3) Plan my trip 🧳", variant="primary")

            with gr.Column():
                gr.Markdown("### Your itinerary")
                itinerary_out = gr.Markdown()
                audio_out = gr.Audio(label="Listen to your plan", type="filepath")
                with gr.Accordion("🔍 Behind the scenes: what each agent did", open=False):
                    trace_out = gr.Textbox(label="Agent trace", lines=8)

        # Wire the buttons to the functions above.
        transcribe_btn.click(fn=transcribe, inputs=mic, outputs=transcript_box)
        plan_btn.click(
            fn=plan_trip,
            inputs=[transcript_box, history_state],
            outputs=[itinerary_out, audio_out, trace_out, history_state],
        )

    return demo


def run() -> None:
    """Entry point used by `poetry run RunChatBotScript`."""
    build_ui().launch()


if __name__ == "__main__":
    run()
