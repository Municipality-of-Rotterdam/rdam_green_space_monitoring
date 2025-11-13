"""Script for distributed computing of pc_ops script.

It does the following:
- Determines rank/world_size from env vars (OMPI/PMI or fallback to 0/1).
- Loads metadata, shards the pc_paths by rank.
- Reuses existing process_point_cloud() for each item in the shard.
- Keeps per-node multiprocessing (args.num_workers) for in-node parallelism.
- Writes a per-rank partial JSON: <dirname(ops_metadata)>/_partials/ops_metadata.rank{rank}.json
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import sys
from typing import Dict, List, Tuple, Union

from pc_ops.helper_functions import load_processed_files
from pc_ops.logger import logger
from pc_ops.ops_pc import configure_arg_parser, process_point_cloud_wrapper
from tqdm import tqdm


def _get_rank_and_world() -> Tuple[int, int]:
    """Derive rank/world_size from common launcher env vars (OMPI/PMI), with sane fallbacks."""
    rank = os.environ.get("OMPI_COMM_WORLD_RANK")
    size = os.environ.get("OMPI_COMM_WORLD_SIZE")
    if rank is None or size is None:
        rank = os.environ.get("PMI_RANK", "0")
        size = os.environ.get("PMI_SIZE", "1")
    try:
        r = int(rank)
    except Exception:
        r = 0
    try:
        w = int(size)
    except Exception:
        w = 1
    r = max(0, r)
    w = max(1, w)
    return r, w


def _choose_num_workers(requested: int | None) -> int:
    """Choose per-node worker count (local multiprocessing)."""
    cpu = multiprocessing.cpu_count()
    if requested is None:
        return max(1, cpu - 1)
    if 0 < requested <= max(1, cpu - 1):
        return requested
    logger.error("Invalid num_workers=%s. Defaulting to cpu_count - 1.", requested)
    return max(1, cpu - 1)


def main() -> None:
    """Main script."""
    # pre-parse our extra arg and remove it from argv so ops_pc's parser won't choke
    _pre = argparse.ArgumentParser(add_help=False)
    _pre.add_argument("--partials_dir", required=True)
    _pre_args, _remaining = _pre.parse_known_args()
    sys.argv = [sys.argv[0], *_remaining]  # drop --partials_dir from argv

    # now parse the existing args as usual
    args = configure_arg_parser()

    # attach our extra value to the parsed namespace
    args.partials_dir = _pre_args.partials_dir

    # MPI/PMI rank & world size from env
    rank, world = _get_rank_and_world()
    logger.info(
        "Distributed wrapper: rank %s / %s on host %s", rank, world, os.uname().nodename
    )

    # Avoid accidental double-forks if the launcher also starts >1 process per node:
    multiprocessing.set_start_method("spawn", force=True)

    # Load preprocessed metadata (same as point_cloud_operations)
    logger.info("Loading processed files.")
    segment_metadata, img_metadata, pc_metadata = load_processed_files(args)

    # Build the list of work items (keys are pc_paths in segment_metadata)
    pc_paths: List[str] = list(segment_metadata.keys())

    # Shard deterministically by rank
    shard: List[str] = [p for i, p in enumerate(pc_paths) if (i % world) == rank]
    logger.info(
        "Sharding: rank %s owns %s items out of %s total.",
        rank,
        len(shard),
        len(pc_paths),
    )

    if not shard:
        logger.warning("Rank %s has no items. Exiting early.", rank)
        _write_partial({}, args.partials_dir, rank)
        return

    # Respect in-node parallelism (existing per-item code is CPU-bound)
    num_workers = _choose_num_workers(getattr(args, "num_workers", None))
    logger.info("Processing shard with %s local workers.", num_workers)

    # Prepare process args for existing wrapper
    process_args = [
        (pc_path, segment_metadata, img_metadata, pc_metadata, args)
        for pc_path in shard
    ]

    result_dict: Dict[str, Dict[str, Union[str, List[str]]]] = {}
    with multiprocessing.Pool(processes=num_workers) as pool:
        for result in tqdm(
            pool.imap_unordered(process_point_cloud_wrapper, process_args),
            total=len(process_args),
            desc=f"Rank {rank}: Processing Point Clouds",
        ):
            if result:
                result_dict.update(result)

    # Write per-rank partial (rank-0 will merge later)
    _write_partial(result_dict, args.partials_dir, rank)
    logger.info("Rank %s wrote %d entries.", rank, len(result_dict))


def _write_partial(
    result_dict: Dict[str, Dict[str, Union[str, List[str]]]],
    partial_dir: str,
    rank: int,
) -> None:
    """Write a per-rank partial JSON next to the final output path."""
    os.makedirs(partial_dir, exist_ok=True)
    partial_path = os.path.join(partial_dir, f"ops_metadata.rank{rank}.json")
    with open(partial_path, "w") as f:
        json.dump(result_dict, f, indent=4)
    logger.info("Wrote partial metadata to %s", partial_path)


if __name__ == "__main__":
    main()
