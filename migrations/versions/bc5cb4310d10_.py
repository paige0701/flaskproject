"""empty message

Revision ID: bc5cb4310d10
Revises: 940a0c14c357
Create Date: 2017-01-24 17:20:26.994781

"""

# revision identifiers, used by Alembic.
revision = 'bc5cb4310d10'
down_revision = '940a0c14c357'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product_return', 'test')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product_return', sa.Column('test', mysql.VARCHAR(length=255), nullable=True))
    ### end Alembic commands ###