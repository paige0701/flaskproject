"""empty message

Revision ID: 691f5d32f572
Revises: 93b54650e9f7
Create Date: 2016-11-20 17:03:41.561439

"""

# revision identifiers, used by Alembic.
revision = '691f5d32f572'
down_revision = '93b54650e9f7'

from alembic import op
import sqlalchemy as sa



def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('catalogue_product_image_ibfk_1', 'catalogue_product_image', type_='foreignkey')
    op.create_foreign_key(None, 'catalogue_product_image', 'catalogue_product', ['product_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'catalogue_product_image', type_='foreignkey')
    op.create_foreign_key('catalogue_product_image_ibfk_1', 'catalogue_product_image', 'catalogue_product_detail', ['product_id'], ['id'])
    ### end Alembic commands ###
