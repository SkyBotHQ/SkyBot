import openai
from bot.userdata import CCT, UserData

base_prompt = "You will be supplied with a text (delimited with XML tags) about a topic.  Reply to the text in under 140 characters. "
prompt_data = {
    "emoji": "Reply with the three emojis that best match the text.  Only reply with emojis, no text.  The emojis should be exciting and vivid.",
    "question": "Reply with a short and technical one sentence question. Be very specific.  Do not be verbose.",
    "sarcastic": "Construct a sarcastic response that subtly criticizes the tweet's content. Limit your response to one punchy sentence. Use witty language and include at least one emoji for tone.",
    "enthusiastic": "Reply enthusiatistically. Be upbeat and positive. Do not be verbose, be clever. Use emojis.",
    "elaborate": "Reply with a request for more information. Ask about a specific part of the text. Use rich vocabulary and concise sentences for clarity.",
    "treasure": "Compose a reply as if it's a cryptic clue leading to a hidden treasure. Be imaginative and mysterious.",
    "answer": "Provide a short and concise answer to the question.",
    "congrats": "Reply with a short congratulations. Use a formal and commanding tone.",
    "wisdom": "Convey a reply with a nugget of wisdom or proverbial saying related to the text.",
    "abstract": "Formulate an abstract, metaphorical response to the text. Let your imagination go wild.",
    "contrary": "Challenge the central idea presented in the tweet respectfully and constructively. Your response should not exceed two sentences. Use polite and engaging language, ensure you exhibit understanding of the original tweet, and ask a thought-provoking question that indirectly challenges disagreeable points but encourages further conversation.",    "fortune": "Reply in the style of a Chinese fortune cookie. Use emoji and oriental flair.",
    "gm": """Write a short and bullish greeting.  Always start with a gm
    Answer should be short and consice.  1 sentences max, 8 words max.
    Your goal is get people insanely hyped for the day.
    Use lots of emojis and make each post visually exciting.

    Examples:
    🌟🌠 GM! Get hyped 🔑🔷 .
    🤖 gm gm gm.  let's fucking goooooo so hard🚀 .
    (🔷,🔑).  Pumping to 10000 Trillion!
    🐏🐂 Huge energy today!  Get hyped.🏋

    """,
}

async def generate_reply(tweet: str, prompt_keyword: str, context: CCT):
    openai.api_key = context.application.bot_data["OPENAI_API_KEY"]

    prompt_text = prompt_data.get(prompt_keyword, "")
    tweet_text = f"<text>{tweet}</text>"
    response = openai.Completion.create(
        model="gpt-4",
        prompt= base_prompt
        +prompt_text
        + tweet_text
        + "\n\n###\n\n",
        temperature=0.7,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"],
    )

    return response.choices[0].text.strip('"')

def generate_gm(context: CCT):
    openai.api_key = context.application.bot_data["OPENAI_API_KEY"]
    prompt = """Write a short and bullish greeting.  Always start with a gm

    Answer should be short and consice.  1 sentences max, 8 words max.
    Your goal is get people insanely hyped for the day.
    Use lots of emojis and make each post visually exciting.

    Examples:
    🌟🌠 GM! Get hyped 🔑🔷 .
    🤖 gm gm gm.  let's fucking goooooo so hard🚀 .
    (🔷,🔑).  Pumping to 10000 Trillion!
    🐏🐂 Huge energy today!  Get hyped.🏋


    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["# # #"],
    )
    return response.choices[0].text.strip('"')


def generate_hype_response(text: str, context: CCT):
    openai.api_key = bot.context.application.bot_data["OPENAI_API_KEY"]
    prompt = """Write a short and exciting reply to this message.

    Answer should be short and consice.  1 sentences max, 8 words max.
    Your goal is get people insanely hyped.
    Use lots of emojis and make each post visually exciting.

    Examples:
    🌟🌠 GM! Get hyped 🔑🔷 .
    🤖 gm gm gm.  let's fucking goooooo so hard🚀 .
    (🔷,🔑).  Pumping to 10000 Trillion!
    🐏🐂 Huge energy today!  Get hyped.🏋

    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["# # #"],
    )
    return response.choices[0].text.strip('"')
