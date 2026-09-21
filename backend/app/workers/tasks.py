import logging

import redis
from celery import Celery

from backend.app.core.config import settings
from backend.app.core.contract_status import ContractStatus
from backend.app.core.database import SessionLocal
from backend.app.repositories.contracts import ContractRepository


logger = logging.getLogger(__name__)


celery_app = Celery(
    "contract_manager",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


PROCESSING_LOCK_TTL = 60 * 60


@celery_app.task
def process_contract_task(contract_id: str) -> str:
    lock_key = f"contract-processing:{contract_id}"

    lock = redis_client.lock(
        name=lock_key,
        timeout=PROCESSING_LOCK_TTL,
        blocking=False,
    )

    if not lock.acquire():
        logger.warning(
            "Contract processing already in progress: %s",
            contract_id,
        )
        return contract_id

    db = SessionLocal()

    try:
        repository = ContractRepository(db)

        contract = repository.get_by_contract_id(contract_id)

        if contract is None:
            logger.error(
                "Contract not found for background processing: %s",
                contract_id,
            )
            return contract_id

        if contract.status == ContractStatus.COMPLETED:
            logger.info(
                "Contract already completed. Skipping processing: %s",
                contract_id,
            )
            return contract_id

        logger.info(
            "Background contract processing started: %s",
            contract_id,
        )

        from backend.app.services.documents.contract_processing_service import (
            ContractProcessingService,
        )

        service = ContractProcessingService(db)

        service.extract_contract_text(contract_id)

        logger.info(
            "Background contract processing completed: %s",
            contract_id,
        )

        return contract_id

    except Exception:
        logger.exception(
            "Background contract processing failed: %s",
            contract_id,
        )
        raise

    finally:
        db.close()

        try:
            lock.release()
        except redis.exceptions.LockError:
            logger.warning(
                "Processing lock was already released or expired: %s",
                contract_id,
            )