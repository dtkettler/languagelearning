import json
import codecs
from gpt import GPT


prompts = {
    "basic_prompt": {
        "system_prompt": """You are talking in Japanese to the user while acting as the following character:
{}

At the location:
{}

The user eventually wants to accomplish the goal:
{}

Act as if you only understand Japanese.  If the user uses another language say 分かりません or something similar""",
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

gpt_control = GPT()

#character = "Bob the angry ramen chef"
#location = "A dingy ramen shop in a neglected area"
#goal = "Order the super spicy ramen"

with codecs.open("example.json", encoding='utf-8') as f:
    example = json.load(f)


character = json.dumps(example["Scenario"]["character"])
location = json.dumps(example["Scenario"]["location"])
goal = json.dumps(example["Scenario"]["goal"])

print(example["Scenario"]["starting_line"])

dialogue = True
history = []
while dialogue:
    command = input("What would you like to say? ")

    response = gpt_control.run_gpt_with_history(prompts["basic_prompt"]["system_prompt"].format(character, location, goal),
                                                command, history, functions=[prompts["basic_prompt"]["function"]])
    print(response["message"])

    history.append({"user": command, "assistant": response["message"]})

    if "goal_accomplished" in response and response["goal_accomplished"]:
        dialogue = False


print("Congrats")
