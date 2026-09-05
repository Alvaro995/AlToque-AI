"""Servicio de cálculo y conciliación de ventanas metabólicas circadianas (F-03)."""

from datetime import datetime, time, timedelta, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.scheduling import MetabolicWindow, SleepTarget
from app.models.ingestion import ScheduleBlock


class MetabolicWindowService:
    """Reconciles circadian rhythm targets with inflexible daily calendar constraints."""

    @staticmethod
    def _time_to_minutes(t: time) -> int:
        return t.hour * 60 + t.minute

    @staticmethod
    def _minutes_to_time(m: int) -> time:
        m = m % 1440
        return time(hour=m // 60, minute=m % 60)

    async def calculate_and_reconcile_windows(
        self,
        db: AsyncSession,
        user_id: str,
        target_eating_duration_hours: float = 11.0,
    ) -> List[MetabolicWindow]:
        """
        Derive daily metabolic windows (breakfast, lunch, dinner, micro_exercise)
        for all days of the week respecting work blocks and 3-hour pre-bed fasting.
        """
        # Retrieve user sleep target
        sleep_res = await db.execute(select(SleepTarget).where(SleepTarget.user_id == user_id))
        sleep_target = sleep_res.scalar_one_or_none()

        wake_time = sleep_target.wakeup_target if sleep_target else time(7, 0)
        bed_time = sleep_target.bedtime_target if sleep_target else time(23, 0)

        wake_min = self._time_to_minutes(wake_time)
        bed_min = self._time_to_minutes(bed_time)

        # Retrieve user schedule blocks
        blocks_res = await db.execute(
            select(ScheduleBlock).where(ScheduleBlock.user_id == user_id)
        )
        schedule_blocks = list(blocks_res.scalars().all())

        # Clear previous generated windows
        await db.execute(delete(MetabolicWindow).where(MetabolicWindow.user_id == user_id))

        generated_windows: List[MetabolicWindow] = []

        for day_of_week in range(7):
            day_blocks = [b for b in schedule_blocks if b.day_of_week == day_of_week]

            # 1. Breakfast window: 45 to 90 minutes post-wake
            b_start = (wake_min + 45) % 1440
            b_end = (wake_min + 120) % 1440

            # 2. Dinner window: must finish at least 180 minutes (3h) prior to bedtime
            d_end = (bed_min - 180) % 1440
            d_start = (d_end - 60) % 1440

            # 3. Lunch window: midway between breakfast and dinner, checking work blocks
            mid_min = (b_end + d_start) // 2
            l_start = mid_min - 45
            l_end = mid_min + 45

            # Adjust lunch if overlapping with work block without break
            for block in day_blocks:
                block_s = self._time_to_minutes(block.start_time)
                block_e = self._time_to_minutes(block.end_time)
                if block.block_type == "work" and block_s <= l_start and block_e >= l_end:
                    # Place lunch at typical midpoint of work shift if long
                    shift_mid = (block_s + block_e) // 2
                    l_start = shift_mid - 30
                    l_end = shift_mid + 30

            # Window definitions
            window_definitions = [
                ("breakfast", b_start, b_end),
                ("lunch", l_start, l_end),
                ("dinner", d_start, d_end),
                ("micro_exercise", (l_end + 30) % 1440, (l_end + 60) % 1440),
            ]

            for w_type, start_m, end_m in window_definitions:
                window_entity = MetabolicWindow(
                    user_id=user_id,
                    window_type=w_type,
                    optimal_start=self._minutes_to_time(start_m),
                    optimal_end=self._minutes_to_time(end_m),
                    day_of_week=day_of_week,
                )
                db.add(window_entity)
                generated_windows.append(window_entity)

        await db.commit()
        return generated_windows
