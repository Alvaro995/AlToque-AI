"""Servicio de estructuración de bloques de horario y rutinas fijas."""

from datetime import datetime, time
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ingestion import UploadedDocument, ScheduleBlock
from app.models.scheduling import SleepTarget
from app.services.llm_service import LLMService


class ScheduleParserService:
    """Service to parse, validate, and persist routine blocks and sleep targets."""

    def __init__(self):
        self.llm = LLMService()

    @staticmethod
    def _parse_time_str(time_str: str, default: time) -> time:
        """Helper to parse HH:MM or HH:MM:SS string into a datetime.time object."""
        try:
            parts = [int(p) for p in time_str.split(":")[:2]]
            return time(hour=parts[0], minute=parts[1])
        except Exception:
            return default

    async def parse_and_store_schedule_document(
        self,
        db: AsyncSession,
        document: UploadedDocument,
        raw_text: str,
    ) -> List[ScheduleBlock]:
        """Extract weekly blocks from text and generate sleep baseline."""
        system_prompt = (
            "You are an expert schedule extraction engine. Extract fixed weekly blocks "
            "from the schedule text. Output a JSON object with: "
            "'schedule_blocks': list of objects with 'day_of_week' (0=Monday, 6=Sunday), "
            "'start_time' (HH:MM:SS), 'end_time' (HH:MM:SS), "
            "'block_type' ('work', 'sleep', 'fixed', 'commute'), 'label' (string); "
            "'wake_time' (HH:MM:SS), 'bed_time' (HH:MM:SS)."
        )
        extraction = await self.llm.generate_structured_json(
            system_prompt=system_prompt,
            user_prompt=raw_text,
        )

        blocks_data = extraction.get("schedule_blocks", [])
        created_blocks: List[ScheduleBlock] = []

        for item in blocks_data:
            dow = int(item.get("day_of_week", 0))
            st = self._parse_time_str(str(item.get("start_time", "08:00")), time(8, 0))
            et = self._parse_time_str(str(item.get("end_time", "17:00")), time(17, 0))
            b_type = str(item.get("block_type", "work")).lower()
            if b_type not in ["work", "sleep", "fixed", "commute"]:
                b_type = "work"
            lbl = str(item.get("label", "Actividad fija"))

            block = ScheduleBlock(
                user_id=document.user_id,
                document_id=document.id,
                day_of_week=dow,
                start_time=st,
                end_time=et,
                block_type=b_type,
                label=lbl,
            )
            db.add(block)
            created_blocks.append(block)

        # Update or create sleep target
        wake_str = extraction.get("wake_time", "06:30:00")
        bed_str = extraction.get("bed_time", "23:00:00")
        wake_target = self._parse_time_str(wake_str, time(6, 30))
        bed_target = self._parse_time_str(bed_str, time(23, 0))

        # Check existing sleep target
        stmt = select(SleepTarget).where(SleepTarget.user_id == document.user_id)
        res = await db.execute(stmt)
        sleep_target = res.scalar_one_or_none()

        if sleep_target:
            sleep_target.bedtime_target = bed_target
            sleep_target.wakeup_target = wake_target
            sleep_target.target_hours = 7.5
        else:
            sleep_target = SleepTarget(
                user_id=document.user_id,
                target_hours=7.5,
                bedtime_target=bed_target,
                wakeup_target=wake_target,
            )
            db.add(sleep_target)

        document.status = "processed"
        document.processed_at = datetime.utcnow()
        await db.commit()
        return created_blocks
