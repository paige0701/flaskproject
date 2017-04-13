"""empty message

Revision ID: 4cba2931621e
Revises: 36739f9d8074
Create Date: 2016-11-09 11:03:20.298638

"""

# revision identifiers, used by Alembic.
revision = '4cba2931621e'
down_revision = '36739f9d8074'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('housing_reservation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('user_name', sa.String(length=55), nullable=True),
    sa.Column('email', sa.String(length=55), nullable=True),
    sa.Column('kakao_id', sa.String(length=55), nullable=True),
    sa.Column('mobile_no', sa.String(length=55), nullable=True),
    sa.Column('checkin_date', sa.DateTime(), nullable=True),
    sa.Column('chekout_date', sa.DateTime(), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('reservation_status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['auth_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_housing_reservation_user_id'), 'housing_reservation', ['user_id'], unique=False)
    op.add_column('wireless_sim_order', sa.Column('user_name', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_wireless_sim_order_sim_number'), 'wireless_sim_order', ['sim_number'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_wireless_sim_order_sim_number'), table_name='wireless_sim_order')
    op.drop_column('wireless_sim_order', 'user_name')
    op.drop_index(op.f('ix_housing_reservation_user_id'), table_name='housing_reservation')
    op.drop_table('housing_reservation')
    ### end Alembic commands ###
