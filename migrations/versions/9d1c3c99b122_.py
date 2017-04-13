"""empty message

Revision ID: 9d1c3c99b122
Revises: 7c5e8e9dbab4
Create Date: 2017-02-04 18:09:40.740809

"""

# revision identifiers, used by Alembic.
revision = '9d1c3c99b122'
down_revision = '7c5e8e9dbab4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('address_user_address', sa.Column('contact_no', sa.String(length=13), nullable=True))
    op.add_column('address_user_address', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('address_user_address', sa.Column('first_name', sa.String(length=30), nullable=True))
    op.add_column('address_user_address', sa.Column('is_display', sa.Boolean(), nullable=True))
    op.add_column('address_user_address', sa.Column('is_main', sa.Boolean(), nullable=True))
    op.add_column('address_user_address', sa.Column('is_main_shipping', sa.Boolean(), nullable=True))
    op.add_column('address_user_address', sa.Column('last_name', sa.String(length=30), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('shipping_address_id', sa.Integer(), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('shipping_message', sa.String(length=255), nullable=True))
    op.drop_constraint('wireless_sim_order_ibfk_4', 'wireless_sim_order', type_='foreignkey')
    op.create_foreign_key(None, 'wireless_sim_order', 'address_user_address', ['shipping_address_id'], ['id'])
    op.drop_column('wireless_sim_order', 'last_name')
    op.drop_column('wireless_sim_order', 'shipping_line1')
    op.drop_column('wireless_sim_order', 'shipping_state')
    op.drop_column('wireless_sim_order', 'shipping_city')
    op.drop_column('wireless_sim_order', 'email')
    op.drop_column('wireless_sim_order', 'shipping_iso_3166_country')
    op.drop_column('wireless_sim_order', 'contact_no')
    op.drop_column('wireless_sim_order', 'message')
    op.drop_column('wireless_sim_order', 'first_name')
    op.drop_column('wireless_sim_order', 'shipping_line2')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wireless_sim_order', sa.Column('shipping_line2', mysql.VARCHAR(length=80), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('first_name', mysql.VARCHAR(length=30), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('message', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('contact_no', mysql.VARCHAR(length=13), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('shipping_iso_3166_country', mysql.VARCHAR(length=2), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('email', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('shipping_city', mysql.VARCHAR(length=80), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('shipping_state', mysql.VARCHAR(length=80), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('shipping_line1', mysql.VARCHAR(length=80), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('last_name', mysql.VARCHAR(length=30), nullable=True))
    op.drop_constraint(None, 'wireless_sim_order', type_='foreignkey')
    op.create_foreign_key('wireless_sim_order_ibfk_4', 'wireless_sim_order', 'address_country', ['shipping_iso_3166_country'], ['iso_3166_1_a2'])
    op.drop_column('wireless_sim_order', 'shipping_message')
    op.drop_column('wireless_sim_order', 'shipping_address_id')
    op.drop_column('address_user_address', 'last_name')
    op.drop_column('address_user_address', 'is_main_shipping')
    op.drop_column('address_user_address', 'is_main')
    op.drop_column('address_user_address', 'is_display')
    op.drop_column('address_user_address', 'first_name')
    op.drop_column('address_user_address', 'email')
    op.drop_column('address_user_address', 'contact_no')
    ### end Alembic commands ###