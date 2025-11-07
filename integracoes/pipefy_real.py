#!/usr/bin/env python3
"""
Integração REAL com Pipefy API
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


class PipefyIntegration:
    def __init__(self):
        self.api_token = os.getenv("PIPEFY_API_TOKEN")
        self.base_url = "https://api.pipefy.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        self.pipe_id = os.getenv("PIPEFY_PIPE_ID", "YOUR_PIPE_ID")

    def create_or_update_card(
        self,
        nome,
        email,
        empresa,
        necessidade,
        interesse_confirmado=False,
        meeting_link=None,
        meeting_datetime=None,
    ):
        """Cria ou atualiza card no Pipefy usando email como chave única"""

        existing_card = self.find_card_by_email(email)

        if existing_card:
            # Extrair dados existentes do card
            existing_meeting_link = None
            existing_meeting_datetime = None

            for field in existing_card.get("fields", []):
                field_id = field.get("field", {}).get("id")
                if field_id == "meeting_link":
                    existing_meeting_link = field.get("value")
                elif field_id == "meeting_datetime":
                    existing_meeting_datetime = field.get("value")

            # Se já tem agendamento, manter os dados existentes
            if existing_meeting_link:
                meeting_link = existing_meeting_link
                meeting_datetime = existing_meeting_datetime

            return self.update_card(
                existing_card["id"],
                nome,
                email,
                empresa,
                necessidade,
                interesse_confirmado,
                meeting_link,
                meeting_datetime,
            )
        else:
            return self.create_card(
                nome,
                email,
                empresa,
                necessidade,
                interesse_confirmado,
                meeting_link,
                meeting_datetime,
            )

    def find_card_by_email(self, email):
        """Busca card existente por email"""
        query = """
        query($pipeId: ID!) {
            cards(pipe_id: $pipeId, first: 50) {
                edges {
                    node {
                        id
                        title
                        fields {
                            field {
                                id
                                label
                            }
                            value
                        }
                    }
                }
            }
        }
        """

        variables = {"pipeId": self.pipe_id}

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables},
            )

            if response.status_code == 200:
                data = response.json()
                cards = data.get("data", {}).get("cards", {}).get("edges", [])

                for card_edge in cards:
                    card = card_edge["node"]

                    for field in card.get("fields", []):
                        field_id = field.get("field", {}).get("id")
                        field_label = field.get("field", {}).get("label")
                        field_value = field.get("value")

                        # Verifica tanto por ID quanto por label
                        if (
                            field_id == "email"
                            or field_label == "email"
                            or field_label == "Email"
                        ) and field_value == email:
                            return card
                return None
            else:
                return None

        except Exception:
            return None

    def create_card(
        self,
        nome,
        email,
        empresa,
        necessidade,
        interesse_confirmado,
        meeting_link,
        meeting_datetime,
    ):
        """Cria novo card no Pipefy"""
        mutation = """
        mutation($pipeId: ID!, $title: String!, $fields: [FieldValueInput!]) {
            createCard(input: {
                pipe_id: $pipeId,
                title: $title,
                fields_attributes: $fields
            }) {
                card {
                    id
                    title
                }
            }
        }
        """

        fields = [
            {"field_id": "nome", "field_value": nome},
            {"field_id": "email", "field_value": email},
            {"field_id": "empresa", "field_value": empresa},
            {"field_id": "necessidade", "field_value": necessidade},
            {
                "field_id": "checklist_vertical",
                "field_value": ["Sim"] if interesse_confirmado else ["Não"],
            },
        ]

        if meeting_link:
            fields.append({"field_id": "meeting_link", "field_value": meeting_link})

        if meeting_datetime:
            fields.append(
                {"field_id": "meeting_datetime", "field_value": meeting_datetime}
            )

        variables = {
            "pipeId": self.pipe_id,
            "title": f"Lead: {nome} - {empresa}",
            "fields": fields,
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": mutation, "variables": variables},
            )

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    return None
                card = data.get("data", {}).get("createCard", {}).get("card")
                if card:
                    card["is_update"] = False
                return card
            else:
                return None

        except Exception:
            return None

    def update_card(
        self,
        card_id,
        nome,
        email,
        empresa,
        necessidade,
        interesse_confirmado,
        meeting_link,
        meeting_datetime,
    ):
        """Atualiza card existente no Pipefy"""

        success_count = 0

        if meeting_link:
            success = self._update_single_field(card_id, "meeting_link", meeting_link)
            if success:
                success_count += 1

        if meeting_datetime:
            success = self._update_single_field(
                card_id, "meeting_datetime", meeting_datetime
            )
            if success:
                success_count += 1

        interesse_value = ["Sim"] if interesse_confirmado else ["Não"]
        success = self._update_single_field(
            card_id, "checklist_vertical", interesse_value
        )
        if success:
            success_count += 1

        if success_count > 0:
            return {
                "id": card_id,
                "title": f"Lead: {nome} - {empresa} (ATUALIZADO)",
                "meeting_link": meeting_link,
                "meeting_datetime": meeting_datetime,
                "has_existing_meeting": bool(meeting_link),
                "is_update": True,
            }
        else:
            return None

    def _update_single_field(self, card_id, field_id, field_value):
        """Atualiza um único campo do card"""
        mutation = """
        mutation($cardId: ID!, $fieldId: ID!, $fieldValue: [UndefinedInput]) {
            updateCardField(input: {
                card_id: $cardId,
                field_id: $fieldId,
                new_value: $fieldValue
            }) {
                card {
                    id
                }
            }
        }
        """

        if not isinstance(field_value, list):
            field_value = [field_value]

        variables = {"cardId": card_id, "fieldId": field_id, "fieldValue": field_value}

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": mutation, "variables": variables},
            )

            if response.status_code == 200:
                data = response.json()

                if "errors" in data:
                    print(f"[DEBUG] Erro ao atualizar {field_id}: {data['errors']}")
                    return False

                card = data.get("data", {}).get("updateCardField", {}).get("card")
                if card:
                    print(f"[DEBUG] Campo {field_id} atualizado com sucesso")
                    return True
                else:
                    print(f"[DEBUG] Falha ao atualizar campo {field_id}")
                    return False
            else:
                print(
                    f"[DEBUG] Erro HTTP ao atualizar {field_id}: {response.status_code}"
                )
                return False

        except Exception as e:
            print(f"[DEBUG] Exceção ao atualizar {field_id}: {e}")
            return False

    def get_pipe_fields(self):
        """Lista todos os campos do pipe para descobrir os field_ids corretos"""
        query = """
        query($pipeId: ID!) {
            pipe(id: $pipeId) {
                start_form_fields {
                    id
                    label
                    type
                    options
                }
                phases {
                    name
                    fields {
                        id
                        label
                        type
                        options
                    }
                }
            }
        }
        """

        variables = {"pipeId": self.pipe_id}

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables},
            )

            if response.status_code == 200:
                data = response.json()
                if "errors" not in data:
                    pipe_data = data.get("data", {}).get("pipe", {})

                    start_fields = pipe_data.get("start_form_fields", [])
                    phases = pipe_data.get("phases", [])

                    return {"start_form": start_fields, "phases": phases}
                else:
                    return None
            else:
                return None
        except Exception:
            return None
