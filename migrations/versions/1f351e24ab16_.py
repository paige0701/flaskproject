"""empty message

Revision ID: 1f351e24ab16
Revises: 66c74195c217
Create Date: 2016-11-02 17:26:55.108582

"""

# revision identifiers, used by Alembic.
revision = '1f351e24ab16'
down_revision = '66c74195c217'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('catalogue_product_image', sa.Column('is_thumbnail', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('catalogue_product_image', 'is_thumbnail')
    ### end Alembic commands ###
