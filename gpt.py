import openai
import configparser
import time
import json
import logging
from animated_loader import AnimatedLoader


logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)


class GPT:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('keys.ini')

        self.api_key = config['DEFAULT']['openai_key']

        config.read('config.ini')
        self.model1 = config['DEFAULT']['model_create']
        self.model2 = config['DEFAULT']['model_converse']

    def completion_with_retries(self, model, messages, temperature=0.5, max_retries=10, functions=None, json=False):
        openai.api_key = self.api_key

        with AnimatedLoader():
            successful = False
            tries = 0
            while tries < max_retries and not successful:
                try:
                    if functions:
                        completion = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature,
                                                                  functions=functions, function_call={"name": functions[0]["name"]})
                    elif json:
                        completion = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature,
                                                                  response_format={"type": "json_object"})
                    else:
                        completion = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
                    successful = True
                except Exception as e:
                    logging.error("error connecting to GPT")
                    logging.error(e)
                    time.sleep((tries + 1) * 2)
                    completion = ""

                tries += 1

        return completion

    def run_gpt(self, system_prompt, user_prompt, temperature=0.5, force_long=False, json=False):
        openai.api_key = self.api_key
        completion = self.completion_with_retries(
            model=self.model1,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            json=json
        )

        output = completion['choices'][0]['message']['content']

        return output

    def run_gpt_with_history(self, system_prompt, user_prompt, history, temperature=0.5, force_long=False, functions=None):
        openai.api_key = self.api_key

        messages = [{"role": "system", "content": system_prompt}]
        for message in history:
            messages.append({"role": "user", "content": message["user"]})
            messages.append({"role": "assistant", "content": message["assistant"]})
        messages.append({"role": "user", "content": user_prompt})

        total_prompt = system_prompt
        for message in messages:
            total_prompt += message["content"]

        completion = self.completion_with_retries(
            model=self.model2,
            messages=messages,
            temperature=temperature,
            functions=functions
        )

        if functions:
            output = json.loads(completion['choices'][0]['message']['function_call']['arguments'])
        else:
            output = json.loads(completion['choices'][0]['message']['content'])

        return output


