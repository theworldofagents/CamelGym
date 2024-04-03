
from camelgym.provider.openai_api import OpenAIGPTAPI as LLM

DEFAULT_LLM = LLM()

async def ai_func(prompt):

    return await DEFAULT_LLM.aask(prompt)
