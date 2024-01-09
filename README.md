# Plato Spack Repo

This repo contains custom spack packages for Plato.
Spack handles external repositories using the `spack repo` sub-command.
When using [super-plato](https://cee-gitlab.sandia.gov/1540-compsim/plato/plato-spack-repo), adding this repo is handled in the set-up scripts.
Otherwise, when setting up a new environment, the following will add the custom plato packages to your spack environment:
```
spack repo add plato-spack-repo/plato
```

You can confirm that the repo was added correctly using:
```
spack repo list
```

