"""Persist analysis results and usage logs to the database."""

from __future__ import annotations

import uuid

from sqlmodel import Session, select

from utility.database.model import TextAnalysisRequest, UsageLog, User


def record_analysis(
    db: Session,
    *,
    user_id: uuid.UUID,
    input_text: str,
    is_profane: bool,
    toxicity_score: float,
    endpoint: str,
    ip_address: str,
    status_code: int,
    deduct_credit: bool = True,
) -> TextAnalysisRequest:
    request_row = TextAnalysisRequest(
        userid=user_id,
        inputtext=input_text,
        isprofane=is_profane,
        toxicityscore=toxicity_score,
    )
    db.add(request_row)
    db.flush()

    log = UsageLog(
        userid=user_id,
        requestid=request_row.id,
        endpointurl=endpoint,
        ipaddress=ip_address,
        statuscode=status_code,
        issuccessful=200 <= status_code < 300,
    )
    db.add(log)

    if deduct_credit:
        user = db.exec(select(User).where(User.id == user_id)).first()
        if user and user.credits > 0:
            user.credits -= 1
            db.add(user)

    db.commit()
    db.refresh(request_row)
    return request_row

