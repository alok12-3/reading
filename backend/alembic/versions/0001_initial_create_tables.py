"""initial_migration_create_tables

Revision ID: 0001_initial
Revises:
Create Date: <timestamp_will_be_filled_by_actual_creation_time>

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('user',
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('passage',
        sa.Column('text', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('question',
        sa.Column('question_text', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('passage_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['passage_id'], ['passage.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vocabentry',
        sa.Column('word', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('meaning', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('passage_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['passage_id'], ['passage.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('passage_id', 'word', name='uix_passage_word')
    )
    op.create_table('answer',
        sa.Column('answer_text', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('answer')
    op.drop_table('vocabentry')
    op.drop_table('question')
    op.drop_table('passage')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
