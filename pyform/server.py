from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_wtf import CSRFProtectMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, HTMLResponse

from config import STATIC_PATH, Path, NETWORK_CONFIG, TEMPLATES
from models import ModelForm, MyForm

async def homepage(request):
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


async def getpostform(request):
    if request.method == 'POST':
        data = await request.form()
        model = MyForm(**data)
        return HTMLResponse(f"""<div>{model}</div>""")
    else:
        form = MyForm()
        data_form = form.form(request=request)
        form_html = form.html_form(post='/form', target="form", insert=True, form=data_form)
        return form_html
        
        

router = [
    Route("/", homepage),
    Route("/form", getpostform, methods=["GET", "POST"]),
    Mount("/static", StaticFiles(directory=STATIC_PATH), name="static"),
    ]  # Placeholder for the router, replace with actual routes


app = Starlette(
    debug=NETWORK_CONFIG.get('debug'),
    routes=router,
    middleware=[
        Middleware(SessionMiddleware, secret_key="!secret"),
        Middleware(CSRFProtectMiddleware, csrf_secret="!secret"),
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
    ],
    
    )



if __name__ == '__main__':
    import uvicorn
    key_path:Path = None #STATIC_PATH /  "localhost+2-key.pem"
    cert_path:Path = None # STATIC_PATH / "localhost+2.pem"
    try:
        uvicorn.run(app=app, host=NETWORK_CONFIG.get('host'), port=NETWORK_CONFIG.get('port'), ssl_certfile=cert_path, ssl_keyfile=key_path )
    except Exception as e:
        print(str(e))
