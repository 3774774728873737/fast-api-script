from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Numbers(BaseModel):
    number1: float
    number2: float

@app.post("/sum")
def calculate_sum(numbers: Numbers):
    result = numbers.number1 + numbers.number2
    return {"sum": result}
