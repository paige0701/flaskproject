"""empty message

Revision ID: a6bb7abb1d4d
Revises: 5acd337a4e42
Create Date: 2016-11-11 14:32:17.066051

"""

# revision identifiers, used by Alembic.
revision = 'a6bb7abb1d4d'
down_revision = '5acd337a4e42'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catalogue_product_cart',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('upc', sa.String(length=64), nullable=True),
    sa.Column('price', sa.DECIMAL(), nullable=True),
    sa.Column('currency', sa.CHAR(length=3), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('upc')
    )
    op.create_index(op.f('ix_catalogue_product_cart_name'), 'catalogue_product_cart', ['name'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_catalogue_product_cart_name'), table_name='catalogue_product_cart')
    op.drop_table('catalogue_product_cart')
    ### end Alembic commands ###