"""empty message

Revision ID: 94b030b84490
Revises: 827e10a6f1c9
Create Date: 2017-01-31 17:40:57.267683

"""

# revision identifiers, used by Alembic.
revision = '94b030b84490'
down_revision = '827e10a6f1c9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wireless_sim_activate', sa.Column('nationality_iso_3166_country', sa.CHAR(length=2), nullable=True))
    op.create_foreign_key(None, 'wireless_sim_activate', 'address_country', ['nationality_iso_3166_country'], ['iso_3166_1_a2'])
    op.drop_column('wireless_sim_activate', 'nationality')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wireless_sim_activate', sa.Column('nationality', mysql.CHAR(length=2), nullable=True))
    op.drop_constraint(None, 'wireless_sim_activate', type_='foreignkey')
    op.drop_column('wireless_sim_activate', 'nationality_iso_3166_country')
    ### end Alembic commands ###