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
from jupyterhub.traitlets import Command
from traitlets import (
    Integer, Unicode, Float, Dict, default
)

class SingularitySpawner(LocalProcessSpawner):
    """SingularitySpawner - extends the default LocalProcessSpawner to allow for:
    1) User-specification of a singularity image via the Spawner options form
    2) Spawning a Notebook server within a Singularity container
    """

    singularity_cmd = Command(['/usr/local/bin/singularity','exec'],
        help="""
        This is the singularity command that will be executed when starting the
        singule-user server. The image path and notebook server args will be concatenated to the end of this command. This is a good place to
        specify any site-specific options that should be applied to all users,
        such as default mounts.
        """
    ).tag(config=True)

    default_image_path = Command([''],
        help="""
        Absolute POSIX filepath to Singularity image that will be used to
        execute the notebook server spawn command, if another path is not
        specified by the user.
        """
    ).tag(config=True)

    options_form = Unicode()

    form_template = Unicode(
        """<label for="user_image_path">
            Specify the Singularity image to use (absolute filepath):
        </label>
        <input class="form-control" name="user_image_path" value={default_image_path} required autofocus>
        """
    )

    def _options_form_default(self):
        format_options = dict(default_image_path=self.default_image_path[0])
        options_form = self.form_template.format(**format_options)
        return options_form

    def options_from_form(self, form_data):
        return dict(user_image_path=form_data.get('user_image_path',None))

    def _build_cmd(self):
        image_path = self.user_options.get('user_image_path',self.default_image_path)
        cmd = []
        cmd.extend(self.singularity_cmd)
        cmd.extend(image_path)
        cmd.extend(self.cmd)
        return cmd

    @gen.coroutine
    def start(self):
        """
        Start the single-user server, after building the new singularity
        for this instance.
        """
        self.cmd = self._build_cmd()
        super(SingularitySpawner,self).start()
