import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    create_engine,
    String,
    Text,
    DateTime,
    ForeignKey
)


class ClientDatabase:
    class Base(DeclarativeBase):
        pass

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

        self.metadata = self.Base.metadata
        self.metadata.create_all(self.database_engine)

        self.session = sessionmaker(bind=self.database_engine)()
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact: str) -> None:
        """
        Create a new contact and add it into database
        :param contact: a contact name
        :return:
        """
        if not self.session.query(
                self.Contacts
        ).filter_by(name=contact).count():
            contact_row = self.Contacts()
            contact_row.name = contact
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact: str) -> None:
        """
        Delete contact from database
        :param contact: a contact name
        :return:
        """
        self.session.query(self.Contacts).filter_by(name=contact).delete()

    def add_users(self, users_list: list) -> None:
        """
        Add users in list known contacts
        :param users_list: a known contact list
        :return:
        """
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers()
            user_row.username = user
            self.session.add(user_row)
        self.session.commit()

    def save_message(self,
                     contact: str,
                     direction: str,
                     message: str) -> None:
        """

        :param contact: a contact name
        :param direction: direction of message sending
        :param message: message text
        :return:
        """
        message_row = self.MessageHistory()
        message_row.contact = contact
        message_row.direction = direction
        message_row.body = message
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self) -> list:
        """
        Return all contacts
        :return: list of contact names
        """
        return [contact[0]
                for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self) -> list:
        """
        Return all known users
        :return:
        """
        return [user[0]
                for user in self.session.query(self.KnownUsers.username).all()]

    def user_exists(self, user: str) -> bool:
        """
        Check either user exists or not
        :param user: a username
        :return:
        """
        if self.session.query(
                self.KnownUsers
        ).filter_by(username=user).count():
            return True
        else:
            return False

    def contact_exists(self, contact: str) -> bool:
        """
        Check either contact exists or not
        :param contact: a contact name
        :return:
        """
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact: str) -> list[tuple]:
        """
        Return message history with the contact
        :param contact: a contact name
        :return:
        """
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
