import gradio as gr
from input_embedding import ask_faq

def main():
    demo = gr.Interface(
        fn=ask_faq,
        inputs=gr.Textbox(
            label="Your Question",
            placeholder="e.g. How can I reset my debit card PIN?",
            lines=2
        ),
        outputs=gr.Textbox(
            label="Answer",
            placeholder="Response will appear here...",
            lines=5,
            interactive=False
        ),
        title="🏦 Bank FAQ Assistant",
        description="Ask any banking question — the system will search the Milvus FAQ database and respond concisely."
    )

    demo.launch(server_name="127.0.0.1", server_port=7860)

if __name__ == "__main__":
    main()
