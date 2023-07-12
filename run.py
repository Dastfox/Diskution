import os
import uvicorn
from chat_application.main import app
from chat_application.openai_call import load_secret_key

import re

def create_env_file(key):
    # Create .env file
    with open(".env", "w") as file:
        file.write(f"OPENAI_API_KEY={key}")

def input_key():
    # Prompt for secret key
    secret_key = input("Enter your OpenAI secret key: ")

    # Validate the key
    if secret_key and re.match(r"sk-\S+", secret_key):
        # Create .env file
        create_env_file(secret_key)
        print("Successfully created .env file with the secret key.")
        load_secret_key(secret_key)
        
    else:
        print("Invalid secret key. Please make sure it is in the correct format.")
        exit()


if __name__ == "__main__":
    if not os.path.exists(".env"):
        input_key()
    uvicorn.run(app, host="0.0.0.0", port=8000)
