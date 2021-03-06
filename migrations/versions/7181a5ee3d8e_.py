"""empty message

Revision ID: 7181a5ee3d8e
Revises: a48e477afe75
Create Date: 2017-01-23 14:33:53.700882

"""

# revision identifiers, used by Alembic.
revision = '7181a5ee3d8e'
down_revision = 'a48e477afe75'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product_return', 'exchange_refund',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('product_return', 'order_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('product_return', 'product_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product_return', 'product_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('product_return', 'order_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('product_return', 'exchange_refund',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    ### end Alembic commands ###
