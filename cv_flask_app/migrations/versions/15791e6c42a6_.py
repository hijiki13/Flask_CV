"""empty message

Revision ID: 15791e6c42a6
Revises: 
Create Date: 2023-02-16 01:25:33.798432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15791e6c42a6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('registeredUsers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mail', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('fathers_name', sa.String(), nullable=True),
    sa.Column('birthdate', sa.String(), nullable=True),
    sa.Column('LinkedIn', sa.String(), nullable=True),
    sa.Column('tel', sa.String(), nullable=True),
    sa.Column('education', sa.String(), nullable=True),
    sa.Column('skills', sa.String(), nullable=True),
    sa.Column('experience', sa.String(), nullable=True),
    sa.Column('u_img', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('registeredUsers')
    # ### end Alembic commands ###