# jupyterhub-singularity-spawner
Spawn user-specified Singularity containers with JupyterHub.

## Pip Installation
To install Singularity Spawner via Pip:
```
pip install jupyterhub-singularity-spawner
```

## Dev Installation
To install Singularity Spawner, clone the repo and do an editable pip install in your JupyterHub environment:
```
git clone https://github.com/ResearchComputing/jupyterhub-singularity-spawner.git
cd jupyterhub-singularity-spawner
pip install -e .
```

## Configuration
A basic configuration for Singularity Spawner _(in the JupyterHub config file)_:
```python
c.JupyterHub.spawner_class = 'singularityspawner.SingularitySpawner'
c.SingularitySpawner.default_image_url = "docker://jupyter/base-notebook"
c.SingularitySpawner.default_image_path = "/home/{username}/singularity/jupyter.img"
```

## Running Notebooks with Singularity
[Jupyter Docker Stacks](https://github.com/jupyter/docker-stacks) can be used as a base for building custom notebook environments run in Singularity containers.
