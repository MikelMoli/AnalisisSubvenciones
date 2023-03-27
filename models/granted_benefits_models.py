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
