"""Add author_edit

Revision ID: d2082408e9ef
Revises: 1dcfdcaa151f
Create Date: 2024-10-25 12:27:14.420028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2082408e9ef'
down_revision = '1dcfdcaa151f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions', sa.Column('author_edit', sa.String(), nullable=True))
    op.add_column('sub_questions', sa.Column('author_edit', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sub_questions', 'author_edit')
    op.drop_column('questions', 'author_edit')
    # ### end Alembic commands ###