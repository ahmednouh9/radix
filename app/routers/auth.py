from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.config import settings

router = APIRouter()


class LoginForm(BaseModel):
    pin: str


def is_pin_protected() -> bool:
    return bool(settings.dashboard_pin)


def check_auth(request: Request):
    if not is_pin_protected():
        return True
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=303, detail="Not authenticated")
    return True


@router.get("/login")
async def login_page(request: Request):
    if not is_pin_protected():
        return RedirectResponse(url="/dashboard")
    from app.templates_setup import templates
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
async def login(request: Request, data: LoginForm):
    if not is_pin_protected():
        return RedirectResponse(url="/dashboard", status_code=303)

    if data.pin == settings.dashboard_pin:
        request.session["authenticated"] = True
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        from app.templates_setup import templates
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid PIN"})


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
