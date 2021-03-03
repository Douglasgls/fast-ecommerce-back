from fastapi import Header, APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.payment_schema import (
    CreditCardPayment,
    SlipPayment,
    ConfigCreditCard,
    ConfigCreditCardResponse,
)
from schemas.order_schema import (
    ProductSchema,
    CheckoutSchema,
    ProductResponseSchema,
)
from domains import domain_payment
from endpoints import deps

from loguru import logger

payment = APIRouter()


@payment.post("/gateway-payment-credit-card", status_code=201)
async def payment_credit_card(
    *, db: Session = Depends(deps.get_db), payment_data: CreditCardPayment
):
    payment = domain_payment.credit_card_payment(db, payment=payment_data)
    return payment


@payment.post("/gateway-payment-bank-slip", status_code=201)
def payment_bank_slip(*, db: Session = Depends(deps.get_db), payment_data: SlipPayment):
    payment = domain_payment.slip_payment(db, payment=payment_data)
    return payment


@payment.post("/create-product", status_code=201)
def create_product(*, db: Session = Depends(deps.get_db), product: ProductSchema):
    product = domain_payment.create_product(db, product=product)
    return ProductSchema.from_orm(product)


@payment.post("/create-config", status_code=201)
def create_config(*, db: Session = Depends(deps.get_db), config_data: ConfigCreditCard):
    _config = domain_payment.create_installment_config(db, config_data=config_data)
    return ConfigCreditCardResponse.from_orm(_config)


@payment.post("/checkout", status_code=201)
def checkout(*, db: Session = Depends(deps.get_db), checkout_data: CheckoutSchema):
    """
    Receber todos os dados -> user_id + list of products_ids
    buscar ou gerar customer
    buscar ou gerar credit card
    gerar um invoice -> user + product + payment
    gerar um postback -> capturar status posteriores
    mandar e-mail
    """
    logger.debug(f"CAPTURAR - {checkout_data}")
    checkout = domain_payment.process_checkout(db=db, checkout_data=checkout_data)
    return checkout
