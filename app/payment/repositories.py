from fastapi import Depends
from decimal import Decimal
from sqlalchemy.orm import Session
from models.order import Product, Order, OrderItems
from models.transaction import Transaction, Payment, CreditCardFeeConfig
from payment.schema import ConfigCreditCardInDB, ConfigCreditCardResponse\
    , OrderFullResponse, ProductInDB
from payment.adapter import Database
from datetime import datetime
from loguru import logger


class ProductDB:
    def __init__(self,item):
        self.db = Database.get_db()
        self.item = item


    def decrease_product(self):
        _product_decrease = self.db.query(Product).filter_by(id=self.item.get("id")).first()
        return _product_decrease
    

    def add_product(self, _product_decrease):
        self.db.add(_product_decrease)
        self.db.commit()


class OrderDB:
    def __init__(self, user_id):
        self.user_id = user_id

    def create_order(self):
        db = Database.get_db()
        db_order = Order(
            customer_id= self.user_id,
            order_date= datetime.now(),
            order_status= 'pending')
        db.add(db_order)
        db.commit()
        return OrderFullResponse.from_orm(db_order)
      
    
    def create_order_items(self, db_order, cart):
        db = Database.get_db()
        db_item = OrderItems(
                order_id = db_order,
                product_id = cart.get("product_id"),
                quantity = cart.get("qty")
                )
        db.add(db_item)
        db.commit()
    

class CreatePayment:
    def __init__(self, user_id, _payment_method, _installments):
        self.user_id = user_id
        self._payment_method = _payment_method
        self._installments = _installments
        self.db = Database.get_db()


    def create_payment(self):
        db_payment = Payment(
                user_id=self.user_id,
                amount=100,
                status="pending",
                payment_method=self._payment_method,
                payment_gateway="PagarMe",
                installments=self._installments if self._installments else 1
                )
        self.db.add(db_payment)
        self.db.commit()
        return db_payment


class QueryPayment:
    def __init__(self, db):
        self.db = db 

    def query(self):
        db_payment = self.db.query(Payment).first()
        return db_payment


class CreateTransaction:
    def __init__(self,user_id, cart, order, affiliate, payment_id):
        self.db = Database.get_db()
        self.user_id = user_id
        self.cart = cart 
        self.order = order 
        self.affiliate = affiliate
        self.payment_id = payment_id


    def create_transaction(self):
        db_transaction = Transaction(
            user_id = self.user_id,
            amount= self.cart.get("amount"),
            order_id=self.order.id,
            qty= self.cart.get("qty"),
            payment_id=self.payment_id,
            status= "pending",
            product_id=self.cart.get("product_id"),
            affiliate= self.affiliate,
        )
        self.db.add(db_transaction)
        self.db.commit()


class GetCreditCardConfig:
    def __init__(self, _product_id):
        self.db = Database.get_db()
        self._product_id = _product_id


    def get_config(self):
        _product_config = self.db.query(Product).filter_by(id=int(self._product_id)).first()

        _config_installments = self.db.query(CreditCardFeeConfig)\
            .filter_by(id=_product_config.installments_config)\
            .first()
        logger.debug(ConfigCreditCardResponse.from_orm(_config_installments))
        return ConfigCreditCardResponse.from_orm(_config_installments)


class CreditCardConfig:
    def __init__(self, config_data):
        self.config_data = config_data


    def create_installment_config(self):
        db_config = CreateCreditConfig(config_data=self.config_data).create_credit()
        return db_config


class CreateCreditConfig:
    def __init__(self,config_data):
        self.config_data = config_data


    def create_credit(self):
        db = Database.get_db()
        db_config = CreditCardFeeConfig(
            active_date = datetime.now(),
            fee=Decimal(self.config_data.fee),
            min_installment_with_fee=self.config_data.min_installment,
            mx_installments=self.config_data.max_installment
            )
        db.add(db_config)
        db.commit()
        return db_config


class UpdateStatus:
    def update_payment_status(db:Session, payment_data, order):
        db_transactions = db.query(Transaction).filter_by(order_id=order.id).all()
        for db_transaction in db_transactions:
            db_transaction.status = payment_data.get("status")

            db_payment = db.query(Payment).filter_by(id=db_transaction.payment_id).first()
            db_payment.processed=True
            db_payment.processed_at=datetime.now()
            db_payment.gateway_id = payment_data.get("gateway_id")
            db_payment.token=payment_data.get("token")
            db_payment.authorization=payment_data.get("authorization_code")
            db_payment.status=payment_data.get("status")
            db.add(db_transaction)
            db.add(db_payment)
            db.commit()
            db.refresh(db_transaction)
            db.refresh(db_payment)