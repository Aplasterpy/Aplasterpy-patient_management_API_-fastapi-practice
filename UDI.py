# import neccessary Liberies
from pydantic import BaseModel, Field, field_validator
from typing import Annotated


# Verhoeff Table
_d = [
    [0,1,2,3,4,5,6,7,8,9],
    [1,2,3,4,0,6,7,8,9,5],
    [2,3,4,0,1,7,8,9,5,6],
    [3,4,0,1,2,8,9,5,6,7],
    [4,0,1,2,3,9,5,6,7,8],
    [5,9,8,7,6,0,4,3,2,1],
    [6,5,9,8,7,1,0,4,3,2],
    [7,6,5,9,8,2,1,0,4,3],
    [8,7,6,5,9,3,2,1,0,4],
    [9,8,7,6,5,4,3,2,1,0]
]

_p = [
    [0,1,2,3,4,5,6,7,8,9],
    [1,5,7,6,2,8,3,0,9,4],
    [5,8,0,3,7,9,6,1,4,2],
    [8,9,1,6,0,4,3,5,2,7],
    [9,4,5,3,1,2,6,8,7,0],
    [4,2,8,6,5,7,3,9,0,1],
    [2,7,9,3,8,0,6,4,1,5],
    [7,0,4,6,9,1,3,2,5,8]
]

def is_valid_aadhaar(number: str) -> bool:
    c = 0
    for i, digit in enumerate(reversed(number)):
        c = _d[c][_p[i % 8][int(digit)]]
    return c == 0


class UDI_check(BaseModel):
    aadhar: Annotated[str, Field(..., description="Enter the Aadhar Number", example="123456789012")]
    
    @field_validator("aadhar")
    @classmethod
    def validate_aadhar(cls, value):
        # R1: Only Digit
        if not value.isdigit():
            raise ValueError("Aadhar Number must contain only digits")
        # R2: 12 Digits
        if len(value) != 12:
            raise ValueError("Aadhar Number must be 12 digits long")
        # R3: First digit 2–9 (UIDAI rule)
        if value[0] not in "23456789":
            raise ValueError("Aadhar Number must start with a number between 2 and 9")
        # R4: Valid Verhoeff checksum
        if not is_valid_aadhaar(value):
            raise ValueError("Aadhar Number is not valid")
        return value
# UDI_instance = UDI_check(aadhar="234567890123")

# export as a model file or json file in pydantic
# UDI_check_model = UDI_instance.model_dump_json()
# print(UDI_check_model)