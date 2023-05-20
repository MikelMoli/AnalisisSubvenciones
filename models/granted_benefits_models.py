import os
import sys
sys.path.append(os.getcwd())
from utils.constants import DB_CONNECTION_URL
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, Float, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import MappedAsDataclass
from typing import List, Optional

DB_SCHEMA = "extract_benefits"


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class GrantedBenefit(Base):
    __tablename__ = 'granted_benefits'
    __table_args__ = {"schema": DB_SCHEMA}

    oid: Mapped[str] = mapped_column(primary_key=True)
    benefit_id: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    regulation: Mapped[str] = mapped_column(String, nullable=True)
    beneficiary_id: Mapped[str] = mapped_column(String, nullable=True)
    beneficiary_name: Mapped[str] = mapped_column(String, nullable=True)
    granted_date: Mapped[str] = mapped_column(TIMESTAMP, nullable=True)
    granted_amount: Mapped[float] = mapped_column(Float, nullable=True)
    import_package_oid: Mapped[str] = mapped_column(String, nullable=True)
    convener_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.convener.id"), nullable=True)


class OrganizationGroup(Base):
    __tablename__ = 'organization_group'
    __table_args__ = {"schema": DB_SCHEMA}

    organization_group_id: Mapped[str] = mapped_column(primary_key=True)
    organization_group_name: Mapped[str] = mapped_column(String, nullable=True)


class Organization(Base):
    __tablename__ = 'organization'
    __table_args__ = {"schema": DB_SCHEMA}
    
    organization_id: Mapped[str] = mapped_column(primary_key=True)
    organization_name: Mapped[str] = mapped_column(String, nullable=True)


class Area(Base):
    __tablename__ = 'area'
    __table_args__ = {"schema": DB_SCHEMA}

    area_id: Mapped[str] = mapped_column(primary_key=True)
    area_name: Mapped[str] = mapped_column(String, nullable=True)


class Service(Base):
    __tablename__ = 'service'
    __table_args__ = {"schema": DB_SCHEMA}

    service_id: Mapped[str] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(String, nullable=True)


class Convener(Base):
    __tablename__ = 'convener'
    __table_args__ = {"schema": DB_SCHEMA}

    id: Mapped[str] = mapped_column(primary_key=True)
    organization_group_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.organization_group.organization_group_id"), nullable=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.organization.organization_id"), nullable=True)
    area_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.area.area_id"), nullable=True)
    service_id: Mapped[str] = mapped_column(ForeignKey(f"{DB_SCHEMA}.service.service_id"), nullable=True)


class CreateDatabase:
    def __init__(self) -> None:
        self.engine = create_engine(DB_CONNECTION_URL, echo=True)
        # TODO: Comprobar si se puede meter aquí el schema en el BASE
        self.base = Base()

    def run(self):
        metadata = Base.metadata
        Base.metadata.create_all(self.engine)


if __name__=='__main__':
    cd = CreateDatabase()
    cd.run()
