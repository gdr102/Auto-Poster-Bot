import asyncio
import os
import yadisk

from telethon import TelegramClient, events
from app.core.database.requests import Query
from telethon.tl.types import MessageMediaPhoto
from app.core.system.formating_dict import format_dict

class Client:
    def __init__(self, session, api_id, api_hash, ya_token, async_session) -> None:
        self.client = TelegramClient(session, api_id, api_hash) # anon
        self.ya = yadisk.YaDisk(token=ya_token)
        self.db_session = Query(async_session)
        self.event = asyncio.Event()

    async def start(self, phone_number):
        await self.client.start(phone=phone_number)

    async def get_post(self):
        return await self.db_session.get_post()
    
    async def update_link(self, post_id, link):
        return await self.db_session.update_link(post_id, link)
    
    async def update_status(self, post_id):
        return await self.db_session.update_status(post_id)

    async def create_img(self, chat, query, path):
        self.message = await self.client.send_message(chat, query)

        @self.client.on(events.NewMessage(chats=chat, incoming=True))
        async def handler(event):
            if event.message.media:
                if isinstance(event.message.media, MessageMediaPhoto):
                    photo = event.message.media
                    await self.client.download_media(photo, file=path)
                    self.event.set() 
                else:
                    await self.retry_create_img(chat, query, path)
            else:
                await self.retry_create_img(chat, query, path)

        await self.event.wait()

    async def retry_create_img(self, chat, query, path):
        await self.create_img(chat, query, path)

    async def upload_image(self, post_id, local_path, yad_path):
        local_path = local_path.format(name=post_id)
        yad_path = yad_path.format(name=post_id)
        
        img = self.ya.upload(local_path, yad_path)

        if img:
            publish = img.publish()

            if os.path.exists(local_path):
                os.remove(local_path)

            return publish.get_download_link()

    async def send_message(self, channel, bot_parametrs, yad_path):
        post = await self.get_post()

        if post:
            params = format_dict(bot_parametrs, post)
            await self.create_img(**params)

            photo_path = params['path']

            link = await self.upload_image(post.id, photo_path, yad_path)

            await self.update_link(post.id, link)

            if link:
                await self.client.send_file(channel, file=link, caption=post.text)

                await self.update_status(post.id)
            else:
                print('exit!')

            await self.client.disconnect()

    async def disconnect(self):
        self.client.disconnect()