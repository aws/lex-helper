"""
Reservation utilities for flight booking operations.

This module provides utilities for airport resolution, city-to-IATA code conversion,
and other reservation-related operations used across multiple intents.
"""
import json
import re

from loguru import logger

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message, invoke_bedrock_converse
from lex_helper.core.bedrock_model_configs import BedrockModel

from ..session_attributes import AirlineBotSessionAttributes


class ReservationUtils:
    """Utility class for reservation-related operations."""

    @staticmethod
    def handle_city_resolution(
        city: str,
        slot_name_city: str,
        slot_name_code: str,
        session_attr: str,
        lex_request: LexRequest[AirlineBotSessionAttributes]
    ) -> LexResponse[AirlineBotSessionAttributes] | None:
        """
        Handle city to IATA resolution with multiple airport selection.
        
        Args:
            city: The city name to resolve
            slot_name_city: Name of the city slot to update
            slot_name_code: Name of the airport code slot to update
            session_attr: Session attribute name to store the IATA code
            lex_request: The Lex request object
            
        Returns:
            LexResponse if user interaction needed, None if resolved successfully
        """
        locale = lex_request.bot.localeId
        iata_result = ReservationUtils._resolve_city_to_iata(city, locale)

        if not isinstance(iata_result, dict) or "status" not in iata_result:
            logger.warning(f"Invalid response from city resolution: {iata_result}")
            return dialog.delegate(lex_request=lex_request)

        if iata_result["status"] == "multiple":
            options = "\n".join([f"- {opt}" for opt in iata_result.get("options", [])])
            message = f"I found multiple airports for {city}. Please choose one:\n{options}"
            message = get_message("book_flight.elicit_airport_code_selection")

            return dialog.elicit_slot(
                slot_to_elicit=slot_name_code,
                messages=[LexPlainText(content=message)],
                lex_request=lex_request
            )
        elif iata_result["status"] == "resolved":
            try:
                setattr(lex_request.sessionState.sessionAttributes, session_attr, iata_result.get("code", city))
                # Set resolved city and airport code slots
                lex_request.sessionState.intent.slots[slot_name_city] = {
                    "value": {
                        "interpretedValue": iata_result["city"],
                        "originalValue": city,
                        "resolvedValues": [iata_result["city"]],
                    }
                }
                lex_request.sessionState.intent.slots[slot_name_code] = {
                    "value": {
                        "interpretedValue": iata_result["code"],
                        "originalValue": iata_result["city"],
                        "resolvedValues": [iata_result["code"]],
                    }
                }
                return dialog.delegate(lex_request=lex_request)
            except (AttributeError, KeyError) as e:
                logger.error(f"Error setting slot values: {e}")
                return dialog.delegate(lex_request=lex_request)
        else:
            message = f"I couldn't find an airport for {city}. Please provide a valid city or airport name."
            return dialog.elicit_slot(
                slot_to_elicit=slot_name_city,
                messages=[LexPlainText(content=message)],
                lex_request=lex_request
            )

    @staticmethod
    def _resolve_city_to_iata(city_input: str, locale: str = "en_US") -> dict:
        """
        Resolve city name to IATA airport code using Bedrock.
        
        Args:
            city_input: The city name or airport code to resolve
            locale: The locale for response language (e.g., "en_US", "it_IT")
            
        Returns:
            dict: {"city":"YYY", "status": "resolved|multiple|none", "code": "XXX", "options": [...]}
        """
        # Adjust language based on locale

        language_instruction = f"""Respond in the language of this {locale} with the language specific city names."""


        system_prompt = f"""You are an airport code resolver. Return ONLY valid JSON. {language_instruction}

Rules:
1. For a city, return airports ONLY within or very close to that specific city (within 50km)
2. Include ALL major airports serving that city
3. Do NOT include airports from other cities in the same country
4. For "Paris" include both CDG and ORY
5. For "Rome" include only FCO and CIA (not Milan, Venice, etc.)
6. For "London" include LHR, LGW, STN, LTN

Formats:
Single: {{"city":"Los Angeles","status":"resolved","code":"LAX"}}
Multiple: {{"city":"Paris","status":"multiple","options":["CDG - Charles de Gaulle","ORY - Orly"]}}
None: {{"city":"InvalidCity","status":"none"}}

JSON ONLY."""

        messages = [
            {"role": "user", "content": [{"text": f"Find airports for: {city_input}"}]}
        ]

        try:
            response = invoke_bedrock_converse(
                messages=messages,
                model_id=BedrockModel.CLAUDE_3_HAIKU,
                max_tokens=300,
                temperature=0.0,
                system_prompt=system_prompt
            )
            logger.debug(f"Bedrock response for '{city_input}': {response}")

            # Extract JSON from the text field if response is a dict
            if isinstance(response, dict) and 'text' in response:
                text_content = response['text'].strip()
                try:
                    return json.loads(text_content)
                except json.JSONDecodeError:
                    # Fallback: parse natural language response
                    logger.warning(f"Non-JSON response from Bedrock: {text_content}")
                    return ReservationUtils._parse_natural_language_response(text_content, city_input)

            # Fallback for other response formats
            if isinstance(response, dict):
                return response
            return json.loads(response)
        except Exception as e:
            logger.error(f"Failed to resolve city to IATA: {e}")
            return {"status": "error"}

    @staticmethod
    def _parse_natural_language_response(text: str, city_input: str) -> dict:
        """
        Parse natural language response from Bedrock to extract IATA airport codes.
        
        This function serves as a fallback when Bedrock returns natural language
        instead of the expected JSON format. It uses regex to find 3-letter
        airport codes in the response text.
        
        Args:
            text: The natural language response from Bedrock
            city_input: The original city input for fallback city name
            
        Returns:
            dict: Formatted response with city, status, and code fields
                  {"city": "City Name", "status": "resolved|error", "code": "XXX"}
        """
        # Look for 3-letter airport codes in the response
        airport_codes = re.findall(r'\b[A-Z]{3}\b', text)

        if airport_codes:
            # Use the first found airport code
            code = airport_codes[0]
            return {
                "city": city_input.title(),
                "status": "resolved",
                "code": code
            }

        return {"status": "error"}

    @staticmethod
    def parse_airport_code(airport_code: str) -> str:
        """
        Safely parse airport code from formatted string.
        
        Args:
            airport_code: Airport code string, possibly in format "LAX - Los Angeles"
            
        Returns:
            str: The IATA code portion
        """
        if ' - ' in airport_code:
            return airport_code.split(' - ')[0]
        return airport_code
