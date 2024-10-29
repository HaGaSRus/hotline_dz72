"""Fix migration for sub_questions

Revision ID: a567df114967
Revises: 303bbd72f67d
Create Date: 2024-10-29 11:44:44.194742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a567df114967'
down_revision = '303bbd72f67d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('subcategory_id', sa.Integer(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('answer', sa.String(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('parent_question_id', sa.Integer(), nullable=True),
    sa.Column('depth', sa.Integer(), nullable=False),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('author_edit', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_questions_category_id'),
    sa.ForeignKeyConstraint(['parent_question_id'], ['questions.id'], name='fk_questions_parent_id'),
    sa.ForeignKeyConstraint(['subcategory_id'], ['categories.id'], name='fk_questions_subcategory_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    op.create_index(op.f('ix_questions_text'), 'questions', ['text'], unique=False)
    op.create_table('sub_questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_question_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('subcategory_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('answer', sa.String(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('depth', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('author_edit', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('parent_subquestion_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_subquestions_category_id'),
    sa.ForeignKeyConstraint(['parent_question_id'], ['questions.id'], name='fk_subquestions_question_id'),
    sa.ForeignKeyConstraint(['parent_subquestion_id'], ['sub_questions.id'], name='fk_subquestions_parent_subquestion_id'),
    sa.ForeignKeyConstraint(['subcategory_id'], ['categories.id'], name='fk_subquestions_subcategory_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sub_questions_id'), 'sub_questions', ['id'], unique=False)
    op.create_index(op.f('ix_sub_questions_text'), 'sub_questions', ['text'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sub_questions_text'), table_name='sub_questions')
    op.drop_index(op.f('ix_sub_questions_id'), table_name='sub_questions')
    op.drop_table('sub_questions')
    op.drop_index(op.f('ix_questions_text'), table_name='questions')
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
    # ### end Alembic commands ###
