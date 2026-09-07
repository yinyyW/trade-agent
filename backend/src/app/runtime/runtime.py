from app.runtime.agent_runtime import AgentRuntime
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.rag.config import database_settings

def create_session_factory():
    """
    创建 SQLAlchemy AsyncSession 工厂。

    需要在 settings 中配置：
        database_url

    示例：

        mysql+aiomysql://root:password@127.0.0.1:3306/ai_trading
    """

    database_url = getattr(database_settings, "database_url", None)

    if not database_url:
        raise RuntimeError(
            "未配置 database_url，请在 .env 中配置 DATABASE_URL"
        )

    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine, session_factory

class ApplicationRuntime:

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.agent_runtime = None

    async def startup(self):

        # DB
        self.engine, self.session_factory = (
            create_session_factory()
        )

        # Agent
        self.agent_runtime = AgentRuntime(
            session_factory=self.session_factory
        )

        await self.agent_runtime.startup()

    async def shutdown(self):

        if self.agent_runtime:
            await self.agent_runtime.shutdown()

        if self.engine:
            await self.engine.dispose()