import os
import json
import re
from abc import ABC, abstractmethod
import google.generativeai as genai


class LLMProvider(ABC):
    @abstractmethod
    def chat_completion(self, messages, functions):
        pass


class GeminiProvider(LLMProvider):
    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada")

        genai.configure(api_key=api_key)

        self.model_name = "models/gemini-2.0-flash-001"

        self.available_models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest"
        ]

    def chat_completion(self, messages, functions):
        try:

            full_prompt = ""

            for msg in messages:
                if msg["role"] == "system":
                    full_prompt += f"INSTRUÇÕES DO SISTEMA:\n{msg['content']}\n\n"
                elif msg["role"] == "user":
                    full_prompt += f"USUÁRIO: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    full_prompt += f"ASSISTENTE: {msg['content']}\n"

            if functions:
                full_prompt += "\nFUNÇÕES DISPONÍVEIS (use [FUNÇÃO:nome:json]):\n"
                for func in functions:
                    func_name = func.get("name", "")
                    func_desc = func.get("description", "")
                    full_prompt += f"- {func_name}: {func_desc}\n"

            full_prompt += "\nRESPOSTA:"

            last_error = None
            response = None

            for model_name in self.available_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(full_prompt)
                    break
                except Exception as e:
                    last_error = e
                    continue

            if not response:
                raise last_error or Exception("Nenhum modelo disponível")

            response_text = response.text

            if response_text and "[FUNÇÃO:" in response_text:

                func_match = re.search(r"\[FUNÇÃO:(\w+):(.*?)\]", response_text)
                if func_match:
                    function_name = func_match.group(1)
                    try:
                        function_args = json.loads(func_match.group(2))
                    except:
                        function_args = {}

                    clean_content = re.sub(r"\[FUNÇÃO:.*?\]", "", response_text).strip()
                    return {
                        "content": clean_content,
                        "function_call": {
                            "name": function_name,
                            "arguments": function_args,
                        },
                    }

            return {"content": response_text}

        except Exception as e:
            return {"content": f"Erro ao chamar Gemini: {str(e)}"}


def get_llm_provider():
    return GeminiProvider()
