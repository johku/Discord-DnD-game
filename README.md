# Discord-assistant
Discord (chatGPT) assistant with the personality of Splinter from TMNT.

!prompt "insert text" for ChatGPT prompt

!image "insert text" for Dall-E image


# Setup
## Create bot with no functionality
1. Go to https://discord.com/developers/applications
2. Click new application
3. Configure the bot settings as shown below:

   ![Bot settings](/images/bot_settings.PNG)
   
4. Create a bot invite link with the following permissions:

   ![Bot permissions](/images/bot_permissions.PNG)
   
5. Get the bot token by clicking "Reset Token" as shown below:

   ![Bot get token](/images/bot_get_token.PNG)

## Add functionality
1. Download the contents of this repository
2. Generate OpenAI API key in here: https://platform.openai.com/account/api-keys
3. Create .env file to the repository root and add following fields to it:
```
DISCORD_API_TOKEN=""
OPENAI_API_KEY=""
```
4. Fill the API token/key fields with keys you obtained earlier
5. Open cmd/terminal and navigate to the downloaded repository
6. In cmd/terminal type the following commands:

    1. `pip install virtualenv`
    2. `python3 -m venv venv`
    3. `venv\Scripts\activate` (or `source venv/bin/activate` if on Linux)
    4. `pip install --upgrade pip`
    5. `pip install -r requirements.txt`
    8. `python3 main.py`


Your bot should now be running for as long as you have the cmd/terminal open


Source of files: https://www.reddit.com/r/DnD/comments/300zz1/links_to_all_available_free_legal_pdfs_for_5e_so/
