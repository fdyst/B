from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.security import get_db, get_current_user
from models.user_model import User
from models.wallet_model import Wallet
from models.transaction_model import Transaction
from services.wallet_service import transfer_wallet

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/me")
def my_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {
        "balance": wallet.balance
    }


@router.post("/transfer")
def transfer(
    receiver_id: int,
    amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        transfer_wallet(db, current_user.id, receiver_id, amount)
        return {"message": "Transfer successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
def transaction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, le=100),
    offset: int = 0
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return transactions