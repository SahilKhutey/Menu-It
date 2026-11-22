"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-19 14:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.core.database import GUID

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Users
    op.create_table(
        'users',
        sa.Column('id', GUID(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('full_name', sa.String(150), nullable=False),
        sa.Column('is_platform_admin', sa.Boolean(), default=False, nullable=False),
        sa.Column('status', sa.String(30), default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 2. Organizations
    op.create_table(
        'organizations',
        sa.Column('id', GUID(), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, index=True, nullable=False),
        sa.Column('status', sa.String(30), default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 3. Restaurants
    op.create_table(
        'restaurants',
        sa.Column('id', GUID(), primary_key=True),
        sa.Column('organization_id', GUID(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, index=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('cover_url', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 4. Restaurant Members
    op.create_table(
        'restaurant_members',
        sa.Column('id', GUID(), primary_key=True),
        sa.Column('organization_id', GUID(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('restaurant_id', GUID(), sa.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', GUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('role', sa.String(40), default='menu_editor', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('restaurant_id', 'user_id', name='uq_restaurant_user')
    )


def downgrade() -> None:
    op.drop_table('restaurant_members')
    op.drop_table('restaurants')
    op.drop_table('organizations')
    op.drop_table('users')
