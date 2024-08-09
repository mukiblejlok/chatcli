import datetime
from pathlib import Path

import openai
import requests
from dotenv import load_dotenv

load_dotenv()


PROMPT = "EDRYHUUYKYKJYM"
RESULTS_FOLDER = Path(__file__).parent / "DALLE_RESULTS"
RESULTS_FOLDER.mkdir(exist_ok=True, parents=True)

client = openai.OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt=PROMPT,
    size="1024x1024",
    quality="standard",
    n=1,
)

first_response = response.data[0]

print(first_response.url, first_response.revised_prompt)

filename = (
    first_response.revised_prompt.casefold()
    .replace(",", "_")
    .replace(" ", "_")
    .replace(".", "_")[:30]
    + ".png"
)
filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + filename
filepath = RESULTS_FOLDER / filename
(RESULTS_FOLDER / filename).write_bytes(requests.get(first_response.url).content)
print(f"Saved to {(RESULTS_FOLDER / filename)}")
