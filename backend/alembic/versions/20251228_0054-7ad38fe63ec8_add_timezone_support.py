"""add_timezone_support

Revision ID: 7ad38fe63ec8
Revises: 4c6eb92e9a01
Create Date: 2025-12-28 00:54:25.433349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ad38fe63ec8'
down_revision = '4c6eb92e9a01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert all TIMESTAMP columns to TIMESTAMP WITH TIME ZONE
    op.execute('ALTER TABLE contents ALTER COLUMN publish_date TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE contents ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE contents ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE')

    op.execute('ALTER TABLE summaries ALTER COLUMN generated_at TYPE TIMESTAMP WITH TIME ZONE')

    op.execute('ALTER TABLE themes ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE themes ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE')

    op.execute('ALTER TABLE content_themes ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE')


def downgrade() -> None:
    # Revert to TIMESTAMP WITHOUT TIME ZONE
    op.execute('ALTER TABLE contents ALTER COLUMN publish_date TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE contents ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE contents ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE')

    op.execute('ALTER TABLE summaries ALTER COLUMN generated_at TYPE TIMESTAMP WITHOUT TIME ZONE')

    op.execute('ALTER TABLE themes ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE themes ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE')

    op.execute('ALTER TABLE content_themes ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE')
