"""обновил Question и SubQuestions

Revision ID: 2c1514b19cab
Revises: 3c048ace1578
Create Date: 2024-09-30 17:04:24.721759

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c1514b19cab"
down_revision = "3c048ace1578"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_questions_subcategory_id", "questions", type_="foreignkey"
    )
    op.drop_column("questions", "subcategory_id")
    op.add_column(
        "sub_questions",
        sa.Column("parent_question_id", sa.Integer(), nullable=True),
    )
    op.drop_constraint(
        "fk_subquestions_question_id", "sub_questions", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_subquestions_parent_question_id",
        "sub_questions",
        "questions",
        ["parent_question_id"],
        ["id"],
    )
    op.drop_column("sub_questions", "question_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "sub_questions",
        sa.Column(
            "question_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(
        "fk_subquestions_parent_question_id",
        "sub_questions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_subquestions_question_id",
        "sub_questions",
        "questions",
        ["question_id"],
        ["id"],
    )
    op.drop_column("sub_questions", "parent_question_id")
    op.add_column(
        "questions",
        sa.Column(
            "subcategory_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.create_foreign_key(
        "fk_questions_subcategory_id",
        "questions",
        "categories",
        ["subcategory_id"],
        ["id"],
    )
    # ### end Alembic commands ###
