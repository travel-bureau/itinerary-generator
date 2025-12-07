import os

import openai

from utils.redis_bot import load_chatgpt_cache, save_chatgpt_cache, delete_chatgpt_cache


def initialize_chatgpt():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY

# ======= ChatGPT Enhancement =======
def enhance_itinerary_with_chatgpt(itinerary_text, cache_flag=True):
    if cache_flag:
        chatgpt_cache = load_chatgpt_cache(itinerary_text)

        """Return enhanced itinerary with packing checklist and tips."""
        if chatgpt_cache:
            return chatgpt_cache
    else:
        delete_chatgpt_cache(itinerary_text)

    prompt = f"Convert the following travel itinerary into a detailed, user-friendly, structured version with day-wise highlights, engaging descriptions, travel tips, local experiences, and a packing checklist at the end.\n\n{itinerary_text}"
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a professional travel planner AI. "
                        "Your responses must follow this exact structure:\n\n"
                        "Travel Itinerary: [Brief description of itinerary]\n"
                        "Primary Traveller Name: [Name of the traveller in which this itinerary is booked]\n"
                        "Travel Dates: [From and to dates in DD-MMM-YYYY format]\n"
                        "Travelers: [Brief description of all travelers with any given info about travelers]\n"
                        "Day n: [Brief about the day's event]\n"
                        "Day wise highlights, travel tips and local experience (if any) if relevant\n"
                        "Packaging checklist: [List of recommended items to pack]\n\n"
                        "Do not include any extra commentary or headings. Just return the structured response."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=int(len(itinerary_text) * 1.5)
        )
        text = resp.choices[0].message.content
        save_chatgpt_cache(itinerary_text, text)
        return text
    except Exception as e:
        return itinerary_text + "\n\n(Note: ChatGPT enhancement failed)"
