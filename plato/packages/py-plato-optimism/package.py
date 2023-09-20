# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
import os
import subprocess

class PyPlatoOptimism(Package):
    """Utilities for using OptimiSM with Plato for optimization-based design."""

    homepage = "https://cee-gitlab.sandia.gov/chamel/plato-optimism"
    git = "ssh://git@cee-gitlab.sandia.gov/chamel/plato-optimism.git"

    maintainers = ['ralberd','chamel']

    version("0.1.0", branch='main')

    depends_on("python", type=('build'))
    depends_on("py-pip")
    depends_on("py-optimism", type=("build", "run"))

    def install(self, spec, prefix):
        os.system("cp -r ./plato_optimism " + spec['py-plato-optimism'].prefix)

        list_files = subprocess.run(["pip", "install", "--target", spec['py-plato-optimism'].prefix.lib, "--trusted-host", "pypi.org", "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", "-e", "."])

    def setup_build_environment(self, build_env):
        build_env.prepend_path('PYTHONPATH', self.spec['py-pip'].prefix.lib)

    def setup_run_environment(self, run_env):
        run_env.prepend_path('PYTHONPATH', self.prefix)
        run_env.prepend_path('PYTHONPATH', self.prefix.lib)
