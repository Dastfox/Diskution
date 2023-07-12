
import os
import openai
from dotenv import load_dotenv

load_dotenv()
dir_path = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(os.path.join(dir_path, "./.env")):
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key

TEMPERATURE = 0.5
MAX_TOKENS = 60
NUMBER_OF_GENERATED_QUESTIONS = 1
ENGINE = "text-curie-001" # text-curie-001 or text-davinci-003 are giving the best results  so far
PREPROMPT = "As an interviewer, you have conducted an interview. Your goal is to generate a follow-up question that explores new aspects or perspectives related to the interviewee's expertise while staying on the subject"
# PROMPT = "Generate a follow-up question that makes the guest develop them last answer. Generate only the question."
PROMPT = "Generate a follow-up question that builds upon the guest's expertise and encourages them to share unique insights or experiences, while staying within the scope of the interview topic. Generate only the question."
# Load secret key from the env
# if os.path.exists(os.path.join(dir_path, "./.env")):
#     secret_key = dotenv.load_dotenv(os.path.join(dir_path, "./.env")).get("OPENAI_API_KEY")

def load_secret_key(secret_key):
    """_summary_

    Args:
        secret_key (_type_): _description_
    """
    openai.api_key = secret_key
    



# Define a function to call the API
def get_follow_up_question(json_podcast_transcript: str, temperature=TEMPERATURE, max_tokens=MAX_TOKENS, n=NUMBER_OF_GENERATED_QUESTIONS, engine=ENGINE, topic= None):
    print(dir_path)
    
    """_summary_

    Args:
        json_podcast_transcript (_type_): _description_
        temperature (_type_, optional): _description_. Defaults to TEMPERATURE.
        max_tokens (_type_, optional): _description_. Defaults to MAX_TOKENS.
        n (_type_, optional): _description_. Defaults to NUMBER_OF_GENERATED_QUESTIONS.
        engine (_type_, optional): _description_. Defaults to ENGINE.

    Returns:
        _type_: _description_
    """
    print(locals()  )
    if topic:
        topic = "The topic of the interview is: " + topic
    
    
    
    response = openai.Completion.create(
        engine=engine,
        prompt=f"{PREPROMPT}\n{topic}\n{json_podcast_transcript}\n{PROMPT}",
        temperature=temperature,
        max_tokens=max_tokens,
        n=n,
        stop=None,
    )

    generated_text = response.choices[0].get("text", None).strip()
    mock_generated_text = "What is your favorite color?"
    if topic:
        print("prompt", f"{PREPROMPT}\n{topic}\n{json_podcast_transcript}\n{PROMPT}\n GIVING: \n ",mock_generated_text)
    else:
        print("prompt", f"{PREPROMPT}\n{json_podcast_transcript}\n{PROMPT}\n GIVING: \n ",mock_generated_text)
    return mock_generated_text
