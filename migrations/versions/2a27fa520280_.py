"""empty message

Revision ID: 2a27fa520280
Revises: 8a4d345fc213
Create Date: 2016-11-14 23:25:49.856189

"""

# revision identifiers, used by Alembic.
revision = '2a27fa520280'
down_revision = '8a4d345fc213'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catalogue_association',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('cart_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('is_ordered', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['cart_id'], ['catalogue_product_cart.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['catalogue_product.id'], ),
    sa.PrimaryKeyConstraint('id', 'product_id', 'cart_id')
    )
    op.drop_index('upc', table_name='catalogue_product_cart')
    op.drop_constraint('catalogue_product_cart_ibfk_2', 'catalogue_product_cart', type_='foreignkey')
    op.drop_column('catalogue_product_cart', 'product_id')
    op.drop_column('catalogue_product_cart', 'upc')
    op.drop_column('catalogue_product_cart', 'quantity')
    op.add_column('wireless_sim_activate', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_wireless_sim_activate_user_id'), 'wireless_sim_activate', ['user_id'], unique=False)
    op.create_foreign_key(None, 'wireless_sim_activate', 'auth_users', ['user_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wireless_sim_activate', type_='foreignkey')
    op.drop_index(op.f('ix_wireless_sim_activate_user_id'), table_name='wireless_sim_activate')
    op.drop_column('wireless_sim_activate', 'user_id')
    op.add_column('catalogue_product_cart', sa.Column('quantity', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('catalogue_product_cart', sa.Column('upc', mysql.VARCHAR(length=64), nullable=True))
    op.add_column('catalogue_product_cart', sa.Column('product_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('catalogue_product_cart_ibfk_2', 'catalogue_product_cart', 'catalogue_product', ['product_id'], ['id'])
    op.create_index('upc', 'catalogue_product_cart', ['upc'], unique=True)
    op.drop_table('catalogue_association')
    ### end Alembic commands ###