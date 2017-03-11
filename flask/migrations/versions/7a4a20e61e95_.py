"""empty message

Revision ID: 7a4a20e61e95
Revises:
Create Date: 2017-03-11 01:17:33.755647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a4a20e61e95'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_name', sa.String(length=40), nullable=True),
    sa.Column('start_datetime', sa.DateTime(), nullable=True),
    sa.Column('round_count', sa.Integer(), nullable=True),
    sa.Column('round_over', sa.Boolean(), nullable=True),
    sa.Column('diversion', sa.Boolean(), nullable=True),
    sa.Column('available', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('market', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('unsheltered', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('intake', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('emergency', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('rapid', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('outreach', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('transitional', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('permanent', sa.ARRAY(sa.Integer()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('score',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('emergency_count', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('transitional_count', sa.ARRAY(sa.Integer()), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('score')
    op.drop_table('game')
    # ### end Alembic commands ###
