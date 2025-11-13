"""Component script for green_space_monitoring ops."""

import multiprocessing

from pc_ops.logger import logger
from pc_ops.ops_pc import main

if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn", force=True)
        main()
    except Exception as ex:
        logger.exception(f"{ex}")
        raise
