from fastapi import status
from app.infra.database import get_async_session
from main import app
from httpx import AsyncClient
import pytest

from tests.factories_db import CategoryFactory, CreditCardFeeConfigFactory, InventoryDBFactory, ProductDBFactory


URL = '/catalog/category/products'


@pytest.mark.asyncio
async def test_with_product_list_only_category_path(asyncdb):
    """Must return with category path ok."""
    # Arrange
    async with asyncdb().begin() as transaction:
        category = CategoryFactory(path='test')
        config_fee = CreditCardFeeConfigFactory()
        transaction.session.add_all([category, config_fee])
        await transaction.session.flush()
        product_db_1 = ProductDBFactory(
            category=category,
            installment_config=config_fee,
            price=100,
            active=True,
        )
        product_db_2 = ProductDBFactory(
            category=category,
            installment_config=config_fee,
            price=200,
            active=False,
        )

        inventory_db_1 = InventoryDBFactory(
            product=product_db_1,
            product_id=1,
            inventory_id=1,
        )
        inventory_db_2 = InventoryDBFactory(
            product=product_db_2,
            product_id=2,
            inventory_id=2,
        )
        transaction.session.add_all([product_db_1, product_db_2])
        await transaction.session.flush()
        transaction.session.add_all([inventory_db_1, inventory_db_2])
        await transaction.session.commit()

    # Act
    async with AsyncClient(app=app, base_url='http://test') as client:
        app.dependency_overrides[get_async_session] = lambda: asyncdb
        response = await client.get(
            f"{URL}/{category.path}",
            params={"offset": 1, "page": 1 },
        )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get('products')[0].get('product_id') == product_db_1.product_id


