from pydantic import BaseModel, Field, field_validator, ValidationError

class InputData(BaseModel):
    Pregnancies: float = Field(ge=0)
    Glucose: float = Field(ge=0)
    Blood_Pressure: float = Field(ge=0)
    Skin_Thickness: float = Field(ge=0)
    Insulin: float = Field(ge=0)
    BMI: float = Field(ge=0)
    Diabetes_Pedigree_Function: float = Field(gt=0)
    Age: float = Field(gt=0)

    # @field_validator('*')
    # def check_values(cls, value, field):
    #     field_name = field['field'].alias
    #     if field_name in ("Age", "Diabetes_Pedigree_Function"):
    #         if value <= 0:
    #             raise ValueError(f'{field_name} must be greater than 0')
    #     else:
    #         if value < 0:
    #             raise ValueError(f'{field_name} must be non-negative')
    #     return value
