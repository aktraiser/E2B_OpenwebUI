"""
Main entry point for VPS deployment.
"""
import logging
import sys
from crew import CodeExecutionCrewVPS
from sandbox_pool import get_sandbox_pool
from config import VPSConfig

# Configure logging
logging.basicConfig(
    level=VPSConfig.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(VPSConfig.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    # Validate configuration
    is_valid, error = VPSConfig.validate()
    if not is_valid:
        logger.error(f"Configuration error: {error}")
        sys.exit(1)

    pool = get_sandbox_pool()
    logger.info(f"Starting execution. Config: {VPSConfig.get_info()}")
    logger.info(f"Initial metrics: {pool.get_metrics()}")

    try:
        # Create and run crew
        crew_instance = CodeExecutionCrewVPS()
        result = crew_instance.crew().kickoff()

        # Display results
        print("\n" + "="*60)
        print("RESULT")
        print("="*60)
        print(result)

        print("\n" + "="*60)
        print("METRICS")
        print("="*60)
        for key, value in pool.get_metrics().items():
            print(f"{key}: {value}")

        logger.info("Execution completed successfully")

    except Exception as e:
        logger.exception("Execution failed")
        print(f"\nERROR: {e}")
        print(f"Metrics: {pool.get_metrics()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
