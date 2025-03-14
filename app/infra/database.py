from typing import Any

from sqlalchemy import AsyncAdaptedQueuePool, Engine, create_engine, QueuePool
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

from config import settings


def get_engine(): # noqa: ANN201
    """Return an instance of a database connection sync engine using SQLAlchemy.

    Return:
    ------
        sqlalchemy.engine.base.Engine: An instance of the configured SQLAlchemy
        connection sync engine.

    """
    sqlalchemy_database_url = settings.DATABASE_URL

    return create_engine(
        sqlalchemy_database_url,
        echo=False,
        pool_size=10,
        max_overflow=5,
    )


def get_session(): # noqa: ANN201
    """Return a SQLAlchemy sync session factory with a configured engine.

    Return:
    ------
        sqlalchemy.orm.session.Session: A sync session factory configured to interact with
        the database using the specified engine.

    Note:
    ----
        To use this function, ensure that the 'get_engine()' function is correctly
        implemented and that the necessary database URL is provided in the project's
        settings.

    """
    _engine = get_engine()
    return sessionmaker(
        bind=_engine,
        expire_on_commit=False,
    )


def get_async_engine() -> AsyncEngine:
    """Return an instance of a database connection async engine using SQLAlchemy.

    Return:
    ------
        sqlalchemy.ext.asyncio.AsyncEngine: An instance of the configured SQLAlchemy
        connection async engine.

    """
    return create_async_engine(
        settings.DATABASE_URI,
        pool_size=10,
        max_overflow=5,
        echo=False,
        poolclass=AsyncAdaptedQueuePool,
    )


def get_async_session():
    """Return a SQLAlchemy async session factory with a configured engine.

    Return:
    ------
        sqlalchemy.orm.session.Session: A async session factory configured to interact with
        the database using the specified async engine with class AsyncSession.

    Note:
    ----
        To use this function, ensure that the 'get_async_engine()' function is correctly
        implemented and that the necessary database URI is provided in the project's
        settings.

    """
    return async_sessionmaker(
        bind=get_async_engine(),
        autocommit=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
