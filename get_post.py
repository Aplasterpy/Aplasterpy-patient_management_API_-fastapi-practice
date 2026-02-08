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
    allergies: Annotated[Optional[list[str]], Field(default=None, description="Enter the Patient Allergies")]
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
# Create the pydantic class for the patient update data
class patient_update_data(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0, lt=100)
    gender: Optional[Literal['male', 'female', 'other']] = None
    email: Optional[EmailStr] = None
    contact_no: Optional[int] = None
    address: Optional[address_data] = None
    addhaar: Optional[UDI_check] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    allergies: Optional[list[str]] = None
    married_status: Optional[bool] = None
    smoking_habbit: Optional[bool] = None

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
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
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
    pid = patient.id.lower()

    if pid in data:
        raise HTTPException(status_code=400, detail='User ID is already exists')

    data[pid] = patient.model_dump(exclude=['id'])
    data_store(data)

    return JSONResponse(status_code=201, content={"message": "Patient data created successfully"})
    
# Create the Update route for the update data - put method
@app.put("/update/{patient_id}")
def updated_data(patient_id: str, updated_patient: patient_update_data):
    # load the data
    data = load_data()
    patient_id = patient_id.lower()
    # check the data is exist or not
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient ID not found!')
    # exixting patient data [it in a dict format data]
    existing_patient_data =data[patient_id]
    # convert pydantic model to dict using model_dump() [Becasue existing data is in dict format
    # and updated data is in pydantic model format] 
    updated_patient_data = updated_patient.model_dump(exclude_unset=True)
    # store the updated data into the existing data using key and value. key basically target the id
    for key, value in updated_patient_data.items():
        existing_patient_data[key] = value
    # existing patient data convert into pydantic model for update the BMI and verdict
    # and then again convert pydantic model to dict for update the data in json file also 
    # add the id in the patient_data [main model] [Becasue the id is missing in the updated patient model]
    existing_patient_data['id'] = patient_id
    # pydantoc object creation in the main model.
    updated_patient_pydantic_obj = patient_data(**existing_patient_data)
    updated_patient_dict = updated_patient_pydantic_obj.model_dump(exclude=['id'])
    # add this dict to data
    data[patient_id] = updated_patient_dict
    # save the model
    data_store(data)
    return JSONResponse(status_code=200, content={"message": "Patient data updated successfully"})
# Create the delete route for the delete data - delete method
@app.delete("/delete/{patient_id}")
def delete_data(patient_id: str):
    data = load_data()
    if patient_data not in data:
        raise HTTPException(status_code=404, detail = 'Patient ID not found!')
    
    # if data is exist, delete the data
    del data[patient_id]   
    data_store(data)
    # after delete the data, return the success message
    raise HTTPException(status_code=200, detail="Patient data deleted successfully!")

# Create the patch route for the update data - patch method
@app.patch("/edit/{patient_id}")
def patch_update_data(patient_id: str, updated_patient: patient_update_data):
    # load the data
    data =load_data()
    # Check the patient id in exists or not
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient ID not found!')
    existing_patient_data = data[patient_id]
    
    update_patient_data = updated_patient.model_dump(exclude_unset=True)
    
    for key, value in update_patient_data.items():
        existing_patient_data[key] = value
        
    updated_patient_obj = patient_data(id=patient_id, **existing_patient_data)
    updated_patient_data_dict = updated_patient_obj.model_dump(exclude=['id'])
    data[patient_id] = updated_patient_data_dict
    
    # save the data
    data_store(data)
    return JSONResponse(status_code=200, content={"message": "patient data updated successfully!"})