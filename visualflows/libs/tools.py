from fastapi import HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import io
import sys
import contextlib
import traceback

class RunCodeModel(BaseModel):
    code:str = "print('hello world')"

def run_code_with_error(config:RunCodeModel):
    try:
        try:
            print(config.code)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(config.code.replace('\r',''))
            captured_output = output.getvalue()
            print(captured_output)
            return PlainTextResponse(f"Success: {captured_output}")
        except Exception as e:
            return PlainTextResponse(f"Failure:\n{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))