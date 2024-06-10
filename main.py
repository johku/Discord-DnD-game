import openai
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime

import discord
from discord.ext import commands
import os
import glob
import random

assistant_id = ""
thread_id = ""
vector_store_id = ""
run_id = ""

load_dotenv()

client = openai.OpenAI()
model = "gpt-4o"

DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def create_bot():
    # Create Bot
    stock_bot_assistant = client.beta.assistants.create(
        name = "dungeon-master",
        instructions = "You are dungeons and dragons discord bot. You are the worlds best dungeon master.",
        tools=[{"type": "file_search"}],
        model = model,
            )

    global assistant_id 
    assistant_id = stock_bot_assistant.id


def add_files():
    # Create a vector store called "data"
    vector_store = client.beta.vector_stores.create(name="data")
    global vector_store_id 
    vector_store_id = vector_store.id
    
    # Ready the files for upload to OpenAI
    # Get all PDF file paths in the directory
    directory = './files'
    file_paths = glob.glob(os.path.join(directory, "*.pdf"))
    file_streams = [open(path, "rb") for path in file_paths]
    
    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
    )
    
    # You can print the status and the file counts of the batch to see the result of this operation.
    print(file_batch.status)
    print(file_batch.file_counts)

    assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

def create_thread():
    # Create Thread
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "discussion"
            }
        ]
    )

    global thread_id
    thread_id = thread.id

def create_message(message):
    # Create message

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

def create_run():
    # Run our assistant
    run = client.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = assistant_id,
        instructions = "Address the user as adventurer."
    )

    global run_id
    run_id = run.id

def wrap_text_in_file(file_path, line_length=200):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()

    wrapped_lines = []

    for line in lines:
        line = line.rstrip('\n')
        while len(line) > line_length:
            # Find the position to split the line
            split_pos = line.rfind(' ', 0, line_length)
            if split_pos == -1:
                split_pos = line_length
            wrapped_lines.append(line[:split_pos])
            line = line[split_pos:].lstrip()
        wrapped_lines.append(line)

    with open(file_path, 'w') as outfile:
        for line in wrapped_lines:
            outfile.write(line + '\n')


def ChatGPT(client, thread_id, run_id, sleep_interval=5):

    """
    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


def Dall_E(description):
    response = client.images.generate(prompt=description,
    n=1,
    size="512x512")

    image_url = response.data[0].url

    return image_url

@bot.event
async def on_ready():
    print('Logged on as', bot.user)
    create_bot()
    try:
        add_files()
    except Exception as e:
        print(f"An error occurred: {e}")
    create_thread()

@bot.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == bot.user:
        return

    # Check if the message starts with "!prompt"
    if message.content.startswith('!prompt'):
        # Extract the prompt after "!prompt" (excluding the command itself)
        prompt = message.content[len('!prompt'):].strip()
        create_message(prompt)
        create_run()

        # Generate a response using ChatGPT
        response = ChatGPT(client=client, thread_id=thread_id, run_id=run_id)

        # Write response to a text file
        response_file_path = "response.txt"
        with open(response_file_path, "w") as file:
            file.write(response)

        wrap_text_in_file(response_file_path)

        # Send the response as a text file attachment to the Discord channel
        await message.channel.send(file=discord.File(response_file_path))

        # Delete the local text file
        os.remove(response_file_path)

    # Check if the message starts with "!image"
    if message.content.startswith("!image"):
        description = message.content[len('!image'):].strip()

        url = Dall_E(description)

        await message.channel.send(url)

        # Check if the message starts with "!prompt"
    if message.content.startswith('!roll'):

        number = random.randint(1, 21)

        response = f"Your dice roll was: {number}"

        # Send the response back to the Discord channel
        await message.channel.send(response)

bot.run(DISCORD_API_TOKEN)







