"""
System-level calls to external tools, directory creation, etc.

Authors:
  Thomas A. Hopf
"""


import os
import tempfile
import subprocess
import requests


class ResourceError(IOError):
    """
    Exception for missing resources (files, URLs, ...)
    """


def run(cmd, stdin=None, working_dir=None, shell=False):
    """
    Run external program as subprocess.

    Parameters
    ----------
    cmd : str or list of str
        Command (and  optional command line arguments)
    stdin : str or byte sequence, optional (default: None)
        Input to be sent to STDIN of the process
    working_dir : str, optional (default: None)
        Change to this directory before running command
    binary_stream : bool, optional (default: False)
        Treat STDIN/STDOUT/STDERR as binary streams or not
    shell : bool, optional
        Invoke shell when calling subprocess (default: False)

    Returns
    -------
    int
        Return code of process
    stdout
        Byte string with stdout output
    stderr
        Byte string of stderr output
    """
    with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE, universal_newlines=True,
            cwd=working_dir, shell=shell
    ) as proc:
        (stdout, stderr) = proc.communicate(stdin)
        return_code = proc.returncode

        return return_code, stdout, stderr


def makedirs(directories):
    """
    Create directory subtree, some or all of the folders
    may already exist.

    Parameters
    ----------
    directories : str
        Directory subtree to create
    """
    os.makedirs(directories, exist_ok=True)


def temp():
    """
    Create a temporary file

    Returns
    -------
    str
        Path of temporary file
    """
    handle, name = tempfile.mkstemp()
    return name


def tempdir():
    """
    Create a temporary directory

    Returns
    -------
    str
        Path of temporary directory
    """
    return tempfile.mkdtemp()


def write_file(file_path, content):
    """
    Writes content to output file

    Parameters
    ----------
    file_path : str
        Path of output file
    content : str
        Content to be written to file
    """
    with open(file_path, "w") as f:
        f.write(content)


def get(url, output_path=None, allow_redirects=False):
    """
    Download external resource

    Parameters
    ----------
    url : str
        URL of resource that should be downloaded
    output_path: str, optional
        Save contents of URL to this file
    allow_redirects: bool
        Allow redirects by server or not

    Returns
    -------
    str
        Contents of resouce at URL

    Raises
    ------
    ResourceError

    """
    try:
        r = requests.get(url, allow_redirects=allow_redirects)

        if r.status_code != requests.codes.ok:
            raise ResourceError(
                "Invalid status code ({}) for URL: {}".format(
                    r.status_code, url
                )
            )

        if output_path is not None:
            try:
                write_file(output_path, r.content)
            except IOError as e:
                raise ResourceError(
                    "Could not save to file: {}".format(output_path)
                ) from e

        return r.content

    except requests.exceptions.RequestException as e:
        raise ResourceError() from e