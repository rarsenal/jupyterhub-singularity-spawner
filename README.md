# jupyterhub-singularity-spawner
Spawn user-specified Singularity containers with JupyterHub.

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
c.JupyterHub.spawner_class = 'singularityspawner.singularityspawner.SingularitySpawner'
c.SingularitySpawner.default_image_path = "/home/<username>/singularity/jupyter.img"
```

## Running Notebooks with Singularity
_**Note:** The manifest in this repo depends on the docker bootstrap method, so the Docker daemon must be installed and running._

This repo comes with a minimal Singularity manifest for running `jupyterhub-singleuser` within a Singularity container. To build the image _(using Singularity v2.3.1)_:
```
singularity create jupyter.img
sudo singularity bootstrap jupyter.img jupyter.def
```
