from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse, StreamingResponse
# from langchain.llms import HuggingFaceTextGenInference
from langchain_community.llms import Ollama, HuggingFaceTextGenInference
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from state import read_state, write_state, get_state


class OllamaModel(BaseModel):
    identifier: str
    model:str
    num_gpu:int =-1
    temperature:float =0.01
    max_new_tokens: int = 512
    stop_sequences:str = "</s>"

class HFHostedInferenceModel(BaseModel):
    identifier: str
    hf_name: str
    hf_token: str = None
    temperature: float = 0.01
    max_new_tokens: int = 512
    stop_sequences: str = "</s>"

class RunPromptModel(BaseModel):
    identifier: str
    prompt: str

async def load_ollama_model(config: OllamaModel):
    try:
        print(str(config))
        llm = Ollama(
            model=config.model,
            callbacks=[StreamingStdOutCallbackHandler()],
            temperature=config.temperature,
            num_ctx=config.max_new_tokens,
            stop=config.stop_sequences.split(","),
        )
        states = read_state("objects")
        states[config.identifier] = llm
        write_state("objects", states)
        print(get_state())
        return PlainTextResponse(config.identifier)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def load_hf_hosted_model(config: HFHostedInferenceModel):
    try:
        llm = HuggingFaceTextGenInference(
            inference_server_url=f"https://api-inference.huggingface.co/models/{config.hf_name}",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            temperature=config.temperature + 0.001,
            max_new_tokens=config.max_new_tokens,
            stop_sequences=config.stop_sequences.split(","),
        )
        llm.client.headers = {"Authorization": f"Bearer {config.hf_token}"}
        states = read_state("objects")
        states[config.identifier] = llm
        write_state("objects", states)
        return PlainTextResponse(config.identifier)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def run_prompt(config: RunPromptModel):
    try:
        print(get_state())
        x= read_state("objects")[
            config.identifier.replace('"', "")
        ].predict(config.prompt)
        return PlainTextResponse(x)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))