from mautrix.types import EventType, RelationType
from mautrix.errors import MForbidden
from maubot import Plugin, MessageEvent
from maubot.handlers import event


class AntiThreadBot(Plugin):
    @event.on(EventType.ROOM_MESSAGE)
    async def handler(self, evt: MessageEvent) -> None:
        if evt.content.relates_to.rel_type == RelationType.THREAD:
            try:
                await evt.redact(reason="Threads are not allowed in this room")
            except MForbidden:
                # TODO leave room if the bot isn't promoted to have redact permissions?
                pass

    # TODO remove separate handler after maubot v0.5.0
    @event.on(EventType.ROOM_ENCRYPTED)
    async def encrypted_handler(self, evt: MessageEvent) -> None:
        await self.handler(evt)
