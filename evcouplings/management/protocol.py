import tarfile
import os

from evcouplings.utils import valid_file, write_config_file, FINAL_CONFIG_SUFFIX


def protocol_zip(**kwargs):

    prefix = kwargs["prefix"]
    incfg = kwargs

    outcfg = {
        **kwargs
    }

    # create results archive
    archive_file = prefix + ".tar.gz"
    create_archive(incfg, outcfg, archive_file)
    outcfg["archive_file"] = archive_file

    # delete selected output files if requested
    outcfg = delete_outputs(incfg, outcfg)

    # write final global state of pipeline
    write_config_file(
        prefix + FINAL_CONFIG_SUFFIX, outcfg
    )

    return outcfg


PROTOCOLS = {
    "zip": protocol_zip
}


def run(**kwargs):
    return PROTOCOLS.get(kwargs["protocol"], PROTOCOLS["zip"])(**kwargs)


def create_archive(config, outcfg, output_file):
    """
    Create archive of files generated by pipeline

    Parameters
    ----------
    config : dict-like
        Input configuration of job. Uses
        config["management"]["archive"] (list of key
        used to index outcfg) to determine
        which files should be added to archive
    outcfg : dict-like
        Output configuration of job
    output_file : str
        Store archive file to this path
    """
    # determine keys (corresponding to files) in
    # outcfg that should be stored
    outkeys = config.get("archive", None)

    # if no output keys are requested, nothing to do
    if outkeys is None or len(outkeys) == 0:
        return

    # create archive
    with tarfile.open(output_file, "w:gz") as tar:
        # add files based on keys one by one
        for k in outkeys:
            # skip missing keys or ones not defined
            if k not in outcfg or outcfg[k] is None:
                continue

            # distinguish between files and lists of files
            if k.endswith("files"):
                for f in outcfg[k]:
                    if valid_file(f):
                        tar.add(f)
            else:
                if valid_file(outcfg[k]):
                    tar.add(outcfg[k])


def delete_outputs(config, outcfg):
    """
    Remove pipeline outputs to save memory
    after running the job

    Parameters
    ----------
    config : dict-like
        Input configuration of job. Uses
        config["management"]["delete"] (list of key
        used to index outcfg) to determine
        which files should be added to archive
    outcfg : dict-like
        Output configuration of job

    Returns
    -------
    outcfg_cleaned : dict-like
        Output configuration with selected
        output keys removed.
    """
    # determine keys (corresponding to files) in
    # outcfg that should be stored
    outkeys = config.get("delete", None)

    # if no output keys are requested, nothing to do
    if outkeys is None:
        return outcfg

    # go through all flagged files and delete if existing
    for k in outkeys:
        # skip missing keys or ones not defined
        if k not in outcfg or k is None:
            continue

        # delete list of files
        if k.endswith("files"):
            for f in outcfg[k]:
                try:
                    os.remove(f)
                except OSError:
                    pass
            del outcfg[k]

        # delete individual file
        else:
            try:
                os.remove(outcfg[k])
                del outcfg[k]
            except OSError:
                pass

    return outcfg