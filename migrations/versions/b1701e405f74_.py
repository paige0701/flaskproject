"""empty message

Revision ID: b1701e405f74
Revises: e09f73da81e3
Create Date: 2016-11-09 15:49:37.333677

"""

# revision identifiers, used by Alembic.
revision = 'b1701e405f74'
down_revision = 'e09f73da81e3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('housing_reservation', sa.Column('checkout_date', sa.DateTime(), nullable=True))
    op.drop_column('housing_reservation', 'chekout_date')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('housing_reservation', sa.Column('chekout_date', mysql.DATETIME(), nullable=True))
    op.drop_column('housing_reservation', 'checkout_date')
    ### end Alembic commands ###