"""Functions to generate locust code.

This module contains functions to generate locust code, *i.e.* it
defines tasks, tasksets and locusts.

"""

from pathlib import Path
from typing import List, Tuple

from . import __version__ as wtgseal_version
from . import dist_name as wtgseal_dist_name
from . import dist_url as wtgseal_dist_url

# from .utils import count_requests, parse_objects

CmdDef = Tuple[int, str]
BlockDef = List[CmdDef]


def cmddef_to_str(cmddef: CmdDef, indentby: str = ' ' * 4) -> str:
    """Convert a command definition into a string."""
    level, cmd = cmddef
    return indentby * level + cmd + '\n'


def setup_blank_line(n: int = 1, /) -> BlockDef:  # noqa
    """Generate representation for a given number of blank lines."""
    if type(n) != int:
        raise TypeError("n must be an integer")
    else:
        blank = [(0, '')] * n
        return blank


def setup_header(*, dist: str = wtgseal_dist_name,
                 version: str = wtgseal_version,
                 url: str = wtgseal_dist_url) -> BlockDef:
    """Generate a simple header with dist, version and url information.

    Generate a program header citing the distribution name from where
    it was generated, the current version and the url where one can find
    further information.
    """
    header = []
    header.append((0,
                   f'# locust file generated by {dist} (release {version})'))
    header.append((0, f'# See {url} for more information'))
    return header


def setup_import() -> BlockDef:
    """Generate the import lines for a locust file.

    Generate code to import the modules needed for running a locust file

    Returns
    -------
    BlockDef
        A list of code representation, where each item represents a line
        of import.
    """
    imports = []
    imports.append((0, 'from locust import HttpLocust, TaskSet, task'))
    imports.append((0, 'from scipy.stats import pareto'))
    return imports


def setup_task(name: str = 'task0',
               weight: int = 1,
               uri: List[str] = ["/", ],
               indlevel: int = 0) -> BlockDef:
    """Generate code to define a locust task.

    Generate code to definie a locust task according to the given
    parameters.

    Parameters
    ----------
    uri : {List[str] = ["/", ]}
        A list of URIs, each starting with a backslash
        like "/index.html"
    name : {str}, optional
        The name for the task to be generated (the default is 'task0')
    weight : {int}, optional
        The weight for the generated task (the default is 1)
    indlevel : {int}, optional
        The indentation level where the task definition should begin
        (the default is 0, which leads to code beginning at the left
        margin)

    Returns
    -------
    List[Tuple[int, str]]
        A list where each item represents a line of code to be
        generated. Each Tuple[int, str] consists of the indentation
        level for the code and the code itself. `None` is returned in
        case `uri` is not an iterable.

    """
    if isinstance(uri, list):
        task = []
        task.append((indlevel, f'@task({weight})'))
        task.append((indlevel, f'def {name}(self):'))
        for req in uri:
            task.append((indlevel + 1, f'self.client.get("{req}")'))
        return task
    else:
        raise TypeError('Parameter uri should be a list')


def setup_taskset(name: str = 'MyTaskSet') -> BlockDef:
    """Generate representation of TaskSet subclass definition."""
    return [(0, f'class {name}(TaskSet):')]


def setup_locust(name: str = 'MyLocust',
                 taskset: str = 'MyTaskSet',
                 weight: int = 1,
                 indlevel: int = 0) -> BlockDef:
    """Generate a locust (user behaviour) representation.

    Generate a representation for a Locust subclass, which represents an
    user behaviour. The representation contains the class name, taskset,
    and a wait time based on a Pareto distribution.

    Parameters
    ----------
    name : {str}, optional
        The new class name (the default is 'MyLocust')
    taskset : {str}, optional
        The taskset name this class will use (the default is
        'MyTaskSet')
    weight : {int}, optional
        The weight for this class. The greater this value, the greater
        the chances this class will be spawned. Only important in case
        you have more than one Locust subclass and with they be spawned
        at different rates.
    indlevel : {int}, optional
        The indentation level where the task definition should begin
        (the default is 0, which leads to code beginning at the left
        margin)

    Returns
    -------
    List[Tuple[int, str]]
        A list where each item represents a line of code to be
        generated. Each Tuple[int, str] consists of the indentation
        level for the code and the code itself.

    Notes
    -----
    An OFF time is defined in this class by the `wait_time` attribute.
    This attribute defines how long a locust will wait after each task.
    Here, we define it as a pareto distribution with shape 1.4 and
    scale 1.0, based on SURGE implementation [1]_.

    References
    ----------
    .. [1] Barford, P., & Crovella, M. (1998, June). Generating
       representative web workloads for network and server performance
       evaluation. In *Proceedings of the 1998 ACM SIGMETRICS joint
       international conference on Measurement and modeling of computer
       systems* (pp. 151-160).

    See Also
    --------
    locust.Locust
    """
    locust = [(indlevel, f'class {name}(HttpLocust):'),
              (indlevel + 1, f'weight = {weight}'),
              (indlevel + 1, f'task_set = {taskset}'),
              (indlevel + 1, 'pareto_obj = pareto(b=1.4, scale=1)'),
              (indlevel + 1, 'pareto_obj.random_state = 1')]
    locust.extend(setup_blank_line())
    locust.extend([(indlevel + 1, 'def wait_time(self):'),
                   (indlevel + 2, 'return self.pareto_obj.rvs()')])
    return locust


def write_locust(path: Path, filedef: BlockDef, indentby: str = ' ' * 4) -> None:
    if not isinstance(path, Path):
        raise TypeError('Expected a pathlib.Path object')
    if not isinstance(filedef, list):
        raise TypeError('Expected a list of tuples')
    else:
        with path.open(mode='w') as fd:
            for cmddef in filedef:
                fd.write(cmddef_to_str(cmddef, indentby))
