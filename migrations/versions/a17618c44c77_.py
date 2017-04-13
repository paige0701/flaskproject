"""empty message

Revision ID: a17618c44c77
Revises: 3e99f83094d6
Create Date: 2016-11-15 16:04:32.129600

"""

# revision identifiers, used by Alembic.
revision = 'a17618c44c77'
down_revision = '3e99f83094d6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('catalogue_product', sa.Column('structure', sa.Enum('Standalone', 'Parent', 'Child', name='structure_choices'), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('catalogue_product', 'structure')
    ### end Alembic commands ###
