"""empty message

Revision ID: 0cd96e32f88d
Revises: 6d46168bee43
Create Date: 2017-01-24 13:00:06.719988

"""

# revision identifiers, used by Alembic.
revision = '0cd96e32f88d'
down_revision = '6d46168bee43'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_association', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order_association', 'auth_users', ['user_id'], ['id'])
    op.alter_column('product_return', 'order_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True,
               existing_server_default=sa.text("'0'"))
    op.alter_column('product_return', 'product_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True,
               existing_server_default=sa.text("'0'"))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product_return', 'product_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.alter_column('product_return', 'order_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.drop_constraint(None, 'order_association', type_='foreignkey')
    op.drop_column('order_association', 'user_id')
    ### end Alembic commands ###
