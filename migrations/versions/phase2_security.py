"""Add 2FA and audit log fields for Phase 2 security

Revision ID: phase2_security
Revises: 
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'phase2_security'
down_revision = None  # Update this if you have previous migrations
branch_labels = None
depends_on = None


def upgrade():
    # Add 2FA fields to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('two_factor_secret', sa.String(32), nullable=True))
        batch_op.add_column(sa.Column('two_factor_enabled', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('backup_codes', sa.Text(), nullable=True))
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(120), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.create_index('ix_audit_logs_event_type', ['event_type'], unique=False)
        batch_op.create_index('ix_audit_logs_timestamp', ['timestamp'], unique=False)
        batch_op.create_index('ix_audit_logs_user_id', ['user_id'], unique=False)


def downgrade():
    # Drop audit_logs table
    op.drop_table('audit_logs')
    
    # Remove 2FA fields from users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('backup_codes')
        batch_op.drop_column('two_factor_enabled')
        batch_op.drop_column('two_factor_secret')
