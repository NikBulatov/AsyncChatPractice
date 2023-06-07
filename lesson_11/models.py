from os import getenv
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv(".env")

engine = sqlalchemy.create_engine(getenv("DATABASE_URI"), echo=True)


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50))
    info: Mapped[str] = mapped_column(Text())


class ClientHistory(Base):
    __tablename__ = "client_history"

    id: Mapped[int] = mapped_column(ForeignKey("client.id"), primary_key=True)
    last_login: Mapped[DateTime] = mapped_column(DateTime())
    ip_address: Mapped[str] = mapped_column(String(15))


class Contacts(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer())
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))


if __name__ == "__main__":
    Base.metadata.create_all(engine)
