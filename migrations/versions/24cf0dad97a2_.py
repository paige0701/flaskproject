"""empty message

Revision ID: 24cf0dad97a2
Revises: 2a27fa520280
Create Date: 2016-11-15 12:14:53.968520

"""

# revision identifiers, used by Alembic.
revision = '24cf0dad97a2'
down_revision = '2a27fa520280'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('housing_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('is_thumbnail', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['housing_services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('room_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('is_thumbnail', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['housing_rooms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('housing_services', 'thumbnail_image')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('housing_services', sa.Column('thumbnail_image', mysql.VARCHAR(length=200), nullable=True))
    op.drop_table('room_image')
    op.drop_table('housing_image')
    ### end Alembic commands ###
