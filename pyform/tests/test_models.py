from pydantic import BaseModel, Field, EmailStr, field_validator,  ValidationError 
from pyform.models.form_models import ModelForm

class Contact(BaseModel):
    tel: int = Field(default=None, gt=0, le=1000, title="Tel", json_schema_extra={"icon": "phone"})
    email: EmailStr = Field(default=None, title="Email", json_schema_extra={"icon": "envelope"})


class Address(BaseModel):
    lot: int = Field(default=None, gt=0, le=1000, title="Lot", json_schema_extra={"icon": "bath"})
    street: str = Field(default=None, min_length=3, max_length=36, title="Street", json_schema_extra={"icon": "address-card"})


class MyForm(ModelForm):
        name: str = Field(default=None, min_length=2, max_length=50, title="Name", description="Your name", json_schema_extra={'icon': 'user'})
        age: int = Field(default=None, gt=0, le=120, title="Age", description="Your age", json_schema_extra={'icon': 'user-clock'})        
        contact:Contact = Contact()
        address:Address = Address()

        @field_validator('age')
        @classmethod
        def age_must_be_over_30(cls, value, values):
            if value <=20:
                raise ValueError(f"must be older than {value} !")
            return value   
    
if __name__ == '__main__':
    #import asyncio
    
    addr:dict = {'lot': 52, 'street': "baker"}   
    contc:dict = {'tel': 752, 'email': "baker@gfox.com"}  
    mf:dict = {'name': "Apple", 'age':23, 'address': addr, 'contact': contc} 
    try:
        model = MyForm( **mf  ) #.model_validate( mf ) #.model_validate(mf)
        print(model.data_form())
        print()
        #print(model.json_schema)
    except ValidationError as e:
       # print(e.errors())
        print(e.json())