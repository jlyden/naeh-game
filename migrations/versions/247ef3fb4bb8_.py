"""empty message

Revision ID: 247ef3fb4bb8
Revises: 
Create Date: 2017-06-16 06:56:00.551877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '247ef3fb4bb8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_datetime', sa.DateTime(), nullable=True),
    sa.Column('round_count', sa.Integer(), nullable=True),
    sa.Column('board_to_play', sa.Integer(), nullable=True),
    sa.Column('intake_cols', sa.Integer(), nullable=True),
    sa.Column('outreach_max', sa.Integer(), nullable=True),
    sa.Column('available', sa.PickleType(), nullable=True),
    sa.Column('intake', sa.PickleType(), nullable=True),
    sa.Column('unsheltered', sa.PickleType(), nullable=True),
    sa.Column('outreach', sa.PickleType(), nullable=True),
    sa.Column('market', sa.PickleType(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('emergency',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('board', sa.PickleType(), nullable=True),
    sa.Column('maximum', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('round_count', sa.Integer(), nullable=True),
    sa.Column('board_played', sa.Integer(), nullable=True),
    sa.Column('moves', sa.PickleType(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('permanent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('board', sa.PickleType(), nullable=True),
    sa.Column('maximum', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rapid',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('board', sa.PickleType(), nullable=True),
    sa.Column('maximum', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('score',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('emergency_count', sa.PickleType(), nullable=True),
    sa.Column('transitional_count', sa.PickleType(), nullable=True),
    sa.Column('unsheltered', sa.Integer(), nullable=True),
    sa.Column('market', sa.Integer(), nullable=True),
    sa.Column('rapid', sa.Integer(), nullable=True),
    sa.Column('permanent', sa.Integer(), nullable=True),
    sa.Column('emergency_total', sa.Integer(), nullable=True),
    sa.Column('transitional_total', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transitional',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('board', sa.PickleType(), nullable=True),
    sa.Column('maximum', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transitional')
    op.drop_table('score')
    op.drop_table('rapid')
    op.drop_table('permanent')
    op.drop_table('log')
    op.drop_table('emergency')
    op.drop_table('game')
    # ### end Alembic commands ###
