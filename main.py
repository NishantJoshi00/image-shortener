from fastapi import FastAPI, Response, Request, Form


from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
import requests
from database import db

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def authenticate_url(url):
    # Check if the url is valid and of type image
    if not url.startswith("https"):
        return False
    value = requests.get(url).headers.get("content-type")
    if value is None:
        return False
    if not value.startswith("image"):
        return False
    return True




# routes
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})

@app.post("/generate")
async def generate(request: Request, url: str = Form(...)):
    if not authenticate_url(url):
        return templates.TemplateResponse("error.html", {'request': request, 'error': "Invalid URL"})
    else:
        new_url, token = db.add_url(url)
        print(request.base_url)
        return templates.TemplateResponse("generated.html", {'request': request, 'new_url': new_url, 'token': token, 'url': url})

@app.get("/view/{idx}")
async def view(request: Request, idx: str):
    url, token = db.get_url(idx)
    if url is None:
        return Response(status_code=404, content="URL not found")
    else:
        response = requests.get(url)
        keys = (k for k in request.headers if k.startswith('sec-ch'))
        data = (': '.join((k, request.headers[k])) for k in keys)
        data = '; '.join(data)
        if data == '':
            data = request.headers.get('User-Agent')
        db.add_entry(token, data, request.client.host)
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type"),
        )


@app.get("/stats/{token}")
async def stats(request: Request, token: str):

    entries = db.get_entries(token)
    url = db.url_from_token(token)
    if entries == None:
        return templates.TemplateResponse("error.html", {'request': request, 'error': "Invalid Token"})
    else:
        return templates.TemplateResponse("stats.html", {'request': request, 'entries': entries, 'token': token, 'url': url})



# @app.get("/stats/{view_url}")
# async def stats(view_url: str):
#     token = db.get_token(view_url)
#     if token is None:
#         return Response(status_code=404, content="URL not found")
#     else:
#         return {
#             'views': db.get_views(token),
#         }

