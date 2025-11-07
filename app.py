import gradio as gr
from agent.sdr_agent import SDRAgent

# Inicializa o agente
sdr = SDRAgent()


def chat_function(message, history):
    """Função principal do chat"""
    response = sdr.processar_conversa(message, history)
    return response


demo = gr.ChatInterface(
    fn=chat_function,
    title="🤖 SDR Agent - Elite Dev IA",
    description="Assistente virtual para soluções de IA",
    examples=[
        "Olá, gostaria de saber sobre soluções de IA",
        "Preciso automatizar processos na minha empresa",
        "Tenho interesse em chatbots para atendimento",
        "Quero agendar uma conversa",
    ],
)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=True,
        inbrowser=True,
    )
