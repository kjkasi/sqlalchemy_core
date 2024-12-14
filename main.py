from typing import Optional
from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy import URL, Column, Integer, MetaData, String, Table, func, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from pydantic import BaseModel

app = FastAPI(debug=True)


@app.get(
    "/",
    include_in_schema=False,
)
async def get_root():
    return RedirectResponse("docs")


url_sql = URL.create(
    drivername="mssql+aioodbc",
    username="sa",
    password="Pass!word",
    host="sqldata",
    database="AdventureWorksDW2017",
    query={"driver": "ODBC Driver 17 for SQL Server"},
)

async_engine: AsyncEngine = create_async_engine(url=url_sql, pool_pre_ping=True)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
)


async def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


metadata_obj = MetaData()


organization = Table(
    "DimOrganization",
    metadata_obj,
    Column("OrganizationKey", Integer, primary_key=True),
    Column("ParentOrganizationKey", Integer, nullable=True),
    Column("PercentageOfOwnership", String(16), nullable=True),
    Column("OrganizationName", String(50), nullable=True),
    Column("CurrencyKey", Integer, nullable=True),
)


class Organisation(BaseModel):
    OrganizationKey: int
    ParentOrganizationKey: Optional[int] = None
    PercentageOfOwnership: Optional[str] = None
    OrganizationName: Optional[str] = None
    CurrencyKey: Optional[int] = None


class Response(BaseModel):
    data: list[Organisation]
    count: int = 0


@app.get("/organizations", response_model=Response)
async def get_organizations(session: AsyncSession = Depends(get_session)):
    query = select(organization, func.count().over().label("total"))
    result = await session.execute(query)

    data = []
    count = 0
    for dict_row in result.mappings():
        data.append(dict_row)
        count = int(dict_row.total)

    return Response(data=data, count=count)
