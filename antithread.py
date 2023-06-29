from __future__ import annotations

import time

from mautrix.types import (
    EventType,
    RelationType,
    EncryptedEvent,
    EncryptedMegolmEventContent,
    RoomID,
)
from mautrix.errors import MForbidden
from maubot import Plugin, MessageEvent
from maubot.handlers import event


promotion_timeout = 5 * 60


class AntiThreadBot(Plugin):
    _pending_leaves: dict[RoomID, float]

    async def start(self) -> None:
        self._pending_leaves = {}

    @event.on(EventType.ROOM_MESSAGE)
    async def handler(self, evt: MessageEvent) -> None:
        if evt.content.relates_to.rel_type == RelationType.THREAD:
            try:
                await evt.redact(reason="Threads are not allowed in this room")
            except MForbidden:
                await self._leave_if_no_permissions(evt.room_id)

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
                await self._leave_if_no_permissions(evt.room_id)

    async def _leave_if_no_permissions(self, room_id: RoomID) -> None:
        now = time.monotonic()
        if self._pending_leaves.setdefault(room_id, now) + promotion_timeout < now:
            # Reset timer in case bot is re-invited
            self._pending_leaves.pop(room_id, None)
            await self.client.leave_room(room_id, reason="I still don't have redaction permissions")
