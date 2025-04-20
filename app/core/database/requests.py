import app.core.database.models as db

from sqlalchemy import select, update, func

class Query:
    def __init__(self, session) -> None:
        self.session = session

    async def get_post(self):
        async with self.session() as session:
            return await session.scalar(select(db.Posts).order_by(func.random()).where(db.Posts.status == 0))
        
    async def update_link(self, post_id, link):
        async with self.session() as session:
            post = await session.scalar(select(db.Posts).where(db.Posts.id == post_id))

            if post:
                await session.execute(update(db.Posts).where(db.Posts.id == post_id).values(img = link))
                await session.commit()

    async def update_status(self, post_id):
        async with self.session() as session:
            post = await session.scalar(select(db.Posts).where(db.Posts.id == post_id))

            if post:
                await session.execute(update(db.Posts).where(db.Posts.id == post_id).values(status = 1))
                await session.commit()