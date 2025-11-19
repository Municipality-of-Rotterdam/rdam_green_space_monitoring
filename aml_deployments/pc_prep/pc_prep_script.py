"""Component script for green_space_monitoring preprocessing.."""

import multiprocessing

from pc_prep.logger import logger
from pc_prep.tree_prep.prep_pc import main

if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn", force=True)
        main()
    except Exception as ex:
        logger.exception(f"{ex}")
        raise
