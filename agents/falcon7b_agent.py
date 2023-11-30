#!/bin/python
""" falcon7b_agent.py
The falcon-7b-instruct model used for the AI-Agent
"""
import logging
import asyncio
from aiagent import AIAgent

from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch



# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


# Setup the model once (implicit singleton ;-)
MODEL_ID = "tiiuae/falcon-7b-instruct"
TOKENIZER = AutoTokenizer.from_pretrained(MODEL_ID)
MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto")
#MODEL.config.pad_token_id = model.config.eos_token_id # suppress eos_token_id warning

PIPELINE = transformers.pipeline(
    "text-generation",
    model=MODEL,
    tokenizer=TOKENIZER,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)


class Falcon7BAgent(AIAgent):
    """Accesses the falcon-7b-instruct model via Transformers, will keep track of the context"""
    def __init__(self) ->None:
        super().__init__()
        self.qa_count = 0
        logger.info("Initialize %s", MODEL_ID)


    def system(self, content :str):
        """Starts with a new context (a reset), and provides the chat-systems general behavior"""
        logger.info("Set Falcon7BAgent system context:%s", content)
        self.messages = []
        self.messages.append( content )

    def advice(self, question :str, answer :str) ->None:
        """Provides context with a predefined question-answer pair """
        logger.info("Advice Falcon7BAgent Question:'%s', Answer:'%s'", question, answer)
        self.qa_count += 1
        if not question is None:
            self.messages.append( f"Q{self.qa_count}: {question}")
        if not answer is None:
            self.messages.append( f"A{self.qa_count}: {answer}" )

    def ask(self, prompt :str) ->str:
        """Sends a prompt, will track the result in the context"""
        self.result = None
        logger.info("Ask Falcon7BAgent '%s'", prompt)
        self.qa_count += 1
        self.messages.append( f"Q{self.qa_count}: {prompt}" )
        sequences = PIPELINE(
            prompt,
            max_length=200,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=TOKENIZER.eos_token_id
        )
        result = ""
        for seq in sequences:
            result += seq['generated_text'] + "\n"

        self.result = result
        self.messages.append( f"A{self.qa_count}: {result}" )
        return result


# Usage
async def main():
    """Async main function"""

    agent = Falcon7BAgent()
    agent.system("You are a helpful assistant.")
    agent.advice(
        "Who won the world series in 2020?",
        "The Los Angeles Dodgers won the World Series in 2020."
    )
    #print( await aiagent.ask("Where was it played?") )

    # A demo for asynchronous programming
    task = asyncio.create_task(agent.ask_async("Where was it played?"))
    print("Waiting for the answer...")  # do other stuff...
    print( await task )


if __name__ == "__main__":
    ### Synchronous Call ###
    agent2 = Falcon7BAgent()
    agent2.system("You are a player of the famous card game 'Werwölfe vom Düsterwald'")
    print( agent2.ask("Tell me the rules of the game.") )

    ### Asynchronous Call ###
    asyncio.run(main())
