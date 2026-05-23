from pathlib import Path

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse

from app.templates_setup import templates
from app.routers.auth import is_pin_protected, check_auth

router = APIRouter()


def get_lang(request: Request) -> str:
    return request.cookies.get("lang", "en")


@router.get("/dashboard")
async def dashboard_page(request: Request):
    if is_pin_protected() and not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "dashboard.html", {"lang": get_lang(request)})


@router.get("/campaigns")
async def campaigns_page(request: Request):
    if is_pin_protected() and not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "campaigns.html", {"lang": get_lang(request)})


@router.get("/settings")
async def settings_page(request: Request):
    if is_pin_protected() and not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "settings.html", {"lang": get_lang(request)})


@router.get("/notifications")
async def notifications_page(request: Request):
    if is_pin_protected() and not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "notifications.html", {"lang": get_lang(request)})


@router.get("/analytics")
async def analytics_page(request: Request):
    if is_pin_protected() and not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "analytics.html", {"lang": get_lang(request)})


@router.get("/privacy")
async def privacy_page(request: Request):
    return templates.TemplateResponse(request, "privacy.html", {"lang": "en"})
