"""empty message

Revision ID: da5963e0304d
Revises: c7497fa98f88
Create Date: 2017-01-11 13:12:48.104390

"""

# revision identifiers, used by Alembic.
revision = 'da5963e0304d'
down_revision = 'c7497fa98f88'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('recipient_name', sa.String(length=65), nullable=True))
    op.drop_column('order', 'name')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('name', mysql.VARCHAR(length=65), nullable=True))
    op.drop_column('order', 'recipient_name')
    ### end Alembic commands ###
