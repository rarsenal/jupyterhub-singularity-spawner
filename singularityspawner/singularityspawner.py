# Copyright (c) 2017, Zebula Sampedro, CU Boulder Research Computing

"""
Singularity Spawner

SingularitySpawner provides a mechanism for spawning Jupyter Notebooks inside of Singularity containers. The spawner options form is leveraged such that the user can specify which Singularity image the spawner should use.

A `singularity exec {notebook spawn cmd}` is used to start the notebook inside of the container.
"""
