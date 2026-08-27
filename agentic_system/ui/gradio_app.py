import os
from uuid import uuid4
import gradio as gr
from agentic_system.agent.ai_agent import handle_customer_message


CUSTOM_CSS = """
html, body, #root {
    width: 100%;
    height: 100%;
    margin: 0;
}

.gradio-container {
    width: 100% !important;
    max-width: none !important;
    min-height: 100vh !important;
    min-height: 100dvh !important;
    padding: 16px 24px 0 !important;
    box-sizing: border-box !important;
}

#chatbot {
    width: 100% !important;
    min-height: calc(100vh - 170px) !important;
    min-height: calc(100dvh - 170px) !important;
}

.message,
.message .prose {
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: plaintext;
}

footer {
    display: none !important;
}

@media (max-width: 768px) {
    .gradio-container {
        padding: 10px 8px 0 !important;
    }

    #chatbot {
        min-height: calc(100vh - 135px) !important;
        min-height: calc(100dvh - 135px) !important;
    }
}
"""


def respond(message, history, chat_id):
    """Gradio callback; Supabase remains the persistent memory source."""
    if not message or not message.strip():
        yield "", history or [], chat_id
        return

    user_message = message.strip()
    chat_id = chat_id or str(uuid4())
    visible_history = list(history or [])

    # Show the customer message immediately while the agent is working.
    visible_history.append(
        {
            "role": "user",
            "content": user_message,
        }
    )
    yield "", visible_history, chat_id

    try:
        answer = handle_customer_message(chat_id, user_message)
    except Exception:
        answer = "معلش يا فندم، حصلت مشكلة مؤقتة. ممكن تجرب تاني؟"

    visible_history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
    yield "", visible_history, chat_id


with gr.Blocks(css=CUSTOM_CSS) as demo:
    gr.Markdown("# Restaurant Assistant")
    gr.Markdown("مساعد المطعم")

    chat_id_state = gr.State(value=None)
    chatbot = gr.Chatbot(elem_id="chatbot")
    message_box = gr.Textbox(
        show_label=False,
        placeholder="اكتب رسالتك هنا...",
        lines=2,
    )
    send_button = gr.Button("Send")

    inputs = [message_box, chatbot, chat_id_state]
    outputs = [message_box, chatbot, chat_id_state]

    message_box.submit(respond, inputs=inputs, outputs=outputs)
    send_button.click(respond, inputs=inputs, outputs=outputs)


