import re

with open("app/api/routes.py", "r") as f:
    content = f.read()

# 1. Update imports
imports_to_add = """from fastapi import Request, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.security import get_current_user, create_access_token, limiter
"""
content = content.replace("from fastapi import APIRouter, Depends, HTTPException, Body", imports_to_add + "from fastapi import APIRouter, Depends, HTTPException, Body")

# 2. Add /token endpoint
token_endpoint = """
@router.post("/token")
@limiter.limit("5/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != settings.admin_username or form_data.password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}
"""
content = content.replace("@router.post(\"/ingest\")", token_endpoint + "\n@router.post(\"/ingest\")\n@limiter.limit(\"5/minute\")")

# 3. Add Request to /ingest and Depends(get_current_user) to all endpoints
# We need to find all `def func_name(...):` that follow a `@router.` decorator.
# For /ingest:
content = content.replace("def ingest_invoices(db: Session = Depends(get_db)):", "def ingest_invoices(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):")

# For other endpoints, we just append `, current_user: str = Depends(get_current_user)` before `):`
endpoints = [
    "def simulate_failure(db: Session = Depends(get_db)):",
    "def list_invoices(status: Optional[str] = None, db: Session = Depends(get_db)):",
    "def get_invoice(invoice_id: int, db: Session = Depends(get_db)):",
    "def get_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):",
    "def review_invoice(invoice_id: int, review: ReviewRequest, db: Session = Depends(get_db)):",
    "def approve_invoice(invoice_id: int, actor: str = Body(default=\"reviewer\", embed=True), db: Session = Depends(get_db)):",
    "def pay_invoice(invoice_id: int, actor: str = Body(default=\"system\", embed=True), db: Session = Depends(get_db)):",
    "def reject_invoice(invoice_id: int, reject_req: RejectRequest, db: Session = Depends(get_db)):",
    "def list_pos(db: Session = Depends(get_db)):",
    "def get_audit_log(invoice_id: int, db: Session = Depends(get_db)):"
]

for ep in endpoints:
    # insert before '):'
    new_ep = ep.replace("):", ", current_user: str = Depends(get_current_user)):")
    content = content.replace(ep, new_ep)

# Also /config and /logs/recent don't have db session
content = content.replace("def get_config():", "def get_config(current_user: str = Depends(get_current_user)):")
content = content.replace("def get_recent_logs(lines: int = 50):", "def get_recent_logs(lines: int = 50, current_user: str = Depends(get_current_user)):")

with open("app/api/routes.py", "w") as f:
    f.write(content)
print("Updated routes.py successfully!")
