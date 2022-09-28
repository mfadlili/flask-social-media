"""empty message

Revision ID: 504036c22620
Revises: e1b6c33a7d26
Create Date: 2022-09-27 14:13:22.212375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '504036c22620'
down_revision = 'e1b6c33a7d26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_conversation_text_timestamp', table_name='conversation_text')
    op.drop_table('conversation_text')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conversation_text',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('message', sa.VARCHAR(), nullable=True),
    sa.Column('from_user_id', sa.INTEGER(), nullable=True),
    sa.Column('room_id', sa.INTEGER(), nullable=True),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['from_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['room_id'], ['room_chat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversation_text_timestamp', 'conversation_text', ['timestamp'], unique=False)
    # ### end Alembic commands ###
