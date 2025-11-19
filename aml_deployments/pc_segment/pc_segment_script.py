"""Component script for green_space_monitoring segment.."""

from pc_segment.logger import logger
from pc_segment.segment_pc import main

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logger.exception(f"{ex}")
        raise
