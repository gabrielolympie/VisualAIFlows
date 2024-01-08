from state import read_state, write_state, get_state
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi import HTTPException
from pydantic import BaseModel
from faster_whisper import WhisperModel

class WhisperConfigModel(BaseModel):
    identifier:str
    model_version:str ='base'
    device:str ='cpu'
    precision:str ='int8'


async def load_whisper(config: WhisperConfigModel):
    print(config.model_version)
    try:
        whisper = WhisperModel(
            config.model_version, 
            device=config.device,
            compute_type=config.precision,
            cpu_threads=16,
            download_root='./downloads'
        )
        states = read_state("objects")
        states[config.identifier] = whisper
        write_state("objects", states)
        return PlainTextResponse(config.identifier)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TranscribeConfig(BaseModel):
    identifier: str='whisper'
    path_to_audio:str=None


async def transcribe(config: TranscribeConfig):
    try:
        segments, info = read_state("objects")[config.identifier].transcribe(config.path_to_audio, beam_size=1)
        transcription=[]
        for segment in segments:
            t=segment.text
            transcription.append(t)
            print(t)

        return PlainTextResponse("\n".join(transcription))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))