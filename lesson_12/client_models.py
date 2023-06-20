from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ContactList(Base):
    __tablename__ = "contact_list"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))


class MessageHistory(Base):
    __tablename__ = "message_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_id: Mapped[int] = mapped_column(ForeignKey("contact_list.id",
                                                    onupdate="CASCADE",
                                                    ondelete="CASCADE"))
    to_id: Mapped[int] = mapped_column(ForeignKey("contact_list.id",
                                                  onupdate="CASCADE",
                                                  ondelete="CASCADE"))
    datetime: Mapped[DateTime] = mapped_column(DateTime(),
                                               default=datetime.now())
    body: Mapped[Text] = mapped_column(Text(), nullable=False)
