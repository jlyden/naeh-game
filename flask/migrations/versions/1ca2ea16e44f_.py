"""empty message

Revision ID: 1ca2ea16e44f
Revises: 1e2038c00103
Create Date: 2017-03-15 21:06:20.938122

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ca2ea16e44f'
down_revision = '1e2038c00103'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('round_count', sa.Integer(), nullable=True),
    sa.Column('bead_count', sa.Integer(), nullable=True),
    sa.Column('from_board', sa.String(), nullable=True),
    sa.Column('to_board', sa.String(), nullable=True),
    sa.Column('diversion', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_index('ix_game_team_name', table_name='game')
    op.drop_column('game', 'team_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game', sa.Column('team_name', sa.VARCHAR(length=40), autoincrement=False, nullable=True))
    op.create_index('ix_game_team_name', 'game', ['team_name'], unique=False)
    op.drop_table('rules')
    # ### end Alembic commands ###
