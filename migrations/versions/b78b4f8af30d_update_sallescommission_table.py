"""Update sallescommission table

Revision ID: b78b4f8af30d
Revises: 0b293b9fe558
Create Date: 2024-10-04 18:54:41.156436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b78b4f8af30d'
down_revision: Union[str, None] = '0b293b9fe558'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coupons', sa.Column('discount_price', sa.Numeric(), nullable=True))
    op.add_column('coupons', sa.Column('limit_price', sa.Numeric(), nullable=True))
    op.add_column('sales_commission', sa.Column('payment_id', sa.Integer(), nullable=False))
    op.add_column('sales_commission', sa.Column('active', sa.Boolean(), nullable=False))
    op.create_foreign_key(None, 'sales_commission', 'payment', ['payment_id'], ['payment_id'])
    op.drop_column('user', 'franchise_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('franchise_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'sales_commission', type_='foreignkey')
    op.drop_column('sales_commission', 'active')
    op.drop_column('sales_commission', 'payment_id')
    op.drop_column('coupons', 'limit_price')
    op.drop_column('coupons', 'discount_price')
    # ### end Alembic commands ###
