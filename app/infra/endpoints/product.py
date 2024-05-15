# ruff: noqa: ANN401 TRY301 TRY300
from types import ModuleType
from typing import Any, Callable
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from redis.commands.core import AsyncHyperlogCommands
from sqlalchemy.orm import Session
from app.entities.product import (
    InventoryTransaction,
    ProductCreate,
    ProductCreateResponse,
    ProductInDB,
    ProductInDBResponse,
)
from app.infra.database import get_async_session
from app.infra.models import ProductDB

from app.order import services
from app.product import services as product_services
from app.infra import deps
from app.infra.deps import get_db
from schemas.order_schema import (
    ProductFullResponse,
    ProductPatchRequest,
)

product = APIRouter(
    prefix='/product',
    tags=['product'],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@product.get(
    '/inventory',
    status_code=status.HTTP_200_OK,
    tags=['admin'],
)
async def product_inventory(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_async_session),
):
    """Get products inventory."""
    return await product_services.get_inventory(token=token, db=db)

@product.post(
    '/inventory/{product_id}/transaction',
    status_code=status.HTTP_201_CREATED,
    tags=['admin'],
)
async def product_inventory(
    product_id: int,
    inventory: InventoryTransaction,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_async_session),
):
    """Get products inventory."""
    return await product_services.inventory_transaction(product_id, inventory=inventory, token=token, db=db)

@product.post(
    '/create-product',
    summary='[Admin] Create new product',
    status_code=status.HTTP_201_CREATED,
    response_model=ProductInDBResponse,
    tags=['admin'],
)
def create_product(
    *,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(deps.get_db),
    product_data: ProductCreate,
) -> ProductInDBResponse:
    """Create product."""
    product = services.create_product(product_data, token=token, db=db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error in create product',
        )
    return product


@product.post(
    '/upload-image/{product_id}',
    summary='Put image in product.',
    description='Get product_id and image file and update to image client.',
    status_code=status.HTTP_200_OK,
    tags=['admin'],
)
def upload_image(
    product_id: int,
    *,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    image: UploadFile = File(...),
) -> None:
    """Upload image."""
    try:
        _ = token
        return product_services.upload_image(product_id, db=db, image=image)
    except Exception:
        raise


@product.post('/upload-image-gallery/', status_code=200)
def upload_image_gallery(
    product_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    imagegallery: UploadFile = File(...),
) -> None:
    """Upload image gallery."""
    try:
        _ = token
        return services.upload_image_gallery(product_id, db, imagegallery)
    except Exception:
        raise


@product.get(
    '/images/gallery/{uri}',
    status_code=status.HTTP_200_OK,
    tags=['admin'],
 )
def get_images_gallery(uri: str, db: Session = Depends(get_db)) -> None:
    """Get images gallery."""
    try:
        return services.get_images_gallery(db, uri)
    except Exception:
        raise


@product.delete(
    '/delete/image-gallery/{id}',
     status_code=status.HTTP_200_OK,
     tags=['admin'],
 )
def delete_image(id: int, db: Session = Depends(get_db)) -> None:
    """Delete image."""
    try:
        return services.delete_image_gallery(id, db)
    except Exception:
        raise


@product.get('/{uri:path}', status_code=200, response_model=ProductInDB)
def get_product_uri(uri: str, db: Session = Depends(get_db)) -> ProductInDB:
    """GET product uri."""
    try:
        product = services.get_product(db, uri)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found',
            )

        return product
    except Exception as e: # noqa: BLE001
        logger.error(f'Erro em obter os produto - { e }')
        raise e from Exception


@product.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=ProductFullResponse,
    tags=['admin'],
)
def patch_product(
    id: int,
    value: ProductPatchRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> ProductFullResponse:
    """Put product."""
    try:
        _ = token
        return services.patch_product(db, id, value)
    except Exception as e:
        logger.error(f'Erro em atualizar o produto - { e }')
        raise


@product.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    tags=['admin'],
)
def delete_product(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
 ) -> None:
    """Delete product."""
    try:
        _ = token
        return services.delete_product(db, id)
    except Exception:
        raise


@product.get('/cart/installments', status_code=200)
def get_installments(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """Get installments."""
    try:
        return services.get_installments(product_id, db=db)
    except Exception as e:
        logger.error(f'Erro ao coletar o parcelamento - {e}')
        raise
