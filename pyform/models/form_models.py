
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Sequence, Type, List
from typing import TypeVar
from secrets import token_urlsafe
from pydantic import BaseModel, EmailStr, Field, ConfigDict, ValidationError ,field_validator
from typing import Generic, TypeVar, Optional, Dict, Any, List, Tuple, Sequence
from starlette.responses import HTMLResponse


#from pydantic.generics import GenericModel
from starlette.responses import StreamingResponse,  HTMLResponse
from starlette.requests import Request

T = TypeVar('T', bound=BaseModel)


class FormField(BaseModel):
    """A class to represent a form field"""
    name: str = None
    error: str = None
    value: Optional[Any] | None = None
    
    class Config:
        frozen = True


class Form(BaseModel, Generic[T]):
    """A class to represent a form"""
    csrf: str = token_urlsafe(16)
    fields: Dict[str, FormField]= Field(default_factory=dict)
    model: Optional[T] = None
    


class ModelForm(BaseModel):     
    model_config = ConfigDict(json_schema_extra={'icon': 'location-arrow'}) 
    
    def form_template(self,  post:str=None, target:str=None, insert:bool=False, form:Form=None, values:bool=False, errors:bool=False):
        """Returns a Jinja templated html form of the model 

        Args:
            insert (bool, optional): to insert css and icons resources or use local resources.
        """
        form_html:str =""
        for i in  self.generate_html_form(post=post, target=target, insert=insert, form=form, values=values, errors=errors):
            form_html = form_html + i
        return  form_html
    

    def html_form(self,  post:str=None, target:str=None, insert:bool=False, form:Form=None, values:bool=False, errors:bool=False):
        """Returns a html form of the model 

        Args:
            insert (bool, optional): to insert css and icons resources or use local resources.
        """
        form_html:str =""
        for i in  self.generate_html_form(post=post, target=target, insert=insert, form=form, values=values, errors=errors):
            form_html = form_html + i
        return  HTMLResponse(form_html)

    
    def stream_html_form(self, post:str=None, target:str=None, insert:bool=False, form:Form=None, values:bool=False, errors:bool=False):
        """Streams the Generated html form for the model
        Args:
            request (Request): The request object
        Returns:
            HTMLResponse: The HTML response with the form
        """
        print("Streaming form")

        return StreamingResponse( self.generate_html_form( post=post, target=target, insert=insert, form=form, values=values, errors=errors), media_type="text/html")


    def generate_html_form(self, post:str=None, target:str=None, insert:bool=False, form:Form=None, values:bool=False, errors:bool=False):
            """Generates a Html form of the instantiated model"""  
            if form:
                pass
            else:
                form = self.data_form()          
            if not insert:
                yield """<!DOCTYPE html><html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{{ title }} </title>
                    <link rel="stylesheet" href="/static/jscss/fontawesome-free-6.7.2-web/css/fontawesome.css" />
                    <link rel="stylesheet" href="/static/jscss/fontawesome-free-6.7.2-web/css/brands.css" />
                    <link rel="stylesheet" href="/static/jscss/fontawesome-free-6.7.2-web/css/solid.css" />
                    <link rel="stylesheet" href="/static/jscss/fontawesome-free-6.7.2-web/css/svg-with-js.css" />
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css">
                    <link rel="stylesheet" type="text/css" href="/static/site.css">
                     
                </head>
                <body> <p>ModelForm</p><i class="fa fa-asterisk"></i>"""
            if post and target:
                yield f"""<div style="margin:50px;"><form method="POST" hx-post="{post}" hx-target="#{target}">"""
            else:
                yield """<div style="margin:50px;"><form method="POST">"""
            yield f"""          
                <input type="hidden" name="csrf" value="{form.get('csrf')}" />"""
            yield f""" <h3 class="title is-4">{ self.model_json_schema().get('title')}</h3> """
            
            for key, value in self.model_json_schema().get('properties').items():                
                if value.get('$ref'):
                    pass
                else:
                    yield f""" <fieldset class="fieldset">
                            <!--legend class="fieldset-legend">{value.get('title')}</legend-->
                            
                    
                    <label class="label" for="{key}">{value.get('title')}<span class="fa fa-{value.get('icon')}"></span>"""
                    if value.get('type') == 'number':                        
                        if values:
                            yield f""" <input class="input is_primary" type="number" step="0.001" name="{key}" id="{key}" placeholder="{value.get('title')}" value="{form.get('fields', {}).get(key, {}).get('value')}" />"""
                        else:
                            yield f""" <input class="input is_primary" type="number" step="0.001" name="{key}" id="{key}" placeholder="{value.get('title')}"  />"""
                       
                        if errors and form.get('fields', {}).get(key, {}).get('error'):
                            yield f"""</label> <div class="text-xs text-red-500 font-semibold">{form.get('fields', {}).get(key, {}).get('error')}</div></fieldset>"""
                        else:
                            yield """</label></fieldset>"""
                        ## if value.validation_error:
                            # yield f""" <span class="is-size-7 has-text-danger has-text-weight-bold">{value.get(errors)[0]}</span>
                    # do further checks for file upload field, radio buttons, checkboxes,select fields etc...
                    else:
                        
                        if values:
                            yield f""" <input class="input is_primary" type="{value.get('type')}" name="{key}" id="{key}" placeholder="{value.get('title')}" value="{form.get('fields', {}).get(key, {}).get('value')}" />"""
                        else:
                            yield f""" <input class="input is_primary" type="{value.get('type')}" name="{key}" id="{key}" placeholder="{value.get('title')}"  />"""
                                         
                        if errors and form.get('fields', {}).get(key, {}).get('error'):
                            yield f"""</label> <div class="text-xs text-red-500 font-semibold">{form.get('fields', {}).get(key, {}).get('error')}</div></fieldset>"""
                        else:
                            yield """</label></fieldset>"""
            # process the nested fields
            if self.model_json_schema().get('$defs'):
                yield f"""<ul uk-accordion>"""
                for key2, value2 in self.model_json_schema().get('$defs').items():
                    yield f""" <li><a class="uk-accordion-title" href>{key2}</a>
                    <div class="uk-accordion-content">"""                    
                    for key3, value3 in value2.get('properties').items():
                        yield f"""<div class="field">        
                            <label class="label" for="{key3}">{value3.get('title')}</label>"""
                        if value3.get('type') == 'number':
                            yield f"""<div class="control has-icons-left"> """
                            if values:
                                yield f"""
                                    <input  class="input is_primary" type="{value3.get('type')}" step="0.001" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" value="{form.get('fields', {}).get(key3, {}).get('value')}" />"""
                            else:
                                yield f"""<input  class="input is_primary" type="number" step="0.001" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" />"""
                                                
                            if errors and form.get('fields', {}).get(key3, {}).get('error'):
                                yield f""" <div class="text-xs text-red-500 font-semibold">{form.get('fields', {}).get(key3, {}).get('error')}</div></div>"""
                            else:
                                yield """</div>"""
                        # do further checks for file upload field, radio buttons, checkboxes,select fields etc...
                        else:
                            yield f"""<div class="control has-icons-left">"""
                            if values:
                                yield f""" <input  class="input is_primary" type="{value3.get('type')}" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" value="{form.get('fields', {}).get(key3, {}).get('value')}"/>"""
                            else:
                                yield f""" <input  class="input is_primary" type="{value3.get('type')}" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" />"""
                            
                            yield f""" <span class="icon is-small is-left">
                            <i class="fas fa-{value3.get('icon')}"></i>
                            </span>"""                      
                            if errors and form.get('fields', {}).get(key3, {}).get('error'):
                                yield f""" <div class="text-xs text-red-500 font-semibold">{form.get('fields', {}).get(key3, {}).get('error')}</div></div>"""
                            else:
                                yield """</div>"""
                    yield """</div></li>"""
                yield """</ul>"""                 
                    
            yield f"""<div class="field is-grouped mt-5">
                    <div class="control has-icons-left">
                        <input type="submit" class="btn btn-primary" value="Submit"></input>
                    </div>
                    <div class="control has-icons-left">
                        <button class="btn btn-soft btn-warning">Cancel</button>
                    </div></div></form></div><p class="text-xs text-blue-500 font-semibold">{form}</p>"""
            if not insert: 
                yield """</body></html>"""
    
    @property        
    def fields(self)->set:        
        return self.model_fields_set
    
    @property
    def json_schema(self):
        return self.model_json_schema()
    
    
    def data_form(self, request=None)->dict:
        pd_form:Form = Form(model=self)
        for field in self.fields:
            pd_form.fields[field] = FormField(name=field, value=pd_form.model.model_dump().get(field))
        return pd_form.model_dump()
    
    
    def validateRequestForm(self, data:dict=None):
        """Validates data returned from the request object
        expected form data ex. 
        FormData([('csrf', 'DEc3T68GVHgelV8SW5UZBA'), ('name', 'Mar a Largo'), ('age', '52')])
        Args:
            request (_type_, optional): _description_. Defaults to None.
        Returns:
            _type_: _description_
        """
        try:
            model:BaseModel = self.model_validate( data ) #.model_validate(mf)
            return model
        except ValidationError as e:
        # print(e.errors())
            #for i in e.json():
            #    print('ERROR', i)
            return {'ERROR': e.json()}  
                 
    async def validateForm(self, request=None, schema:BaseModel=None): 
        import json
        data = await request.form()
        result = self.validateRequestForm(data=data)
        if 'ERROR' in result: #.get('ERROR'):
            errors = json.loads(result.get('ERROR'))
            pd_form:Form = Form()
            data = dict(data)
            for key, value in data.items():
                if key == 'csrf':
                    pass
                else:
                    for err in errors:
                        if key in err.get('loc'):
                            pd_form.fields[key] = FormField(name=key, error=err.get('msg') ,value=value)
                        else:
                            pd_form.fields[key] = FormField(name=key, value=value)
            pd_form.csrf = data.get('csrf')
            form = schema()
            #data_form = form.data_form(request=request)
            form_html = form.html_form(post='/form', target="form", insert=True, form=pd_form.model_dump(), values=True, errors=True)
            return form_html
            #return pd_form #pd_form #dict(data)
        return HTMLResponse(f"""<div class="card w-96 bg-base-100 card-xs shadow-sm">
                                    <div class="card-body">
                                        <h2 class="card-title">Data Exchange</h2>
                                        <p>{result}</p>
                                        <p class="text-xs text-blue-500">{data}</p>
                                        
                                        <div class="justify-end card-actions">
                                        <button class="btn btn-success btn-sm">Success</button>
                                        </div>
                                    </div>
                                </div>""")


class Address(BaseModel):
    lot: int = Field(default=None, gt=0, le=1000, title="Lot", json_schema_extra={"icon": "bath"})
    street: str = Field(default=None, min_length=3, max_length=36, title="Street", json_schema_extra={"icon": "address-card"})


class MyForm(ModelForm):
        name: str = Field(default=None, min_length=2, max_length=50, title="Name", description="Your name", json_schema_extra={'icon': 'user'})
        age: int = Field(default=None, gt=0, le=120, title="Age", description="Your age", json_schema_extra={'icon': 'user-clock'})        
        address:Address = Address()

        @field_validator('age')
        @classmethod
        def age_must_be_over_30(cls, value, values):
            if value <=20:
                raise ValueError(f"Age must be older than {value} !")
            return value
      
    
    
if __name__ == '__main__':
    #import asyncio
    
    addr:dict = {'lot': 52, 'street': "baker road"}     
    mf:dict = {'name': "Apple", 'age':23, 'address': addr} 
    try:
        model = MyForm.model_validate( mf ) #.model_validate(mf)
        print(model.data_form())
        print()
        print(model.json_schema)
    except ValidationError as e:
       # print(e.errors())
        print(e.json())