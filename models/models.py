from sqlalchemy import create_engine, Table, Column, MetaData, Integer, Float, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import MappedAsDataclass
from typing import List, Optional

class Base(MappedAsDataclass, DeclarativeBase):
    pass

class Municipality(Base):
    __tablename__ = "municipality"

    municipality_code: Mapped[str] = mapped_column(primary_key=True)
    country: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    province: Mapped[str] = mapped_column(String)
    municipal_name: Mapped[str] = mapped_column(String)

    entity_list: Mapped[List["Entity"]] = relationship(back_populates="municipality")

class Entity(Base):

    __tablename__ = "entity"

    oid: Mapped[str] = mapped_column(primary_key=True)
    id_entity: Mapped[str] = mapped_column(String, unique=True)
    entity_name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    subtype: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    municipality_code = mapped_column(ForeignKey("municipality.municipality_code"))
    creation_date: Mapped[str] = mapped_column(TIMESTAMP)
    last_update: Mapped[str] = mapped_column(String)

    municipality: Mapped[Municipality] = relationship(back_populates="entity_list")
    people_list: Mapped[List["EntityPerson"]] = relationship(back_populates="id_entity")

class EntityPerson(Base):

    __tablename__ = "persona_de_entidad"

    oid: Mapped[str] = mapped_column(primary_key=True)
    id_person: Mapped[str] = mapped_column(String)
    id_entity: Mapped[str] = mapped_column(ForeignKey("entity.id_entity"))
    person_name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    subtype: Mapped[str] = mapped_column(String)
    creation_date: Mapped[str] = mapped_column(TIMESTAMP)
    last_update: Mapped[str] = mapped_column(TIMESTAMP)

    entity: Mapped[Entity] = relationship(back_populates="people_list")

class Group(Base):
    __tablename__ = "group"
    
    id_group: Mapped[str] = mapped_column(primary_key=True)
    group_name: Mapped[str] = mapped_column(String)

    list_conveners: Mapped["Convener"] = relationship(back_populates="id_convener")

class Organization(Base):
    __tablename__ = "organization"
    
    id_organization: Mapped[str] = mapped_column(primary_key=True)
    organization_name: Mapped[str] = mapped_column(String)

    list_conveners: Mapped["Convener"] = relationship(back_populates="id_convener")

class Area(Base):
    __tablename__ = "area"
    
    id_area: Mapped[str] = mapped_column(primary_key=True)
    area_name: Mapped[str] = mapped_column(String)

    list_conveners: Mapped["Convener"] = relationship(back_populates="id_convener")

class Service(Base):
    __tablename__ = "service"
    
    id_service: Mapped[str] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(String)

    list_conveners: Mapped["Convener"] = relationship(back_populates="id_convener")

class Convener(Base):
    __tablename__ = "convener"

    id_convener: Mapped[str] = mapped_column(primary_key=True)
    id_group: Mapped[Group] = mapped_column(ForeignKey("group.id_group"))
    id_organization: Mapped[Organization] = mapped_column(ForeignKey("organization.id_organization"))
    id_area: Mapped[Area] = mapped_column(ForeignKey("area.id_area"))
    id_service: Mapped[Service] = mapped_column(ForeignKey("service.id_service"))

    list_granted_benefits: Mapped["GrantedBenefits"] = relationship(back_populates="id_convener")

class GrantedBenefits(Base):
    __tablename__ = "granted_benefits"

    oid: Mapped[str] = mapped_column(String)
    id_subvencion: Mapped[str] = mapped_column(primary_key=True)
    benefit_name: Mapped[str] = mapped_column(String)
    regulation: Mapped[str] = mapped_column(String)
    id_benefited: Mapped[Entity] = mapped_column(ForeignKey("entity.id_entity"))
    name_benefited: Mapped[str] = mapped_column(String)
    given_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    quantity: Mapped[float] = mapped_column(Float)

    id_convener: Mapped[Convener] = mapped_column(ForeignKey("convener.id_convener"))

class ErroresProceso(Base):
    __tablename__ = "processing_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint_fallido: Mapped[str] = mapped_column(String)
    cod_error: Mapped[str] = mapped_column(String)
    mensaje_error: Mapped[str] = mapped_column(String)
    hora_error: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    id_grupo: Mapped[str] = mapped_column(String)
    id_organizacion: Mapped[str] = mapped_column(String)
    id_area: Mapped[str] = mapped_column(String)
    id_servicio: Mapped[str] = mapped_column(String)



class CreateDatabase:
    
    def __init__(self) -> None:
        self.engine = create_engine("postgresql+psycopg2://postgres:postgres@192.168.1.21/subvenciones_euskadi", echo=True)
        self.base = Base()

    def run(self):
        Base.metadata.create_all(self.engine)

if __name__=='__main__':
    cd = CreateDatabase()
    cd.run()