"""
Sandbox pool manager for E2B on VPS.
Handles resource limits, rate limiting, and cost protection.
"""
import asyncio
import time
import logging
import json
from typing import Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from e2b_code_interpreter import Sandbox
from config import VPSConfig

logger = logging.getLogger(__name__)


@dataclass
class SandboxMetrics:
    """Metrics tracking for E2B sandbox usage"""

    # Total counters
    total_created: int = 0
    total_failed: int = 0
    total_executions: int = 0
    total_timeouts: int = 0

    # Hourly tracking (for rate limiting)
    hourly_count: int = 0
    hourly_reset_time: datetime = field(default_factory=datetime.now)

    # Active tracking
    active_sandboxes: int = 0
    peak_concurrent: int = 0

    # Timing
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0

    def record_creation(self):
        """Record a successful sandbox creation"""
        self.total_created += 1
        self.active_sandboxes += 1

        if self.active_sandboxes > self.peak_concurrent:
            self.peak_concurrent = self.active_sandboxes

        self._check_hourly_reset()
        self.hourly_count += 1

        logger.info(
            f"Sandbox created. Active: {self.active_sandboxes}, "
            f"Hourly: {self.hourly_count}/{VPSConfig.MAX_SANDBOXES_PER_HOUR}"
        )

    def record_closure(self):
        """Record a sandbox closure"""
        self.active_sandboxes = max(0, self.active_sandboxes - 1)
        logger.info(f"Sandbox closed. Active: {self.active_sandboxes}")

    def record_failure(self):
        """Record a sandbox creation/execution failure"""
        self.total_failed += 1
        logger.warning(f"Sandbox failure recorded. Total failures: {self.total_failed}")

    def record_timeout(self):
        """Record a timeout event"""
        self.total_timeouts += 1
        logger.warning(f"Timeout recorded. Total timeouts: {self.total_timeouts}")

    def record_execution(self, execution_time: float):
        """Record a successful execution"""
        self.total_executions += 1
        self.total_execution_time += execution_time

        # Update average
        self.avg_execution_time = (
            self.total_execution_time / self.total_executions
            if self.total_executions > 0
            else 0.0
        )

        logger.info(
            f"Execution recorded. Time: {execution_time:.2f}s, "
            f"Avg: {self.avg_execution_time:.2f}s"
        )

    def _check_hourly_reset(self):
        """Reset hourly counter if hour has passed"""
        now = datetime.now()
        if now - self.hourly_reset_time > timedelta(hours=1):
            logger.info(
                f"Hourly reset. Previous count: {self.hourly_count}, "
                f"Time: {self.hourly_reset_time}"
            )
            self.hourly_count = 0
            self.hourly_reset_time = now

    def can_create_sandbox(self) -> tuple[bool, str]:
        """
        Check if a new sandbox can be created based on limits.

        Returns:
            (can_create, reason)
        """
        self._check_hourly_reset()

        # Check concurrent limit
        if self.active_sandboxes >= VPSConfig.MAX_CONCURRENT_SANDBOXES:
            return (
                False,
                f"Max concurrent sandboxes reached "
                f"({VPSConfig.MAX_CONCURRENT_SANDBOXES}). "
                f"Currently active: {self.active_sandboxes}"
            )

        # Check hourly limit
        if self.hourly_count >= VPSConfig.MAX_SANDBOXES_PER_HOUR:
            time_until_reset = (
                self.hourly_reset_time + timedelta(hours=1) - datetime.now()
            )
            minutes_left = int(time_until_reset.total_seconds() / 60)
            return (
                False,
                f"Hourly limit reached ({VPSConfig.MAX_SANDBOXES_PER_HOUR}/hour). "
                f"Reset in {minutes_left} minutes. Current: {self.hourly_count}"
            )

        return True, "OK"

    def to_dict(self) -> dict:
        """Convert metrics to dictionary"""
        data = asdict(self)
        # Convert datetime to ISO string
        data["hourly_reset_time"] = self.hourly_reset_time.isoformat()
        return data

    def save_to_file(self):
        """Save metrics to file for persistence"""
        if not VPSConfig.ENABLE_METRICS:
            return

        try:
            # Try to create directory if needed
            import os
            metrics_dir = os.path.dirname(VPSConfig.METRICS_FILE)
            if metrics_dir and not os.path.exists(metrics_dir):
                os.makedirs(metrics_dir, exist_ok=True)
            
            with open(VPSConfig.METRICS_FILE, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            logger.debug(f"Could not save metrics to file: {e}")

    @classmethod
    def load_from_file(cls) -> "SandboxMetrics":
        """Load metrics from file"""
        if not VPSConfig.ENABLE_METRICS:
            return cls()

        try:
            with open(VPSConfig.METRICS_FILE, "r") as f:
                data = json.load(f)
                # Convert ISO string back to datetime
                data["hourly_reset_time"] = datetime.fromisoformat(
                    data["hourly_reset_time"]
                )
                return cls(**data)
        except FileNotFoundError:
            logger.debug("No existing metrics file, starting fresh")
            return cls()
        except Exception as e:
            logger.debug(f"Could not load metrics: {e}, starting fresh")
            return cls()


class SandboxPool:
    """
    Manages E2B sandbox lifecycle with resource limits and monitoring.

    This pool ensures:
    - Maximum concurrent sandboxes limit
    - Hourly creation rate limit
    - Proper cleanup and error handling
    - Metrics tracking for monitoring
    """

    def __init__(self):
        self.metrics = SandboxMetrics.load_from_file()
        self._semaphore = asyncio.Semaphore(VPSConfig.MAX_CONCURRENT_SANDBOXES)
        self._lock = asyncio.Lock()

        logger.info(f"SandboxPool initialized with config: {VPSConfig.get_info()}")
        logger.info(f"Loaded metrics: {self.metrics.to_dict()}")

    @asynccontextmanager
    async def acquire_sandbox(self):
        """
        Acquire a sandbox with resource protection.

        Usage:
            async with pool.acquire_sandbox() as sandbox:
                result = await sandbox.run_code(...)

        Raises:
            RuntimeError: If sandbox cannot be created due to limits
        """
        sandbox = None

        # Check limits before acquiring semaphore
        async with self._lock:
            can_create, reason = self.metrics.can_create_sandbox()
            if not can_create:
                logger.warning(f"Sandbox creation blocked: {reason}")
                raise RuntimeError(f"Cannot create sandbox: {reason}")

        # Acquire semaphore for concurrent limit
        async with self._semaphore:
            try:
                logger.info("Attempting to create E2B sandbox...")
                start_time = time.time()

                # Create sandbox with timeout
                sandbox = await asyncio.wait_for(
                    asyncio.to_thread(Sandbox.create),
                    timeout=VPSConfig.SANDBOX_CREATION_TIMEOUT
                )

                creation_time = time.time() - start_time
                logger.info(f"Sandbox created in {creation_time:.2f}s")

                async with self._lock:
                    self.metrics.record_creation()
                    self.metrics.save_to_file()

                yield sandbox

            except asyncio.TimeoutError:
                logger.error(
                    f"Sandbox creation timeout after "
                    f"{VPSConfig.SANDBOX_CREATION_TIMEOUT}s"
                )
                async with self._lock:
                    self.metrics.record_timeout()
                    self.metrics.record_failure()
                    self.metrics.save_to_file()
                raise RuntimeError(
                    f"Sandbox creation timeout after "
                    f"{VPSConfig.SANDBOX_CREATION_TIMEOUT}s"
                )

            except Exception as e:
                logger.error(f"Sandbox creation failed: {e}", exc_info=True)
                async with self._lock:
                    self.metrics.record_failure()
                    self.metrics.save_to_file()
                raise RuntimeError(f"Sandbox creation failed: {e}")

            finally:
                # Always cleanup sandbox
                if sandbox:
                    try:
                        await asyncio.to_thread(sandbox.close)
                        logger.info("Sandbox closed successfully")
                    except Exception as e:
                        logger.error(f"Error closing sandbox: {e}", exc_info=True)
                    finally:
                        async with self._lock:
                            self.metrics.record_closure()
                            self.metrics.save_to_file()

    def get_metrics(self) -> dict:
        """Get current metrics as dictionary"""
        return {
            **self.metrics.to_dict(),
            "config": VPSConfig.get_info()
        }

    def get_health_status(self) -> dict:
        """
        Get health status for monitoring.

        Returns:
            Dictionary with status and details
        """
        can_create, reason = self.metrics.can_create_sandbox()

        # Determine health status
        if not can_create:
            status = "degraded"
        elif self.metrics.total_failed > self.metrics.total_created * 0.1:
            status = "warning"  # >10% failure rate
        else:
            status = "healthy"

        return {
            "status": status,
            "can_create_sandbox": can_create,
            "reason": reason if not can_create else "OK",
            "active_sandboxes": self.metrics.active_sandboxes,
            "hourly_usage": f"{self.metrics.hourly_count}/{VPSConfig.MAX_SANDBOXES_PER_HOUR}",
            "failure_rate": (
                f"{(self.metrics.total_failed / max(1, self.metrics.total_created)) * 100:.1f}%"
            ),
            "avg_execution_time": f"{self.metrics.avg_execution_time:.2f}s"
        }


# Global singleton instance
_sandbox_pool: Optional[SandboxPool] = None


def get_sandbox_pool() -> SandboxPool:
    """Get or create the global sandbox pool"""
    global _sandbox_pool
    if _sandbox_pool is None:
        _sandbox_pool = SandboxPool()
    return _sandbox_pool


def reset_sandbox_pool():
    """Reset the global pool (mainly for testing)"""
    global _sandbox_pool
    _sandbox_pool = None
