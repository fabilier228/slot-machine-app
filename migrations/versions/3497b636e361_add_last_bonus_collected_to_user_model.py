"""Add last_bonus_collected to User model

Revision ID: 3497b636e361
Revises:
Create Date: 2025-01-12 18:54:58.771812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3497b636e361'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_bonus_collected', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint('uq_user_email', ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_email', type_='unique')
        batch_op.drop_column('last_bonus_collected')

    # ### end Alembic commands ###
