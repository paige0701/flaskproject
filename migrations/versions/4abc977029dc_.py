"""empty message

Revision ID: 4abc977029dc
Revises: 198b53f07174
Create Date: 2017-02-06 16:21:16.486977

"""

# revision identifiers, used by Alembic.
revision = '4abc977029dc'
down_revision = '198b53f07174'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wireless_recharge', sa.Column('quantity', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('wireless_recharge', 'quantity')
    ### end Alembic commands ###
