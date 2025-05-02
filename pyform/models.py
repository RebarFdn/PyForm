
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Sequence, Type, List
from typing import TypeVar
from secrets import token_urlsafe
from pydantic import BaseModel, EmailStr, Field, ConfigDict, ValidationError ,field_validator
from typing import Generic, TypeVar

import pydantic

#from pydantic.generics import GenericModel
from starlette.responses import StreamingResponse,  HTMLResponse
from starlette.requests import Request



class Form(BaseModel):
    csrf: str | None = None

form = Form(csrf = "xxe33tf-GB")


class ModelForm(BaseModel):     
    model_config = ConfigDict(json_schema_extra={'icon': 'location-arrow'})  

    
    def form_template(self,  post:str=None, target:str=None, insert:bool=False):
        """Returns a Jinja templated html form of the model 

        Args:
            insert (bool, optional): to insert css and icons resources or use local resources.
        """
        form_html:str =""
        for i in  self.generate_html_form(post=post, target=target, insert=insert):
            form_html = form_html + i
        return  form_html
    

    def html_form(self,  post:str=None, target:str=None, insert:bool=False):
        """Returns a html form of the model 

        Args:
            insert (bool, optional): to insert css and icons resources or use local resources.
        """
        form_html:str =""
        for i in  self.generate_html_form(post=post, target=target, insert=insert):
            form_html = form_html + i
        return  HTMLResponse(form_html)

    
    def stream_html_form(self, post:str=None, target:str=None, insert:bool=False):
        """Streams the Generated html form for the model
        Args:
            request (Request): The request object
        Returns:
            HTMLResponse: The HTML response with the form
        """
        print("Streaming form")

        return StreamingResponse( self.generate_html_form( post=post, target=target, insert=insert), media_type="text/html")


    def generate_html_form(self, post:str=None, target:str=None, insert=False, form=form):
            """Generates a Html form of the instantiated model"""            
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
                <body>"""
            if post and target:
                yield f"""<div style="margin:50px;"><form method="POST" hx-post="{post}" hx-target="#{target}">"""
            else:
                yield """<div style="margin:50px;"><form method="POST">"""
            yield f"""          
                <input type="hidden" name="csrf" value="{form.csrf}" />"""
            yield f""" <h3 class="title is-4">{ self.model_json_schema().get('title')}</h3> """
            
            for key, value in self.model_json_schema().get('properties').items():                
                if value.get('$ref'):
                    pass
                else:
                    yield f""" <div class="field">    
                    <label class="label" for="{key}">{value.get('title')}</label>"""
                    if value.get('type') == 'number':
                        yield f"""<div class="control has-icons-left">
                        <input class="input is_primary" type="{value.get('type')}" step="0.001" name="{key}" id="{key}" placeholder="{value.get('title')}" value="{{form.fields[{key}].value}}" />
                         <span class="icon is-small is-left">
                            <i class="fas fa-{value.get('icon')}"></i>
                        </span>                      
                         <div id="error"></div>
                        </div>                        
                        """
                        ## if value.validation_error:
                            # yield f""" <span class="is-size-7 has-text-danger has-text-weight-bold">{value.get(errors)[0]}</span>
                    # do further checks for file upload field, radio buttons, checkboxes,select fields etc...
                    else:
                        yield f"""<div class="control has-icons-left"> <input class="input is_primary" type="{value.get('type')}" name="{key}" id="{key}" placeholder="{value.get('title')}" value="{{form.fields[{key}].value}}" />
                        <span class="icon is-small is-left">
                            <i class="fas fa-{value.get('icon')}"></i>
                        </span>                      
                         <div id="error"></div>
                        </div>"""
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
                            yield f"""<div class="control has-icons-left"> <input  class="input is_primary" type="{value3.get('type')}" step="0.001" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" value="{{form.fields[{key3}].value}}" />
                            <span class="icon is-small is-left">
                            <i class="fas fa-{value3.get('icon')}"></i>
                            </span>                      
                             <div>{{ form.fields.[{key3}].error }}</div>
                            </div>"""
                        # do further checks for file upload field, radio buttons, checkboxes,select fields etc...
                        else:
                            yield f"""<div class="control has-icons-left"> 
                            <input  class="input is_primary" type="{value3.get('type')}" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" value="{{form.fields[{key3}].value}}"/>
                            <span class="icon is-small is-left">
                            <i class="fas fa-{value3.get('icon')}"></i>
                            </span>
                             <div>{{ form.fields.[{key3}].error }}</div>
                            </div>
                                   
                            """
                    yield """</div></li>"""
                yield """</ul>"""                 
                    
            yield f"""<div class="field is-grouped uk-margin-top">
                    <div class="control has-icons-left">
                        <input type="submit" class="btn btn-primary" value="Submit"></input>
                    </div>
                    <div class="control has-icons-left">
                        <button class="button is-link is-light">Cancel</button>
                    </div></div></form></div>"""
            if not insert: 
                yield """</body></html>"""
    
    @property        
    def fields_set(self)->set:
        return self.model_fields_set
    
    @property
    def json_schema(self):
        return self.model_json_schema()
    
    
    async def form(self, request=None):
        pyd_form = await PydanticForm.create(request, ModelForm)
        return pyd_form
    
    async def validateForm(self, request=None):
        form = await PydanticForm.validate_request(request, ModelForm)
        return form
        
        

class MyForm(ModelForm):
        name: str = Field(default=None, min_length=2, max_length=50, title="Name", description="Your name", icon="user")
        age: int = Field(default=None, gt=0, le=120, title="Age", description="Your age", icon="user-clock")
        

        @field_validator('age')
        @classmethod
        def age_must_be_over_30(cls, value, values):
            if value <=20:
                raise ValueError("30's are your new 20's")
            return value
      
    
    
if __name__ == '__main__':
    import asyncio
    
        
    mf:dict = {'name': "Apple", 'age':29} 
    try:
        model = MyForm( **mf ) #.model_validate(mf)
        print(model.model_dump())
    except ValidationError as e:
       # print(e.errors())
        print(e.json())