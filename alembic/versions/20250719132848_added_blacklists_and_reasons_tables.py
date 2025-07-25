"""added blacklists and reasons tables

Revision ID: 3200ffdffafc
Revises: 
Create Date: 2025-07-19 13:28:48.152149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3200ffdffafc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reasons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('blacklist_customers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('middle_name', sa.String(length=255), nullable=True),
    sa.Column('birth_date', sa.DateTime(), nullable=False),
    sa.Column('reason_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['reason_id'], ['reasons.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('first_name', 'last_name', 'middle_name', 'birth_date', name='unique_blacklist_per_full_name_and_birth_date')
    )

    reasons_table = sa.table(
        'reasons',
        sa.column('name', sa.String),
        sa.column('slug', sa.String),
        sa.column('description', sa.String)
    )

    op.bulk_insert(
        reasons_table,
        [
            {
                'name': 'Мошенничество',
                'slug': 'fraud',
                'description': 'Подозрение на мошеннические действия'
            },
            {
                'name': 'Задолженность',
                'slug': 'debt',
                'description': 'Имеется непогашенная задолженность'
            },
        ]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blacklist_customers')
    op.drop_table('reasons')
    # ### end Alembic commands ###
