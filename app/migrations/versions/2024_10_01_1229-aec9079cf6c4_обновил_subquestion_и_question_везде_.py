"""обновил SubQuestion и Question везде теперь есть категории и подкатегории

Revision ID: aec9079cf6c4
Revises: 5c2c5a5d153e
Create Date: 2024-10-01 12:29:53.375225

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "aec9079cf6c4"
down_revision = "5c2c5a5d153e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "questions", sa.Column("subcategory_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_questions_subcategory_id",
        "questions",
        "categories",
        ["subcategory_id"],
        ["id"],
    )
    op.add_column(
        "sub_questions", sa.Column("category_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "sub_questions",
        sa.Column("subcategory_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_subquestions_subcategory_id",
        "sub_questions",
        "categories",
        ["subcategory_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_subquestions_category_id",
        "sub_questions",
        "categories",
        ["category_id"],
        ["id"],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_subquestions_category_id", "sub_questions", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_subquestions_subcategory_id", "sub_questions", type_="foreignkey"
    )
    op.drop_column("sub_questions", "subcategory_id")
    op.drop_column("sub_questions", "category_id")
    op.drop_constraint(
        "fk_questions_subcategory_id", "questions", type_="foreignkey"
    )
    op.drop_column("questions", "subcategory_id")
    # ### end Alembic commands ###
