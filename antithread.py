from mautrix.types import (
    EventType,
    RelationType,
    EncryptedEvent,
    EncryptedMegolmEventContent,
)
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

    @event.on(EventType.ROOM_ENCRYPTED)
    async def encrypted_handler(self, evt: EncryptedEvent) -> None:
        if (
            isinstance(evt.content, EncryptedMegolmEventContent)
            and evt.content.relates_to.rel_type == RelationType.THREAD
        ):
            try:
                await self.client.redact(
                    evt.room_id,
                    evt.event_id,
                    reason="Threads are not allowed in this room",
                )
            except MForbidden:
                pass
