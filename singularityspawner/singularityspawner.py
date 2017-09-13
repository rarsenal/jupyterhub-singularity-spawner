# Copyright (c) 2017, Zebula Sampedro, CU Boulder Research Computing

"""
Singularity Spawner

SingularitySpawner provides a mechanism for spawning Jupyter Notebooks inside of Singularity containers. The spawner options form is leveraged such that the user can specify which Singularity image the spawner should use.

A `singularity exec {notebook spawn cmd}` is used to start the notebook inside of the container.
"""
import os
import pipes

from tornado import gen
from tornado.process import Subprocess
from tornado.iostream import StreamClosedError

from jupyterhub.spawner import (
    LocalProcessSpawner, set_user_setuid
)
from jupyterhub.utils import random_port
from traitlets import (
    Integer, Unicode, Float, Dict, Command, default
)

class SingularitySpawner(LocalProcessSpawner):
    """SingularitySpawner - extends the default LocalProcessSpawner to allow for:
    1) User-specification of a singularity image via the Spawner options form
    2) Spawning a Notebook server within a Singularity container
    """

    singularity_cmd = Command(['singularity','exec'],
        help="""
        This is the singularity command that will be executed when starting the
        singule-user server. The image path and notebook server args will be concatenated to the end of this command. This is a good place to
        specify any site-specific options that should be applied to all users,
        such as default mounts.
        """
    )

    default_image_path = Unicode('',
        help="""
        Absolute POSIX filepath to Singularity image that will be used to
        execute the notebook server spawn command, if another path is not
        specified by the user.
        """
    ).tag(config=True)

    def _build_cmd(self):
        cmd = []
        cmd.extend(self.singularity_cmd)
        cmd.append(default_image_path)
        cmd.extend(self.cmd)
        self.cmd = cmd

    @gen.coroutine
    def start(self):
        """
        Start the single-user server, after building the new singularity
        for this instance.
        """
        self.cmd = self._build_cmd()
        super(SingularitySpawner,self).start()
