"""
Configuration for VPS deployment with E2B sandboxes.
All parameters optimized for production environment.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class VPSConfig:
    """Configuration class for VPS deployment"""

    # ==================== API KEYS ====================
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    E2B_API_KEY: str = os.getenv("E2B_API_KEY", "")

    # ==================== E2B TIMEOUTS ====================
    # Maximum time for code execution inside sandbox
    CODE_EXECUTION_TIMEOUT: float = float(os.getenv("CODE_EXECUTION_TIMEOUT", "30.0"))

    # Maximum time for entire request to complete
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "60.0"))

    # Maximum time to wait for sandbox creation
    SANDBOX_CREATION_TIMEOUT: float = float(os.getenv("SANDBOX_CREATION_TIMEOUT", "120.0"))

    # ==================== RESOURCE LIMITS ====================
    # Maximum number of sandboxes running at the same time
    # CRITICAL: Each sandbox = API call + cost
    MAX_CONCURRENT_SANDBOXES: int = int(os.getenv("MAX_CONCURRENT_SANDBOXES", "2"))

    # Maximum sandboxes created per hour (cost protection)
    MAX_SANDBOXES_PER_HOUR: int = int(os.getenv("MAX_SANDBOXES_PER_HOUR", "20"))

    # Maximum agent iterations (prevent infinite loops)
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))

    # Maximum RPM for CrewAI agents
    MAX_RPM: int = int(os.getenv("MAX_RPM", "10"))

    # ==================== RETRY POLICY ====================
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "2"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "5.0"))

    # ==================== MONITORING ====================
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_FILE: str = os.getenv("METRICS_FILE", "/var/log/crewai/metrics.json")

    # Health check interval in seconds
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "300"))

    # ==================== LOGGING ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "/var/log/crewai/app.log")

    # ==================== CODE LIMITS ====================
    # Maximum code length to prevent abuse
    MAX_CODE_LENGTH: int = int(os.getenv("MAX_CODE_LENGTH", "10000"))

    # Maximum output length to store
    MAX_OUTPUT_LENGTH: int = int(os.getenv("MAX_OUTPUT_LENGTH", "5000"))

    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """Validate configuration before starting"""
        if not cls.ANTHROPIC_API_KEY:
            return False, "ANTHROPIC_API_KEY is required"

        if not cls.E2B_API_KEY:
            return False, "E2B_API_KEY is required"

        if cls.MAX_CONCURRENT_SANDBOXES < 1:
            return False, "MAX_CONCURRENT_SANDBOXES must be >= 1"

        if cls.MAX_SANDBOXES_PER_HOUR < cls.MAX_CONCURRENT_SANDBOXES:
            return False, "MAX_SANDBOXES_PER_HOUR must be >= MAX_CONCURRENT_SANDBOXES"

        if cls.CODE_EXECUTION_TIMEOUT > cls.REQUEST_TIMEOUT:
            return False, "CODE_EXECUTION_TIMEOUT must be <= REQUEST_TIMEOUT"

        return True, None

    @classmethod
    def get_info(cls) -> dict:
        """Get configuration info (without sensitive data)"""
        return {
            "max_concurrent_sandboxes": cls.MAX_CONCURRENT_SANDBOXES,
            "max_sandboxes_per_hour": cls.MAX_SANDBOXES_PER_HOUR,
            "code_execution_timeout": cls.CODE_EXECUTION_TIMEOUT,
            "request_timeout": cls.REQUEST_TIMEOUT,
            "max_iterations": cls.MAX_ITERATIONS,
            "max_rpm": cls.MAX_RPM,
            "enable_metrics": cls.ENABLE_METRICS,
            "log_level": cls.LOG_LEVEL
        }
