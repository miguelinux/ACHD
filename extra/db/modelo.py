# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Modelo de la base de datos con SQLAlchemy
"""

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


# declarative base class
class Base(DeclarativeBase):
    pass


# an example mapping using the base
class Persona(Base):
    __tablename__ = "persona"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(30), nullable=False)
    apellido_pat: Mapped[str] = mapped_column(String(22), nullable=False)
    apellido_mat: Mapped[str] = mapped_column(String(22), nullable=False)
