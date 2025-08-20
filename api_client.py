# api_client.py
# Handles all communication with the Google Generative AI API.

import configparser
import json
import google.generativeai as genai

class ApiClient:
    # ... (the __init__, configure, and get_command_from_gemini methods are unchanged) ...
    def __init__(self):
        self.model = None
        self.configure()

    def configure(self):
        """Configures the Generative AI model with the API key from the config file."""
        config = configparser.ConfigParser()
        try:
            if not config.read('config.ini') or not config.has_section('API') or not config.has_option('API', 'key'):
                self.model = None; return
            api_key = config.get('API', 'key')
            if not api_key: self.model = None; return
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("Google AI SDK configured successfully.")
        except Exception as e:
            print(f"Error configuring Google AI SDK: {e}"); self.model = None

    def get_command_from_gemini(self, user_prompt, chat_history, os_info="Windows 11"):
        """
        Sends a prompt as part of an ongoing conversation to the Gemini API.
        """
        if not self.model:
            return {"error": "API client is not configured. Please set your API key in the settings."}

        system_prompt = f"""
        You are an expert command-line assistant for {os_info}. Your task is to generate and correct shell commands.

        **BEHAVIOR MODEL**
        1. Data Gathering: For diagnostic questions, your first response MUST be `response_type: 'data_gathering'`.
        2. Analysis & Solution: After receiving data, you will analyze it and provide a solution with `response_type: 'command'`.
        3. User Confirmation: If the user responds with a short confirmation ("do it"), re-issue the commands from your previous message.
        4. Self-Correction on Error: If a command fails, analyze the error message and provide a corrected command.

        **Constraints and Rules:**
        - **Safety First:** For any potentially destructive command, you MUST use `response_type: 'confirmation'`.
        - **JSON Formatting:** Your output MUST be a raw, syntactically correct JSON object.
          - **Escape backslashes:** All literal backslashes `\` must be escaped as `\\\\`.
          - **Escape double quotes:** All literal double quotes `"` within a JSON string value must be escaped as `\\"`.
        - **Output Structure:** The JSON must follow this structure:
            {{
                "response_type": "command" | "clarification" | "confirmation" | "data_gathering",
                "summary": "...", "directory_change_path": "...",
                "commands": [ {{ "command": "...", "description": "...", "is_powershell": boolean }} ],
                "clarification_question": "...", "confirmation_prompt": "..."
            }}
        """

        full_prompt = f"{system_prompt}\n\n**User Request:** \"{user_prompt}\""

        try:
            chat_session = self.model.start_chat(history=chat_history)
            response = chat_session.send_message(full_prompt)

            try:
                clean_response = response.text.strip().replace("```json", "").replace("```", "")
                return clean_response
            except (AttributeError):
                return response.text

        except Exception as e:
            print(f"An error occurred during API call: {e}")
            return {"error": f"An error occurred during API call: {e}"}

    # <-- NEW METHOD
    def get_suggestions_from_gemini(self, original_prompt, command_summary):
        """
        After a command is run, this method gets relevant follow-up suggestions.
        """
        if not self.model:
            return json.dumps({"suggestions": []}) # Return empty list if not configured

        prompt = f"""
        You are a helpful command-line assistant. A user just performed an action. Based on their initial request and the action's summary, provide 2-3 relevant follow-up prompts they might want to ask next.

        **Initial Request:** "{original_prompt}"
        **Action Summary:** "{command_summary}"

        **Your Task:**
        Generate a list of concise and helpful next steps.
        Your response MUST be a raw JSON object with a single key "suggestions" which contains a list of strings. Do not add any other text or formatting.

        **Example Response:**
        {{
          "suggestions": [
            "Show me the 5 largest files in this folder.",
            "Compress this folder into a zip file.",
            "How do I set permissions for this directory?"
          ]
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().replace("```json", "").replace("```", "")
        except Exception as e:
            print(f"Error getting suggestions: {e}")
            return json.dumps({"suggestions": []})