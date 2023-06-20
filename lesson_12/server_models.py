from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Clients(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    last_login: Mapped[DateTime] = mapped_column(DateTime(),
                                                 default=datetime.now())
    info: Mapped[str] = mapped_column(Text(), nullable=True)


class ClientsHistory(Base):
    __tablename__ = "clients_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", onupdate="CASCADE", ondelete="CASCADE"))
    last_login: Mapped[DateTime] = mapped_column(DateTime(),
                                                 default=datetime.now())
    ip_address: Mapped[str] = mapped_column(String(15))
    port: Mapped[int] = mapped_column(Integer())


class ActiveClients(Base):
    __tablename__ = "active_clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id",
                                                      onupdate="CASCADE",
                                                      ondelete="CASCADE"))


class ContactList(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))


class MessageHistory(Base):
    __tablename__ = "message_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    to_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    datetime: Mapped[DateTime] = mapped_column(DateTime(),
                                               default=datetime.now())
    body: Mapped[Text] = mapped_column(Text(), nullable=False)
