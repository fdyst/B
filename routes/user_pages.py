from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("user/dashboard.html", {
        "request": request
    })


@router.get("/transfer", response_class=HTMLResponse)
def transfer_page(request: Request):
    return templates.TemplateResponse("user/transfer.html", {
        "request": request
    })


@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse("user/history.html", {
        "request": request
    })


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse("user/profile.html", {
        "request": request
    })
    
@router.get("/topup", response_class=HTMLResponse)
def topup_page(request: Request):
    return templates.TemplateResponse("user/topup.html", {"request": request})