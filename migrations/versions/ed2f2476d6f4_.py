"""empty message

Revision ID: ed2f2476d6f4
Revises: edc699045fb2
Create Date: 2016-11-14 02:35:19.007773

"""

# revision identifiers, used by Alembic.
revision = 'ed2f2476d6f4'
down_revision = 'edc699045fb2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wireless_sim_activate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('phone_number', sa.String(length=12), nullable=True),
    sa.Column('sim_number', sa.String(length=16), nullable=True),
    sa.Column('sim_type', sa.CHAR(length=2), nullable=True),
    sa.Column('phone_type', sa.String(length=40), nullable=True),
    sa.Column('passport_img', sa.String(length=255), nullable=True),
    sa.Column('active_date', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('deactivate_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wireless_sim_activate_phone_number'), 'wireless_sim_activate', ['phone_number'], unique=False)
    op.create_table('wireless_sim_product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('sim_number', sa.String(length=16), nullable=True),
    sa.Column('sim_type', sa.CHAR(length=2), nullable=True),
    sa.Column('is_sold', sa.Boolean(), nullable=True),
    sa.Column('is_activated', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wireless_sim_product_sim_number'), 'wireless_sim_product', ['sim_number'], unique=True)
    op.create_table('wireless_sim_order_product',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['wireless_sim_order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['wireless_sim_product.id'], ),
    sa.PrimaryKeyConstraint('product_id', 'order_id')
    )
    op.add_column('wireless_sim_order', sa.Column('rcv_extra_address', sa.String(length=255), nullable=True))
    op.drop_constraint('wireless_sim_order_ibfk_4', 'wireless_sim_order', type_='foreignkey')
    op.drop_column('wireless_sim_order', 'user_country')
    op.drop_column('wireless_sim_order', 'rcv_extran_address')
    op.add_column('wireless_sim_topup', sa.Column('activate_sim', sa.Integer(), nullable=True))
    op.add_column('wireless_sim_topup', sa.Column('is_initial', sa.String(length=12), nullable=True))
    op.create_foreign_key(None, 'wireless_sim_topup', 'wireless_sim_activate', ['activate_sim'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wireless_sim_topup', type_='foreignkey')
    op.drop_column('wireless_sim_topup', 'is_initial')
    op.drop_column('wireless_sim_topup', 'activate_sim')
    op.add_column('wireless_sim_order', sa.Column('rcv_extran_address', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('wireless_sim_order', sa.Column('user_country', mysql.CHAR(length=2), nullable=True))
    op.create_foreign_key('wireless_sim_order_ibfk_4', 'wireless_sim_order', 'address_country', ['user_country'], ['iso_3166_1_a2'])
    op.drop_column('wireless_sim_order', 'rcv_extra_address')
    op.drop_table('wireless_sim_order_product')
    op.drop_index(op.f('ix_wireless_sim_product_sim_number'), table_name='wireless_sim_product')
    op.drop_table('wireless_sim_product')
    op.drop_index(op.f('ix_wireless_sim_activate_phone_number'), table_name='wireless_sim_activate')
    op.drop_table('wireless_sim_activate')
    ### end Alembic commands ###
