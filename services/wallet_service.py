from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.wallet_model import Wallet
from models.transaction_model import Transaction


def credit_wallet(db: Session, user_id: int, amount: float, description: str):
    if amount <= 0:
        raise Exception("Invalid amount")

    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise Exception("Wallet not found")

    wallet.balance += amount

    db.add(Transaction(
        user_id=user_id,
        amount=amount,
        type="credit",
        description=description
    ))

    db.commit()


def debit_wallet(db: Session, user_id: int, amount: float, description: str):
    if amount <= 0:
        raise Exception("Invalid amount")

    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise Exception("Wallet not found")

    if wallet.balance < amount:
        raise Exception("Insufficient balance")

    wallet.balance -= amount

    db.add(Transaction(
        user_id=user_id,
        amount=amount,
        type="debit",
        description=description
    ))

    db.commit()


def transfer_wallet(db: Session, sender_id: int, receiver_id: int, amount: float):
    if amount <= 0:
        raise Exception("Invalid amount")

    if sender_id == receiver_id:
        raise Exception("Cannot transfer to yourself")

    sender_wallet = db.query(Wallet).filter(Wallet.user_id == sender_id).first()
    receiver_wallet = db.query(Wallet).filter(Wallet.user_id == receiver_id).first()

    if not sender_wallet or not receiver_wallet:
        raise Exception("Wallet not found")

    if sender_wallet.balance < amount:
        raise Exception("Insufficient balance")

    try:
        # Kurangi sender
        sender_wallet.balance -= amount

        # Tambah receiver
        receiver_wallet.balance += amount

        # Catat transaksi sender
        db.add(Transaction(
            user_id=sender_id,
            amount=amount,
            type="debit",
            description=f"Transfer to user {receiver_id}"
        ))

        # Catat transaksi receiver
        db.add(Transaction(
            user_id=receiver_id,
            amount=amount,
            type="credit",
            description=f"Transfer from user {sender_id}"
        ))

        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise Exception("Transfer failed")