# ruff: noqa: ANN401 FBT001 B008
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from typing import Any
from app.entities.coupon import CouponResponse
from app.entities.product import ProductInDB
from sqlalchemy.orm import sessionmaker

from app.infra.database import get_session
from app.entities.report import CommissionInDB, CreateCommissionInDB, InformUserProduct
from app.report import repository
from app.product import repository as product_repository
from app.infra.models import SalesCommissionDB
from faststream.rabbit import RabbitQueue
from app.infra.worker import task_message_bus


async def get_user_sales_comissions(
    user: Any,
    paid: bool,
    released: bool,
    db,
) -> list[CommissionInDB | None]:
    """Get user sales commissions."""
    async with db.begin() as transaction:
        return await repository.get_user_sales_comissions(
            user,
            paid=paid,
            released=released,
            transaction=transaction,
        )


def create_sales_commission( # noqa: PLR0913
    order_id: int,
    user_id: int,
    subtotal: Decimal,
    coupon: CouponResponse,
    payment_id: int,
    db: sessionmaker = get_session(),
) -> SalesCommissionDB:
    """Get sales commit at all."""
    today = datetime.now(tz=UTC)
    release_data = today + timedelta(days=30)
    if not coupon or not coupon.commission_percentage:
        raise ValueError
    commission_value = Decimal(subtotal) * Decimal(coupon.commission_percentage)

    with db.begin() as transaction:
        comission_db = repository.create_sales_commission(
            CreateCommissionInDB(
                order_id=order_id,
                user_id=user_id,
                commission=commission_value,
                date_created=today,
                release_date=release_data,
                payment_id=payment_id,

            ),
            transaction=transaction,
    )
        transaction.commit()
    return comission_db


async def notify_product_to_admin(
    *,
    inform: InformUserProduct,
    db,
    broker: RabbitQueue = task_message_bus,

):
    """Get user, product info and send notification to admin."""
    async with db.begin() as transaction:
        admins = await repository.get_admins(
            transaction=transaction,
        )
        product_db = await product_repository.get_product_by_id(
            inform.product_id,
            transaction=transaction,
        )
        product = ProductInDB.model_validate(product_db)
        inform_db = await repository.save_user_inform(
            inform=inform,
            product=product,
            transaction=transaction,
        )
        transaction.commit()

        await broker.publish(
            {
            'admin_email': admins,
            'product_id': inform_db.product_id,
            'product_name': inform_db.product_name,
            'user_email': inform_db.user_mail,
            'user_phone': inform_db.user_phone,
        },
        queue=RabbitQueue('inform_product_to_admin'),
        )
