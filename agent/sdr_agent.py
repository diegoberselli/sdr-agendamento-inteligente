import json
import os
import re
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from integracoes.pipefy_real import PipefyIntegration
from integracoes.cal_integration import CalIntegration
from agent.llm_factory import get_llm_provider


load_dotenv()


class SDRAgent:
    def __init__(self):
        self.llm = get_llm_provider()
        self.pipefy_token = os.getenv("PIPEFY_API_TOKEN")
        self.cal_token = os.getenv("CAL_API_TOKEN")
        self.lead_data = {}

    def registrar_lead(
        self, nome, email, empresa, necessidade, interesse_confirmado=False
    ):
        """Registra lead no Pipefy"""
        self.lead_data = {
            "nome": nome,
            "email": email,
            "empresa": empresa,
            "necessidade": necessidade,
            "interesse_confirmado": interesse_confirmado,
            "timestamp": datetime.now().isoformat(),
        }

        if self.pipefy_token:
            try:
                pipefy = PipefyIntegration()
                card = pipefy.create_or_update_card(
                    nome=nome,
                    email=email,
                    empresa=empresa,
                    necessidade=necessidade,
                    interesse_confirmado=interesse_confirmado,
                )
                pass
            except (ImportError, AttributeError) as e:
                pass
            except (requests.RequestException, ConnectionError) as e:
                pass
            except (KeyError, ValueError) as e:
                pass
        else:
            pass

        return f"Lead {nome} registrado com sucesso"

    def oferecer_horarios(self):
        """Retorna horários disponíveis"""
        if self.cal_token:
            try:
                cal = CalIntegration()
                real_slots = cal.get_available_slots()

                if real_slots and len(real_slots) >= 3:
                    horarios = []
                    for i, slot in enumerate(real_slots[:3]):
                        horarios.append(f"Opção {i+1}: {slot}")

                    return horarios
            except Exception as e:
                pass

        horarios = []
        base = datetime.now()
        horarios_comerciais = [14, 15, 16]

        dias_base = 1
        while True:
            primeiro_dia = base + timedelta(days=dias_base)
            if primeiro_dia.weekday() < 5:
                break
            dias_base += 1

        for i, hora in enumerate(horarios_comerciais):
            if i == 0:
                data_horario = primeiro_dia
            else:
                dias_extras = 1
                while True:
                    data_horario = primeiro_dia + timedelta(days=i + dias_extras - 1)
                    if data_horario.weekday() < 5:
                        break
                    dias_extras += 1
                    data_horario = primeiro_dia + timedelta(days=i + dias_extras - 1)

            data_horario = data_horario.replace(
                hour=hora, minute=0, second=0, microsecond=0
            )
            horarios.append(f"Opção {i+1}: {data_horario.strftime('%d/%m às %H:%M')}")

        return horarios

    def agendar_reuniao(self, slot_escolhido, lead_data=None):
        """Agenda reunião via Cal.com"""
        if slot_escolhido in ["1", "2", "3"]:
            horarios = self.oferecer_horarios()
            slot_index = int(slot_escolhido) - 1
            if slot_index < len(horarios):
                slot_escolhido = horarios[slot_index]

        try:

            match = re.search(
                r"(\d{2})/(\d{2}) (às|as) (\d{2}):(\d{2})", slot_escolhido
            )
            if match:
                dia, mes, _, hora, minuto = match.groups()
                ano = datetime.now().year
                meeting_datetime = f"{ano}-{mes}-{dia}T{hora}:{minuto}:00-03:00"
            else:
                meeting_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-03:00")
        except Exception as e:
            meeting_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-03:00")

        if self.cal_token:
            try:
                cal = CalIntegration()

                email = self.lead_data.get("email", "")
                nome = self.lead_data.get("nome", "")

                if not email or not nome:
                    return "Erro: dados do lead nao encontrados. Tente novamente."

                meeting_link = cal.agendar_reuniao_cal(
                    email=email,
                    nome=nome,
                    slot_escolhido=slot_escolhido,
                )

                if meeting_link:
                    if self.pipefy_token:
                        try:
                            pipefy = PipefyIntegration()
                            updated_card = pipefy.create_or_update_card(
                                nome=self.lead_data.get("nome", ""),
                                email=self.lead_data.get("email", ""),
                                empresa=self.lead_data.get("empresa", ""),
                                necessidade=self.lead_data.get("necessidade", ""),
                                interesse_confirmado=True,
                                meeting_link=meeting_link,
                                meeting_datetime=meeting_datetime,
                            )
                        except Exception as e:
                            pass

                    return f"✅ **Reunião agendada com sucesso!**\n\n📅 **Horário**: {slot_escolhido}\n🔗 **Link da reunião**: {meeting_link}\n\n💾 Seus dados foram salvos no nosso sistema."
                else:
                    return f"❌ Erro ao agendar. Tente novamente ou entre em contato."

            except Exception as e:
                return f"❌ Erro ao agendar. Tente novamente ou entre em contato."
        else:
            return f"❌ Agendamento não configurado. Entre em contato conosco."

    def processar_conversa(self, mensagem, historico):
        """Processa conversa com OpenAI"""

        functions = [
            {
                "name": "registrar_lead",
                "description": "Register lead data in Pipefy CRM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Lead's full name"},
                        "email": {
                            "type": "string",
                            "description": "Lead's email address",
                        },
                        "empresa": {"type": "string", "description": "Company name"},
                        "necessidade": {
                            "type": "string",
                            "description": "Business need or pain point",
                        },
                        "interesse_confirmado": {
                            "type": "boolean",
                            "description": "Whether lead confirmed interest in meeting",
                        },
                    },
                    "required": [
                        "nome",
                        "email",
                        "empresa",
                        "necessidade",
                        "interesse_confirmado",
                    ],
                },
            },
            {
                "name": "oferecer_horarios",
                "description": "Get available meeting slots from calendar",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "agendar_reuniao",
                "description": "Schedule meeting and update Pipefy with meeting link",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "slot_escolhido": {
                            "type": "string",
                            "description": "Chosen time slot",
                        },
                        "lead_data": {
                            "type": "object",
                            "description": "Lead information",
                        },
                    },
                    "required": ["slot_escolhido"],
                },
            },
        ]

        system_prompt = """You are an expert SDR for Elite Dev IA company.

        FLOW:
        1. GREETING: Introduce yourself and ask how you can help
        2. DISCOVERY: Collect name, email, company, business needs progressively
        3. QUALIFICATION: Ask "Gostaria de agendar uma conversa com nosso time?"
        4. REGISTRATION: When you have ALL data AND user shows interest, call registrar_lead with interesse_confirmado=True
        5. SCHEDULING: IMMEDIATELY after registrar_lead, call oferecer_horarios
        6. BOOKING: When user chooses "1", "2", or "3", call agendar_reuniao with slot_escolhido="1", "2", or "3"

        CRITICAL RULES:
        - NEVER call registrar_lead until you have: nome, email, empresa, necessidade
        - ALWAYS confirm interest BEFORE calling registrar_lead
        - Words indicating interest: "sim", "gostaria", "quero", "tenho interesse", "vamos", "ok"
        - After oferecer_horarios, wait for user to explicitly choose "1", "2", or "3"
        - When user says "1", "2", or "3", call agendar_reuniao with slot_escolhido="1", "2", or "3"
        - ALWAYS include slot_escolhido parameter in agendar_reuniao function call
        - ALWAYS respond in Portuguese
        - Be natural, professional and empathetic

        EXAMPLES:
        User: "1"
        You: Call agendar_reuniao(slot_escolhido="1")

        User: "2"
        You: Call agendar_reuniao(slot_escolhido="2")

        User: "3"
        You: Call agendar_reuniao(slot_escolhido="3")

        Start by introducing yourself as Elite Dev IA assistant."""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in historico:
            messages.append({"role": "user", "content": msg[0]})
            messages.append({"role": "assistant", "content": msg[1]})

        messages.append({"role": "user", "content": mensagem})

        try:
            response = self.llm.chat_completion(messages, functions)

            if isinstance(response, dict) and "function_call" in response:
                function_name = response["function_call"]["name"]
                function_args = response["function_call"]["arguments"]

                if function_name == "registrar_lead":
                    required_fields = ["nome", "email", "empresa", "necessidade"]

                    missing_fields = []
                    for field in required_fields:
                        value = function_args.get(field)
                        if not value or not str(value).strip():
                            missing_fields.append(field)

                    if not missing_fields:
                        self.lead_data.update(function_args)

                        card_info = None
                        if self.pipefy_token:
                            try:
                                pipefy = PipefyIntegration()
                                card_info = pipefy.create_or_update_card(
                                    **function_args
                                )

                                if card_info and card_info.get("has_existing_meeting"):
                                    existing_link = card_info.get("meeting_link")
                                    existing_datetime = card_info.get(
                                        "meeting_datetime"
                                    )
                                    result = f"Seu cadastro foi atualizado com sucesso!\n\n✅ Você já tem uma reunião agendada:\n🔗 **Link**: {existing_link}\n📅 **Data/Hora**: {existing_datetime}"
                                    return result
                            except Exception:
                                pass

                        if card_info and card_info.get("id"):
                            if card_info.get("is_update", False):
                                result = f"Cadastro atualizado com sucesso!"
                            else:
                                result = f"Lead {function_args['nome']} registrado com sucesso"
                        else:
                            result = self.registrar_lead(**function_args)

                        if function_args.get("interesse_confirmado", False):
                            horarios = self.oferecer_horarios()
                            result += f"\n\n✅ Perfeito! Tenho alguns horários disponíveis:\n\n1 - {horarios[0].replace('Opção 1: ', '')}\n2 - {horarios[1].replace('Opção 2: ', '')}\n3 - {horarios[2].replace('Opção 3: ', '')}\n\nQual horário funciona melhor para você?"
                    else:
                        result = f"Preciso das seguintes informações: {', '.join(missing_fields)}"
                elif function_name == "oferecer_horarios":
                    horarios = self.oferecer_horarios()
                    formatted_horarios = []
                    for i, horario in enumerate(horarios):
                        clean_horario = horario.replace(f"Opção {i+1}: ", "")
                        formatted_horarios.append(f"{i+1} - {clean_horario}")

                    result = f"✅ Perfeito! Tenho alguns horários disponíveis:\n\n{chr(10).join(formatted_horarios)}\n\nQual horário funciona melhor para você?"
                elif function_name == "agendar_reuniao":
                    slot = function_args.get("slot_escolhido", "")
                    # Aceita apenas "1", "2", "3"
                    if slot in ["1", "2", "3"]:
                        result = self.agendar_reuniao(**function_args)
                    else:
                        result = (
                            "Por favor, digite o numero da opcao desejada: 1, 2 ou 3."
                        )
                else:
                    result = "Função não reconhecida"

                content = response.get("content", "")
                if content and content.strip():
                    return f"{content} {result}"
                else:
                    return result
            else:
                return (
                    response.get("content", response)
                    if isinstance(response, dict)
                    else response
                )

        except (ImportError, AttributeError) as e:
            return f"Erro de configuração do sistema. Contate o suporte."
        except (requests.RequestException, ConnectionError) as e:
            return f"Erro de conexão. Verifique sua internet e tente novamente."
        except (KeyError, ValueError, TypeError) as e:
            return f"Erro nos dados fornecidos. Pode repetir a informação?"
        except json.JSONDecodeError as e:
            return f"Erro ao processar resposta. Tente novamente."
        except Exception as e:
            return f"Erro inesperado. Pode repetir? ({type(e).__name__})"
