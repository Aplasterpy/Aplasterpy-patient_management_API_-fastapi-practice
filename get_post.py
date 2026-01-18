# Import necessary modules
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field
from fastapi.responses import JSONResponse
from typing import Literal, Optional, Annotated
from UDI import UDI_check
import json

# Create FastAPI app instance
app = FastAPI()

# Create 'Address' pydantic model for nested address data
class address_data(BaseModel):
    home: Annotated[str, Field(..., description="Enter the Home Address", example="123 Main St")]
    city: Annotated[str, Field(..., description="Enter the City", example="New York")]
    pin_code: Annotated[int, Field(..., description="Enter the Pin Code", example=10001)]
    Country: Annotated[str, Field(..., description="Enter the Country", example="USA")]


# Create 'patient_data' Pydantic model for data modeling
class patient_data(BaseModel):
    id: Annotated[str, Field(..., description="Enter the Patient ID", example="p001")]
    name: Annotated[str, Field(..., description="Enter the Patient Name", example="John Doe")]
    age: Annotated[int, Field(..., gt=0, lt=100, description="Enter the Patient Age", example=25)]
    gender: Annotated[Literal['male', 'female', 'other'], Field(..., description="Enter the Patient Gender", example="male")]
    email: Annotated[EmailStr, Field(..., description="Enter the Patient Email", example="username@oksbi.com")]
    contact_no: Annotated[int, Field(..., description="Enter the Patient Contact Number", example=1234567890)]
    address: address_data
    addhaar: UDI_check
    height: Annotated[float, Field(..., description="Enter the Patient Height in cm", example=175.5)]
    weight: Annotated[float, Field(..., description="Enter the Patient Weight in kg", example=70.5)]
    allergies: Annotated[list[str], Field(default=None, description="Enter the Patient Allergies", example=["peanuts", "pollen", "dust"])]
    married_status: Annotated[Optional[bool], Field(description="Enter the Patient Marital Status", example=True)] =None
    smoking_habbit: Annotated[Optional[bool], Field(description="Enter the Patient Smoking Habbit", example=False)] =None

    # Age validate - already done
    # Email validate
    @field_validator('email')
    @classmethod
    def email_validator(cls, value):
        domain_name_list = ['oksbi.com', 'icici.com', 'hdfc.com', 'axis.com']
        if value.split('@')[1] not in domain_name_list:
            raise ValueError(f"Use workig mail only, Valid mail domain should be {domain_name_list}")
        return value
    # Bmi calculate
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round((self.weight/ (self.height/100)**2),2)
        return bmi
    # Verdict calculate
    @computed_field
    @property
    def verdict_calculate(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        if self.bmi >= 18.5 and self.bmi < 24.9:
            return "Normal"
        if self.bmi >= 25 and self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

# Function to display patient data
def display_patient_data(patient_data=patient_data):
    print("Patient ID:", patient_data.id)
    print("Patient Name:", patient_data.name)
    print("Patient Age:", patient_data.age)
    print("Patient Gender:", patient_data.gender)
    print("Patient Email:", patient_data.email)    
    print("Patient Contact:", patient_data.contact_no)
    print("Patient Address:", patient_data.address)
    print("Patient Height:", patient_data.height)    
    print("Patient Weight:", patient_data.weight)
    print("Patient Allergies:", patient_data.allergies)
    print("Patient Married Status:", patient_data.married_status)
    print("Patient Smoking Habit:", patient_data.smoking_habbit)
    
# Create the json data load function 
def load_data():
    try:
        with open('post_data.json', 'r') as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        return {}

# Create the json data store/add function
def data_store(data: dict):
    with open('post_data.json', 'w') as s:
        # data = json.load(data, s)
        data = json.dump(data, s)

# create the get route for the view all data
@app.get("/view")
def view_data():
    return load_data()

# Create the get route for the view single data
@app.get("/view/{id}")
def view_single_data(id: str = Path(..., description="Enter the Patient ID", example="p001")):
    data = load_data()
    id = id.lower()
    if id in data:
        return data[id]
    raise HTTPException(status_code=404, detail="Patient ID not found...")

# Create the get route for the sorted data
@app.get("/sort_data")
def sortdata(sort_by: str = Query(..., description="Sort by height or weight or bmi", example="height"),
             order_by: str = Query(description="Sort by ascending or descending", example="asc")):
    sort_by_data = ['height', 'weight', 'bmi']
    order_by_data = ['asc', 'desc']
    data = load_data()
    # Logic for the sorting data
    if sort_by not in sort_by_data:
        raise HTTPException(status_code=400, detail= f'Invalid sort_by parameter, It must be one of the {sort_by_data}')
    if order_by not in order_by_data:
        raise HTTPException(status_code=400, detail=f'Invalid order by parameter, It must be one of the {order_by_data}. Defaul value is ascending')
    rev_data = True if order_by == 'desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=rev_data)
    return sorted_data
    
# Create the post route for the create data
@app.post("/add_data")
def add_data(patient: patient_data):
    data = load_data()
    id = patient.id.lower()
    if patient.id in data: 
        raise HTTPException(status_code=400, detail='User ID is already exists')
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    # Save or add the data into the json file.
    data_store(data)
    return JSONResponse(status_code=201, content={"message": "Patient data created successfully"})
    
# Create the put route for the update data

# Create the delete route for the delete data

# Create the patch route for the update data
