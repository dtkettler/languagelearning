import json


prompts = {"scenario_creation":
    { "system_prompt": """You are a helpful assistant creating the setting for roleplaying scenarios.
Based on the data the user provides, output a JSON object with the following fields:
details = {{
"character": "One or two sentences describing the character the user will be talking to in this scenario",
"location": "One or two sentences describing the location that this scenario takes place",
"starting_line": "One line in Japanese that the scenario's character will use to open the conversation with the user",
"details": "Any additional details you feel might add to this scenario"
}}
""",
      "user_prompt": """
scenario_name: {},
scenario_goal: {},
additional_details: {}
"""
    }
}


def create_scenario(name, goal, details, gpt_control):
    system_prompt = prompts["scenario_creation"]["system_prompt"]
    user_prompt = prompts["scenario_creation"]["user_prompt"].format(name, goal, details)

    output = gpt_control.run_gpt(system_prompt, user_prompt, temperature=0.8, json=True)
    output_json = json.loads(output)

    return output_json
