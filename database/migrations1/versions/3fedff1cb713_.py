"""empty message

Revision ID: 3fedff1cb713
Revises: 
Create Date: 2021-01-24 08:15:19.144148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fedff1cb713'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
    sa.Column('cid', sa.Integer(), nullable=False),
    sa.Column('cname', sa.String(), nullable=False),
    sa.Column('clocation', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('cid'),
    sa.UniqueConstraint('cname')
    )
    op.create_table('employee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('employee')
    op.drop_table('company')
    # ### end Alembic commands ###