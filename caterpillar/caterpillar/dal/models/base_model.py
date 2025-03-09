from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing_extensions import Annotated

pk_int = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    pass
