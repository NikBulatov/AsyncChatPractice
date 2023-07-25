from datetime import datetime
from typing import NoReturn, Iterable

from Crypto.PublicKey import RSA
from sqlalchemy import create_engine, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column


class ServerStorage:
    class Base(DeclarativeBase):
        pass

    class AllUsers(Base):
        __tablename__ = "all_users"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50))
        last_login: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
        pubkey: Mapped[Text] = mapped_column(Text(), default=None, nullable=True)
        password_hash: Mapped[Text] = mapped_column(Text())

    class ActiveUsers(Base):
        __tablename__ = "active_users"

        id: Mapped[int] = mapped_column(primary_key=True)
        user: Mapped[int] = mapped_column(
            ForeignKey("all_users.id", onupdate="CASCADE", ondelete="CASCADE")
        )
        login_time: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
        ip_address: Mapped[str] = mapped_column(String(15))
        port: Mapped[int] = mapped_column(Integer())

    class LoginHistory(Base):
        __tablename__ = "login_history"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[int] = mapped_column(
            ForeignKey("all_users.id", onupdate="CASCADE", ondelete="CASCADE")
        )
        date_time: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
        ip: Mapped[str] = mapped_column(String(15))
        port: Mapped[int] = mapped_column(Integer())

    class UsersContacts(Base):
        __tablename__ = "user_contacts"

        id: Mapped[int] = mapped_column(primary_key=True)
        user: Mapped[int] = mapped_column(
            ForeignKey("all_users.id", onupdate="CASCADE", ondelete="CASCADE")
        )
        contact: Mapped[int] = mapped_column(
            ForeignKey("all_users.id", onupdate="CASCADE", ondelete="CASCADE")
        )

    class UsersHistory(Base):
        __tablename__ = "users_history"

        id: Mapped[int] = mapped_column(primary_key=True)
        user: Mapped[int] = mapped_column(
            ForeignKey("all_users.id", onupdate="CASCADE", ondelete="CASCADE")
        )
        sent: Mapped[int] = mapped_column(Integer(), default=0)
        accepted: Mapped[int] = mapped_column(Integer(), default=0)

    def __init__(self, path):
        self.database_engine = create_engine(
            f"sqlite:///{path}",
            echo=False,
            pool_recycle=7200,
            connect_args=dict(check_same_thread=False),
        )

        self.metadata = self.Base.metadata
        self.metadata.create_all(self.database_engine)
        self.session = sessionmaker(bind=self.database_engine)()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(
        self, username: str, ip_address: str, port: int, key: RSA
    ) -> None | NoReturn:
        """
        Check user exists and add it into database
        ("ActiveUsers" and "LoginHistory" tables)
        :param username:
        :param ip_address:
        :param port:
        :param key:
        :return:
        """
        result = self.session.query(self.AllUsers).filter_by(name=username)

        if result.count():
            user = result.first()
            user.last_login = datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        else:
            raise ValueError("User is not registered")

        new_active_user = self.ActiveUsers()
        new_active_user.user = user.id
        new_active_user.ip_address = ip_address
        new_active_user.port = port
        new_active_user.login_time = datetime.now()
        self.session.add(new_active_user)

        history = self.LoginHistory()
        history.name = user.id
        history.ip = ip_address
        history.port = port
        history.date_time = datetime.now()
        self.session.add(history)
        self.session.commit()

    def add_user(self, name: str, password_hash: str) -> None:
        """
        Add a new user into database ("AllUsers" and "UsersHistory" tables)
        :param name:
        :param password_hash:
        :return:
        """
        user_row = self.AllUsers(name=name, password_hash=password_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user=user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name: str) -> None:
        """
        Remove user from database (All tables)
        :param name:
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name: str) -> bytes:
        """
        Return the user's password hash
        :param name: a username
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.password_hash

    def get_pubkey(self, name: str) -> str:
        """
        Return the user's public key
        :param name: a username
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pubkey

    def user_exists(self, name: str) -> bool:
        """
        Check either user exists or not
        :param name:
        :return:
        """
        if self.session.query(self.AllUsers).filter_by(name=name).count():
            return True
        else:
            return False

    def user_logout(self, name: str) -> None:
        """
        Delete the user from ActiveUsers table
        :param name: a username
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender: str, recipient: str) -> None:
        """
        Chat message handler
        :param sender:
        :param recipient:
        :return:
        """
        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = (
            self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        )

        sender_row = (
            self.session.query(self.UsersHistory).filter_by(user=sender).first()
        )

        sender_row.sent += 1
        recipient_row = (
            self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        )
        recipient_row.accepted += 1
        self.session.commit()

    def add_contact(self, user: AllUsers, contact: UsersContacts) -> None:
        """
        Add the user into contact list
        :param user: instance of AllUsers model
        :param contact: instance of UserContacts model
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        if (
            not contact
            or self.session.query(self.UsersContacts)
            .filter_by(user=user.id, contact=contact.id)
            .count()
        ):
            return

        contact_row = self.UsersContacts()
        contact_row.user = user.id
        contact_row.contact = contact.id
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user: AllUsers, contact: UsersContacts) -> None:
        """
        Remove the user from contact list
        :param user: instance of AllUsers model
        :param contact: instance of UsersContacts model
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        if not contact:
            return

        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id, self.UsersContacts.contact == contact.id
        ).delete()
        self.session.commit()

    @property
    def users_list(self) -> Iterable:
        """
        Return all users (name and last login datetime)
        :return:
        """
        query = self.session.query(self.AllUsers.name, self.AllUsers.last_login)
        return query.all()

    def active_users_list(self) -> Iterable:
        """
        Return active users
        :return:
        """
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time,
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, name: str = None) -> Iterable:
        """
        Return all users' login history
        :param name: a username
        :return:
        """
        query = self.session.query(
            self.AllUsers.name,
            self.LoginHistory.date_time,
            self.LoginHistory.ip,
            self.LoginHistory.port,
        ).join(self.AllUsers)
        if name:
            query = query.filter(self.AllUsers.name == name)
        return query.all()

    def get_contacts(self, name: str) -> Iterable:
        """
        Return the user's contacts
        :param name: a username
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=name).one()

        query = (
            self.session.query(self.UsersContacts, self.AllUsers.name)
            .filter_by(user=user.id)
            .join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)
        )

        return [contact[1] for contact in query.all()]

    def message_history(self) -> Iterable:
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted,
        ).join(self.AllUsers)
        return query.all()
