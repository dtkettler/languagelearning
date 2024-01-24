import json


prompts = {
    "basic_prompt": {
        "system_prompt": """You are talking in Japanese to the user while acting as the following character:
{}

At the location:
{}

The user eventually wants to accomplish the goal:
{}

Act as if you only understand Japanese.  If the user uses another language respond with 分かりません or something similar""",
        "function": {
            "name": "conversation_with_flag",
            "description": "Get the text of the conversation and add a flag to indicate whether or not the goal has been accomplished",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The text of the message the character is saying"
                    },
                    "goal_accomplished": {
                        "type": "integer",
                        "description": "Should be 0 unless the goal has been accomplished and then 1 if it has"
                    }
                }
            },
            "required": ["message", "goal_accomplished"]
        }
    }
}

def create_conversation_response(character, location, goal, details, user_message, history, gpt_control):
    response = gpt_control.run_gpt_with_history(prompts["basic_prompt"]["system_prompt"].format(character, location, goal),
                                                user_message, history, functions=[prompts["basic_prompt"]["function"]])
    print(response["message"])

    history.append({"user": user_message, "assistant": response["message"]})

    if "goal_accomplished" in response and response["goal_accomplished"]:
        goal_accomplished = True
    else:
        goal_accomplished = False

    return history, goal_accomplished
