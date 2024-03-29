import os
from datetime import datetime
from sqlalchemy import (
    create_engine,
    String,
    Text,
    MetaData,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ClientDatabase:
    class KnownUsers(Base):
        __tablename__ = "known_users"

        id: Mapped[int] = mapped_column(primary_key=True)
        username: Mapped[str] = mapped_column(String(50))

    class MessageHistory(Base):
        __tablename__ = "message_history"
        id: Mapped[int] = mapped_column(primary_key=True)
        contact: Mapped[int] = mapped_column(
            ForeignKey("contacts.id", onupdate="CASCADE", ondelete="CASCADE")
        )
        direction: Mapped[int] = mapped_column(
            ForeignKey("contacts.id", onupdate="CASCADE", ondelete="CASCADE")
        )
        datetime: Mapped[DateTime] = mapped_column(DateTime(),
                                                   default=datetime.now())
        body: Mapped[Text] = mapped_column(Text(), nullable=False)

    class Contacts(Base):
        __tablename__ = "contacts"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50))

    def __init__(self, name: str):
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f"client_{name}.db3"
        self.database_engine = create_engine(
            f"sqlite:///{os.path.join(path, filename)}",
            echo=False,
            pool_recycle=7200,
            connect_args=dict(check_same_thread=False),
        )

        self.metadata = MetaData()
        # self.KnownUsers.__table__.create(self.database_engine)
        # self.MessageHistory.__table__.create(self.database_engine)
        # self.Contacts.__table__.create(self.database_engine)
        self.metadata.create_all(self.database_engine)

        self.session = sessionmaker(bind=self.database_engine)()
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact: str):
        if not self.session.query(
                self.Contacts
        ).filter_by(name=contact).count():
            contact_row = self.Contacts()
            contact_row.name = contact
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact: str):
        self.session.query(self.Contacts).filter_by(name=contact).delete()

    def add_users(self, users_list: list):
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers()
            user_row.username = user
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message: str):
        message_row = self.MessageHistory()
        message_row.contact = contact.id
        message_row.direction = direction.id
        message_row.body = message
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        return [contact[0]
                for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        return [user[0]
                for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user: str):
        if self.session.query(
                self.KnownUsers
        ).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact: str):
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact: str):
        query = self.session.query(
            self.MessageHistory
        ).filter_by(contact=contact)
        return [
            (
                history_row.contact,
                history_row.direction,
                history_row.body,
                history_row.datetime,
            )
            for history_row in query.all()
        ]
