"""empty message

Revision ID: c55d80b6b635
Revises: b72f03296cc5
Create Date: 2016-11-01 17:57:50.055269

"""

# revision identifiers, used by Alembic.
revision = 'c55d80b6b635'
down_revision = 'b72f03296cc5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catalogue_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('image', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('catalogue_product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('upc', sa.String(length=64), nullable=True),
    sa.Column('price', sa.DECIMAL(), nullable=True),
    sa.Column('currency', sa.CHAR(length=3), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['catalogue_category.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('upc')
    )
    op.create_index(op.f('ix_catalogue_product_name'), 'catalogue_product', ['name'], unique=False)
    op.create_table('catalogue_product_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('is_thumbnail', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['catalogue_product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('catalogue_product_image')
    op.drop_index(op.f('ix_catalogue_product_name'), table_name='catalogue_product')
    op.drop_table('catalogue_product')
    op.drop_table('catalogue_category')
    ### end Alembic commands ###
