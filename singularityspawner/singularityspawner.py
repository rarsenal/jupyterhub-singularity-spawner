# Copyright (c) 2017, Zebula Sampedro, CU Boulder Research Computing

"""
Singularity Spawner

SingularitySpawner provides a mechanism for spawning Jupyter Notebooks inside of Singularity containers. The spawner options form is leveraged such that the user can specify which Singularity image the spawner should use.

A `singularity exec {notebook spawn cmd}` is used to start the notebook inside of the container.
"""
import os, subprocess
import pipes

from subprocess import Popen

from tornado import gen
from tornado.process import Subprocess
from tornado.iostream import StreamClosedError
from singularity.cli import Singularity

from jupyterhub.spawner import (
    LocalProcessSpawner, set_user_setuid
)
from jupyterhub.utils import random_port
from jupyterhub.traitlets import Command
from traitlets import (
    Integer, Unicode, Float, Dict, List, Bool, default
)

class SingularitySpawner(LocalProcessSpawner):
    """SingularitySpawner - extends the default LocalProcessSpawner to allow for:
    1) User-specification of a singularity image via the Spawner options form
    2) Spawning a Notebook server within a Singularity container
    """

    singularity_cmd = Command(['/opt/singularity/3.3.0/bin/singularity','exec'],
        help="""
        This is the singularity command that will be executed when starting the
        single-user server. The image path and notebook server args will be concatenated to the end of this command. This is a good place to
        specify any site-specific options that should be applied to all users,
        such as default mounts.
        """
    ).tag(config=True)

    notebook_cmd = Command(['jupyterhub-singleuser'],
        help="""
        The command used for starting the single-user server.
        Provide either a string or a list containing the path to the startup script command. Extra arguments,
        other than this path, should be provided via `args`.
        """
    ).tag(config=True)

    imagename = Unicode('',
        help="""
        Absolute POSIX filepath to Singularity image that will be used to
        execute the notebook server spawn command, if another path is not
        specified by the user.
        """
    ).tag(config=True)

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
        cmd.extend([self.default_image_path])
        cmd.extend(self.notebook_cmd)
        return cmd

    @property
    def cmd(self):
        return self._build_cmd()

    def get_env(self):
        """Get the complete set of environment variables to be set in the spawned process."""
        env = super().get_env()
        env = self.user_env(env)
        env['BIOJHUB_IMAGE'] = str(self.imagename)
        tmpdirpath = os.path.join('/tmp',self.user.name,self.imagename)
        if not os.path.exists(tmpdirpath):
            os.makedirs(tmpdirpath)
        env['SINGULARITY_BINDPATH'] = '/tmp/'+str(self.user.name)+'/'+str(self.imagename)+':/tmp'
        biojhubhome = str(subprocess.check_output('sudo -Hiu '+str(self.user.name)+' env| grep BIOJHUBHOME|cut -f2 -d "="', shell=True),'utf-8').rstrip()
        if biojhubhome is "":
            biojhubhome = '/data/users/'+str(self.user.name)+'/'+str(self.imagename)
        if not os.path.exists(biojhubhome):
            subprocess.check_output('sudo -u '+str(self.user.name)+' mkdir -p '+biojhubhome)
        env['SINGULARITY_HOME'] = biojhubhome 
        return env


    async def start(self):
        """Start the single-user server."""
        self.port = random_port()
        cmd = []
        env = self.get_env()

        cmd.extend(self.cmd)
        cmd.extend(self.get_args())

        if self.shell_cmd:
            # using shell_cmd (e.g. bash -c),
            # add our cmd list as the last (single) argument:
            cmd = self.shell_cmd + [' '.join(pipes.quote(s) for s in cmd)]

        self.log.info("Spawning %s", ' '.join(pipes.quote(s) for s in cmd))

        popen_kwargs = dict(
            preexec_fn=self.make_preexec_fn(self.user.name),
            start_new_session=True,  # don't forward signals
        )
        popen_kwargs.update(self.popen_kwargs)
        # don't let user config override env
        popen_kwargs['env'] = env
        try:
            self.proc = Popen(cmd, **popen_kwargs)
        except PermissionError:
            # use which to get abspath
            script = shutil.which(cmd[0]) or cmd[0]
            self.log.error(
                "Permission denied trying to run %r. Does %s have access to this file?",
                script,
                self.user.name,
            )
            raise

        self.pid = self.proc.pid

        if self.__class__ is not LocalProcessSpawner:
            # subclasses may not pass through return value of super().start,
            # relying on deprecated 0.6 way of setting ip, port,
            # so keep a redundant copy here for now.
            # A deprecation warning will be shown if the subclass
            # does not return ip, port.
            if self.ip:
                self.server.ip = self.ip
            self.server.port = self.port
            self.db.commit()
        return (self.ip or '127.0.0.1', self.port)
