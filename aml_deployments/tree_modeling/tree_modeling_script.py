"""Component script for green_space_monitoring tree modeling.."""

import multiprocessing

from tree_modeling.logger import logger
from tree_modeling.modeling_tree import main

if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn", force=True)
        main()
    except Exception as ex:
        logger.exception(f"{ex}")
        raise
