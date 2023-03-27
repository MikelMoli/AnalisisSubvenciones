import os
import sys
sys.path.append(os.getcwd())
from utils.constants import DB_CONNECTION_URL
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, Float, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import MappedAsDataclass
from typing import List, Optional

DB_SCHEMA = "extract_directory"

class Base(MappedAsDataclass, DeclarativeBase):
    pass

class RelatedActors(Base):
    __tablename__ = "related_actors"
    __table_args__ = {"schema": DB_SCHEMA}

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_one_id: Mapped[str] = mapped_column(String)
    actor_two_id: Mapped[str] = mapped_column(String)

class Actor(Base):
    __tablename__ = "actor"
    __table_args__ = {"schema": DB_SCHEMA}


    oid: Mapped[str] = mapped_column(primary_key=True)
    id: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    subtype: Mapped[str] = mapped_column(String)
    creation_date: Mapped[str] = mapped_column(TIMESTAMP)
    last_update: Mapped[str] = mapped_column(String)


    sector_list: Mapped[List["Sector"]] = relationship()
    municipality: Mapped["Municipality"] = relationship(back_populates="actor")
    contact_phone_list: Mapped[List["ContactPhone"]] = relationship()
    contact_email_list: Mapped[List["ContactEmail"]] = relationship()
    contact_website_list: Mapped[List["ContactWebsite"]] = relationship()


class Municipality(Base):
    __tablename__ = "municipality"
    __table_args__ = {"schema": DB_SCHEMA}

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.actor.oid"))
    actor: Mapped["Actor"] = relationship(back_populates="municipality")
    country: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String, nullable=True)
    county: Mapped[str] = mapped_column(String, nullable=True)
    municipality: Mapped[str] = mapped_column(String, nullable=True)
    locality: Mapped[str] = mapped_column(String, nullable=True)
    street: Mapped[str] = mapped_column(String, nullable=True)
    portal: Mapped[str] = mapped_column(String, nullable=True)
    zipcode: Mapped[str] = mapped_column(String, nullable=True)
    floor: Mapped[str] = mapped_column(String, nullable=True)


class Sector(Base):
    __tablename__ = "sector"
    __table_args__ = {"schema": "extract_directory"}

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.actor.oid"))

class ContactPhone(Base):

    __tablename__ = "phone"
    __table_args__ = {"schema": "extract_directory"}

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.actor.oid"))
    type: Mapped[str] = mapped_column(String, nullable=True)
    usage: Mapped[str] = mapped_column(String, nullable=True)


class ContactEmail(Base):

    __tablename__ = "email"
    __table_args__ = {"schema": "extract_directory"}

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.actor.oid"))
    usage: Mapped[str] = mapped_column(String, nullable=True)

class ContactWebsite(Base):

    __tablename__ = "website"
    __table_args__ = {"schema": "extract_directory"}

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    website: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.actor.oid"))
    usage: Mapped[str] = mapped_column(String, nullable=True)


class CreateDatabase:
    
    def __init__(self) -> None:
        self.engine = create_engine(DB_CONNECTION_URL, echo=False)
        # TODO: Comprobar si se puede meter aquí el schema en el BASE
        self.base = Base()

    def run(self):
        metadata = Base.metadata
        Base.metadata.create_all(self.engine)

if __name__=='__main__':
    cd = CreateDatabase()
    cd.run()
