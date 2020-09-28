"""Add installments config in product

Revision ID: e3c7efafba59
Revises: b655f3d7af00
Create Date: 2020-09-01 08:56:14.058304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3c7efafba59'
down_revision = 'b655f3d7af00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('creditcardfeeconfig',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('min_installment_with_fee', sa.Integer(), nullable=True),
    sa.Column('mx_installments', sa.Integer(), nullable=True),
    sa.Column('fee', sa.Numeric(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('product', sa.Column('installments_config', sa.Integer(), nullable=True))
    op.add_column('product', sa.Column('installments_json', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'installments_json')
    op.drop_column('product', 'installments_config')
    op.drop_table('creditcardfeeconfig')
    # ### end Alembic commands ###
