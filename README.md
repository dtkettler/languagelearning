# Languaverse
Hackathon language learning project

# Installation

Install python requirements (`pip install -r requirements.txt`)

Flask session requires redis.  If you have redis installed you can just run it.  If not but if you have docker then run: `docker run --name some-redis -d -p 6379:6379 redis`

Will need to create a keys.ini file with one section (`[DEFAULT]`) and one entry `open_ai_key = ` that has your OpenAI key.

Then run the UI with app.py
