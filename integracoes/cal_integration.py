#!/usr/bin/env python3
"""
Integração com Cal.com API
"""

import requests
import json
from datetime import datetime, timedelta
import os
import re
from dotenv import load_dotenv

load_dotenv()


class CalIntegration:
    def __init__(self):
        self.api_token = os.getenv("CAL_API_TOKEN")
        self.base_url = "https://api.cal.com/v1"
        self.headers = {
            "Content-Type": "application/json",
        }

    def get_event_types(self):
        """Lista event types disponíveis"""
        try:
            params = {"apiKey": self.api_token}
            response = requests.get(
                f"{self.base_url}/event-types", headers=self.headers, params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None

    def check_availability(self, event_type_id, date_from, date_to):
        """Verifica disponibilidade de horários"""
        try:
            params = {
                "apiKey": self.api_token,
                "eventTypeId": event_type_id,
                "startTime": f"{date_from}T00:00:00.000Z",
                "endTime": f"{date_to}T23:59:59.000Z",
                "timeZone": "America/Sao_Paulo",
            }

            response = requests.get(
                f"{self.base_url}/slots", headers=self.headers, params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None

    def get_existing_bookings(self):
        """Lista agendamentos existentes"""
        try:
            params = {"apiKey": self.api_token}
            response = requests.get(
                f"{self.base_url}/bookings", headers=self.headers, params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None

    def get_available_slots(self):
        """Retorna próximos 3 horários disponíveis"""
        try:
            event_types = self.get_event_types()
            if not event_types or not event_types.get("event_types"):
                return None

            event_type_id = event_types["event_types"][0]["id"]
            date_from = datetime.now().strftime("%Y-%m-%d")
            date_to = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

            availability = self.check_availability(event_type_id, date_from, date_to)

            if availability and availability.get("slots"):
                slots_data = availability["slots"]
                available_slots = []

                for date_key, day_slots in slots_data.items():
                    for slot in day_slots:
                        if len(available_slots) >= 3:
                            break

                        try:
                            slot_time_str = slot.get("time")
                            if slot_time_str:
                                slot_time = datetime.fromisoformat(slot_time_str)
                                formatted_slot = slot_time.strftime("%d/%m às %H:%M")
                                available_slots.append(formatted_slot)
                        except Exception as e:
                            continue

                    if len(available_slots) >= 3:
                        break

                if available_slots:
                    return available_slots

            bookings = self.get_existing_bookings()
            candidate_slots = []
            base = datetime.now()
            horarios_comerciais = [9, 10, 11, 14, 15, 16, 17]

            for i in range(7):
                check_date = base + timedelta(days=i + 1)
                if check_date.weekday() < 5:
                    for hora in horarios_comerciais:
                        slot_time = check_date.replace(
                            hour=hora, minute=0, second=0, microsecond=0
                        )
                        candidate_slots.append(slot_time)

            available_slots = []
            occupied_times = set()

            if bookings and bookings.get("bookings"):
                for booking in bookings["bookings"]:
                    if booking.get("startTime"):
                        booking_time = datetime.fromisoformat(
                            booking["startTime"].replace("Z", "+00:00")
                        )
                        booking_time_br = booking_time.replace(tzinfo=None) - timedelta(
                            hours=3
                        )
                        occupied_key = booking_time_br.strftime("%Y-%m-%d %H:%M")
                        occupied_times.add(occupied_key)

            for i, slot in enumerate(candidate_slots):
                if i >= 10:
                    break

                slot_key = slot.strftime("%Y-%m-%d %H:%M")

                if slot_key not in occupied_times:
                    formatted_slot = slot.strftime("%d/%m às %H:%M")
                    available_slots.append(formatted_slot)
                    if len(available_slots) >= 3:
                        break

            if available_slots:
                return available_slots

            return None

        except Exception as e:
            return None

    def create_booking(self, event_type_id, start_time, name, email):
        """Cria agendamento no Cal.com"""
        try:
            headers = {
                "Content-Type": "application/json",
            }

            booking_data = {
                "eventTypeId": event_type_id,
                "start": start_time,
                "responses": {
                    "name": name,
                    "email": email,
                    "location": {"optionValue": "", "value": "Cal.com"},
                },
                "timeZone": "America/Sao_Paulo",
                "language": "pt",
                "metadata": {},
            }

            params = {"apiKey": self.api_token}
            response = requests.post(
                f"{self.base_url}/bookings",
                headers=headers,
                params=params,
                json=booking_data,
            )

            if response.status_code == 200:
                booking = response.json()
                return booking
            else:
                return None

        except Exception as e:
            return None

    def agendar_reuniao_cal(self, email, nome, slot_escolhido):
        """Agenda reunião no Cal.com"""
        try:
            match = re.search(
                r"(\d{2})/(\d{2}) (às|as) (\d{2}):(\d{2})", slot_escolhido
            )
            if match:
                dia, mes, _, hora, minuto = match.groups()
                ano = datetime.now().year
                start_dt = datetime(ano, int(mes), int(dia), int(hora), int(minuto))

                now = datetime.now()
                time_diff = (start_dt - now).total_seconds() / 60

                if time_diff < 120:
                    start_dt = now + timedelta(hours=3)
                    start_dt = start_dt.replace(minute=0, second=0, microsecond=0)

                is_dia_util = start_dt.weekday() < 5

                if not is_dia_util:
                    days_ahead = 7 - start_dt.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    start_dt = start_dt + timedelta(days=days_ahead)
                    start_dt = start_dt.replace(hour=14, minute=0)

                start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%S-03:00")
            else:
                start_dt = datetime.now() + timedelta(hours=3)
                start_dt = start_dt.replace(minute=0, second=0, microsecond=0)
                start_time = start_dt.strftime("%Y-%m-%dT%H:%M:%S-03:00")

            event_types = self.get_event_types()
            if not event_types or not event_types.get("event_types"):
                fallback_link = f"https://cal.com/diego-berselli-awbokf?date={start_dt.strftime('%Y-%m-%d')}&time={start_dt.strftime('%H:%M')}"
                return fallback_link

            available_types = event_types["event_types"]
            event_type_id = None
            for et in available_types:
                if et.get("length") == 30:
                    event_type_id = et["id"]
                    break
            if not event_type_id:
                event_type_id = available_types[0]["id"]

            booking = self.create_booking(event_type_id, start_time, nome, email)

            if booking and booking.get("uid"):
                meeting_link = f"https://cal.com/meeting/{booking['uid']}"
                return meeting_link
            else:
                fallback_link = f"https://cal.com/diego-berselli-awbokf?date={start_dt.strftime('%Y-%m-%d')}&time={start_dt.strftime('%H:%M')}"
                return fallback_link

        except Exception as e:
            return "https://cal.com/diego-berselli-awbokf"
