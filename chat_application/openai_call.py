import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()
dir_path = os.path.dirname(os.path.realpath(__file__))


MOCK = True

TEMPERATURE = 0.5
MAX_TOKENS = 100
NUMBER_OF_GENERATED_QUESTIONS = 1
ENGINE = "text-davinci-003"  # text-curie-001 or text-davinci-003 are giving the best results  so far
PREPROMPT = "As an interviewer, you have conducted an interview. Your goal is to generate a follow-up question that explores new aspects or perspectives related to the interviewee's expertise while staying on the subject"
PROMPT = "Generate a follow-up question that builds upon the guest's expertise and encourages them to share unique insights or experiences, while staying within the scope of the interview topic. Generate only the question."


def load_secret_key(secret_key):
    """_summary_

    Args:
        secret_key (_type_): _description_
    """
    openai.api_key = secret_key


api_key = os.getenv("OPENAI_API_KEY")
load_secret_key(api_key)


# Define a function to call the API
def get_follow_up_question(
    json_podcast_transcript: str,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
    n=NUMBER_OF_GENERATED_QUESTIONS,
    engine=ENGINE,
    topic=None,
    pre_prompt=PREPROMPT,
    prompt=PROMPT,
    use_default_pre=True,
    use_default_prompt=True,
):
    if pre_prompt == None or pre_prompt == "" and use_default_pre:
        pre_prompt = PREPROMPT
    if prompt == None or prompt == "" and use_default_prompt:
        prompt = PROMPT

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
    if topic:
        topic = "\nThe topic of the interview is: " + topic
    else:
        topic = ""

    if not MOCK:
        response = openai.Completion.create(
            model=engine,
            prompt=f"{pre_prompt}{topic}\n{json_podcast_transcript}\n{prompt}",
            temperature=temperature,
            max_tokens=max_tokens,
            n=n,
            stop=None,
        )
    else:
        with open(os.path.join(dir_path, "MOCK.json"), "r") as f:
            print(f)
            response = json.load(f)

    print("response", response)

    generated_text = response["choices"][0].get("text", None).strip()
    print("generated_text", generated_text)
    return generated_text
