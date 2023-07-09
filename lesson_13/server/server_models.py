from datetime import datetime
from sqlalchemy import (create_engine, String, DateTime, Integer, ForeignKey,
                        MetaData)
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ServerStorage:
    class AllUsers(Base):
        __tablename__ = "all_users"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50))
        last_login: Mapped[DateTime] = mapped_column(DateTime(),
                                                     default=datetime.now())

    class ActiveUsers(Base):
        __tablename__ = "active_users"

        id: Mapped[int] = mapped_column(primary_key=True)
        user: Mapped[int] = mapped_column(ForeignKey("all_users.id",
                                                     onupdate="CASCADE",
                                                     ondelete="CASCADE"))
        login_time: Mapped[DateTime] = mapped_column(DateTime(),
                                                     default=datetime.now())
        ip_address: Mapped[str] = mapped_column(String(15))
        port: Mapped[int] = mapped_column(Integer())

    class LoginHistory(Base):
        __tablename__ = "login_history"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[int] = mapped_column(ForeignKey("all_users.id",
                                                     onupdate="CASCADE",
                                                     ondelete="CASCADE"))
        date_time: Mapped[DateTime] = mapped_column(DateTime(),
                                                    default=datetime.now())
        ip: Mapped[str] = mapped_column(String(15))
        port: Mapped[int] = mapped_column(Integer())

    class UsersContacts(Base):
        __tablename__ = "user_contacts"

        id: Mapped[int] = mapped_column(primary_key=True)
        user: Mapped[int] = mapped_column(ForeignKey("all_users.id",
                                                     onupdate="CASCADE",
                                                     ondelete="CASCADE"))
        contact: Mapped[int] = mapped_column(ForeignKey("all_users.id",
                                                     onupdate="CASCADE",
                                                     ondelete="CASCADE"))

    class UsersHistory(Base):
        __tablename__ = "users_history"

        id: Mapped[int] = mapped_column(primary_key=True)
        user: Mapped[int] = mapped_column(ForeignKey("all_users.id",
                                                     onupdate="CASCADE",
                                                     ondelete="CASCADE"))
        sent: Mapped[int] = mapped_column(Integer(), default=0)
        accepted: Mapped[int] = mapped_column(Integer(), default=0)

    def __init__(self, path):
        self.database_engine = create_engine(
            f"sqlite:///{path}", echo=False,
            pool_recycle=7200,
            connect_args=dict(check_same_thread=False))

        self.metadata = MetaData()

        self.metadata.create_all(self.database_engine)

        self.session = sessionmaker(bind=self.database_engine)()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        rez = self.session.query(self.AllUsers).filter_by(name=username)

        if rez.count():
            user = rez.first()
            user.last_login = datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
            user_in_history = self.UsersHistory(user.id)
            self.session.add(user_in_history)

        new_active_user = self.ActiveUsers(user.id, ip_address, port,
                                           datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user.id, datetime.now(),
                                    ip_address, port)
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(
            name=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender, recipient):
        sender = self.session.query(self.AllUsers).filter_by(
            name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(
            name=recipient).first().id
        sender_row = self.session.query(self.UsersHistory).filter_by(
            user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(
            user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    def add_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(
            name=contact).first()

        if not contact or self.session.query(self.UsersContacts).filter_by(
                user=user.id, contact=contact.id).count():
            return

        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(
            name=contact).first()

        if not contact:
            return

        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )
        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    def get_contacts(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).one()

        query = self.session.query(self.UsersContacts, self.AllUsers.name). \
            filter_by(user=user.id). \
            join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)

        return [contact[1] for contact in query.all()]

    def message_history(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)
        return query.all()
