
from typing import TypeVar
from secrets import token_urlsafe
from pydantic import BaseModel, Field, ConfigDict, ValidationError 
from typing import Generic, TypeVar, Optional, Dict, Any
from starlette.responses import StreamingResponse,  HTMLResponse, JSONResponse

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
                    <link rel="stylesheet" type="text/css" href="/static/site.css">
                     
                </head>
                <body> <p class="text-xs"><i class="fa fa-asterisk"></i>ModelForm with Header</p>"""
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
                yield f"""<div class="join join-vertical bg-base-100">"""
               
                for key2, value2 in self.model_json_schema().get('$defs').items():
                    yield f"""<div class="collapse collapse-arrow join-item border-base-300 border">
                        <input type="radio" name="my-accordion-0"/>                    
                        <div class="collapse-title font-semibold"> <div class="badge badge-outline badge-info ">{key2}</div></div>
                        <div class="collapse-content text-sm">""" 
                                       
                    for key3, value3 in value2.get('properties').items():
                        yield f"""<fieldset class="fieldset">        
                            <label class="label" for="{key3}">{value3.get('title')}<span class="fa fa-{value3.get('icon')}"></span>"""
                        if value3.get('type') == 'number':
                            if values:
                                yield f"""
                                    <input  class="input is_primary" type="{value3.get('type')}" step="0.001" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" value="{form.get('fields', {}).get(key3, {}).get('value')}" />"""
                            else:
                                yield f"""<input  class="input is_primary" type="number" step="0.001" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" />"""
                                                
                            if errors and form.get('fields', {}).get(key3, {}).get('error'):
                                yield f"""</label> <div class="text-xs text-red-500 font-semibold">{form.get('fields', {}).get(key3, {}).get('error')}</div></fieldset>"""
                            else:
                                yield """</label></fieldset>"""
                        # do further checks for file upload field, radio buttons, checkboxes,select fields etc...
                        else:                            
                            if values:
                                yield f""" <input  class="input is_primary" type="{value3.get('type')}" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" value="{form.get('fields', {}).get(key3, {}).get('value')}"/>"""
                            else:
                                yield f""" <input  class="input is_primary" type="{value3.get('type')}" name="{key3}" id="{key3}" placeholder="{value3.get('title')}" />"""
                                                                             
                            if errors and form.get('fields', {}).get(key3, {}).get('error'):
                                yield f"""</label><div class="text-xs text-red-500 font-semibold">{form.get('fields', {}).get(key3, {}).get('error')}</div></fieldset>"""
                            else:
                                yield """</label></fieldset>"""
                    yield """</div>"""
                yield """</div>"""                 
                    
            yield f"""<div class="field flex flex-row is-grouped mt-5">
                        <div class="control">
                            <input type="submit" class="btn btn-info rounded-md btn-sm" value="Submit"></input>
                        </div>
                        <div class="control mx-5">
                            <button class="btn btn-outline btn-sm rounded-md">Cancel</button>
                        </div>
                    </div>
                    </form>
                    </div>
                    <p class="text-xs text-blue-500 font-fine"><strong>Form Data</strong> {form}</p>"""
            if not insert: 
                yield """</body></html>"""

    
    @property        
    def model_data(self)->set:        
        return dict(self.model_dump())
    
    @property        
    def model_nested_fields(self)->list:        
        # checking for nested fields
        def_props:list = []
        if '$defs' in self.json_schema.keys():
            defs:dict = self.json_schema.get('$defs')
            def_keys:list = defs.keys()
            for m_field in def_keys:
                def_props.append(defs.get(m_field).get('properties'))
        return def_props 
        
    
    @property        
    def formfields(self)->set:  
        fields:set = set() 
        # checking for nested fields
        def_props:list = []
        if '$defs' in self.json_schema.keys():
            defs:dict = self.json_schema.get('$defs')
            def_keys:list = defs.keys()
            for m_field in def_keys:
                def_props.append(defs.get(m_field).get('properties').keys())
            nested_form_fields = set([item for row in def_props for item in row])
            return self.model_fields_set.union(nested_form_fields)
        else:
            return self.model_fields_set
        
    
    @property
    def json_schema(self):
        return self.model_json_schema()
    
    
    def data_form(self, request=None)->dict:
        pd_form:Form = Form(model=self)
        for field in self.formfields:
            pd_form.fields[field] = FormField(name=field, value=pd_form.model.model_dump().get(field))
        return pd_form.model_dump()
    
    
    def validateRequestData(self, data:dict=None):

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
            return {'ERROR': e.json()}  
                 
   
    async def validateForm(self, request=None, schema:BaseModel=None, json_data:bool=False): 
        from json import loads
        data = await request.form()
        modeled_data = schema().model_data 
        for key, value in modeled_data.items():
            if type(value) == dict:
                for key2 in value.keys():
                    if key2 in data:
                        value[key2] = data.get(key2)
                    else:
                        pass
            else:
                modeled_data[key] = data.get(key)        
        result = self.validateRequestData(data=modeled_data)
        if 'ERROR' in result: #.get('ERROR'):
            errors = loads(result.get('ERROR'))
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
            pd_form.model = schema
            form = schema()            
            form_html = form.html_form(post='/form', target="form", insert=True, form=pd_form.model_dump(), values=True, errors=True)
            return form_html
            #return pd_form #pd_form #dict(data)
        
        if json_data:
            return JSONResponse(dict(result.model_dump()))
        else:
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


if __name__ == '__main__':
    print('PyForm Auto generated  Forms ')