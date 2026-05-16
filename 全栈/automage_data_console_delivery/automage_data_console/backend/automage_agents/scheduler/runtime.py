from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

from automage_agents.config import RuntimeSettings, load_runtime_settings
from automage_agents.db import create_session_factory
from automage_agents.scheduler.jobs import (
    SchedulerJob,
    build_manager_summary_auto_generate_job,
    build_manager_summary_reminder_job,
    build_staff_daily_reminder_job,
    health_check_job,
)
from automage_agents.scheduler.orchestrator import orchestrator_tick


logger = logging.getLogger("automage.scheduler")


@dataclass(slots=True)
class SchedulerRuntime:
    settings: RuntimeSettings
    jobs: list[SchedulerJob]
    _threads: list[threading.Thread]
    _stop_event: threading.Event

    def start(self) -> None:
        if not self.settings.scheduler_enabled:
            logger.info("scheduler_enabled=false, skip starting scheduler runtime")
            return
        for job in self.jobs:
            if not job.enabled:
                continue
            thread = threading.Thread(target=self._run_job_loop, args=(job,), daemon=True, name=f"scheduler-{job.name}")
            thread.start()
            self._threads.append(thread)
            logger.info("scheduler_job_started name=%s interval_seconds=%s", job.name, job.interval_seconds)

    def stop(self) -> None:
        self._stop_event.set()
        for thread in self._threads:
            thread.join(timeout=1)
        self._threads.clear()

    def run_forever(self) -> None:
        self.start()
        if not self.settings.scheduler_enabled:
            return
        try:
            while not self._stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("scheduler received keyboard interrupt, stopping")
            self.stop()

    def _run_job_loop(self, job: SchedulerJob) -> None:
        while not self._stop_event.is_set():
            try:
                job.handler()
            except Exception as exc:
                logger.exception("scheduler_job_failed name=%s error=%s", job.name, exc)
            if self._stop_event.wait(job.interval_seconds):
                return


def build_scheduler_runtime(settings: RuntimeSettings | None = None) -> SchedulerRuntime:
    runtime_settings = settings or load_runtime_settings("configs/automage.local.toml")
    session_factory = create_session_factory(runtime_settings.postgres)
    jobs = []
    handler_map = {
        "health_check_job": health_check_job,
        "staff_daily_reminder_job": build_staff_daily_reminder_job(
            session_factory,
            limit=runtime_settings.scheduler_task_record_limit,
        ),
        "manager_summary_reminder_job": build_manager_summary_reminder_job(
            session_factory,
            limit=runtime_settings.scheduler_task_record_limit,
        ),
        "manager_summary_auto_generate_job": build_manager_summary_auto_generate_job(
            session_factory,
            limit=runtime_settings.scheduler_task_record_limit,
        ),
    }
    # 编排器始终添加，不依赖配置
    jobs.append(
        SchedulerJob(
            name="orchestrator_tick",
            interval_seconds=300,
            enabled=True,
            handler=lambda: orchestrator_tick("configs/automage.docker.toml"),
        )
    )
    for item in runtime_settings.scheduler_jobs:
        name = str(item.get("name") or "").strip()
        handler = handler_map.get(name)
        if handler is None:
            logger.warning("skip unknown scheduler job: %s", name)
            continue
        jobs.append(
            SchedulerJob(
                name=name,
                interval_seconds=max(1, int(item.get("interval_seconds", 300))),
                enabled=bool(item.get("enabled", True)),
                handler=handler,
            )
        )
    return SchedulerRuntime(
        settings=runtime_settings,
        jobs=jobs,
        _threads=[],
        _stop_event=threading.Event(),
    )
