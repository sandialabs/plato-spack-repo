# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
import os
import subprocess


class PyOptimism(Package):
    """OptimiSM: Computational solid mechanics made easy with Jax."""

    homepage = "https://github.com/sandialabs/optimism"
    git = "https://github.com/sandialabs/optimism.git"

    maintainers = ['ralberd']

    version("0.0.1", branch='main')

    depends_on("python", type=('build'))
    depends_on("py-pip")
    depends_on("suite-sparse")

    def install(self, spec, prefix):
        os.system("cp -r ./optimism " + spec['py-optimism'].prefix)

        list_files = subprocess.run(["pip", "install", "--target", spec['py-optimism'].prefix.lib, "--trusted-host", "pypi.org", "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", "-e", ".[sparse]"])

    def setup_build_environment(self, build_env):
        build_env.prepend_path('PYTHONPATH', self.spec['python'].prefix.lib)
        build_env.prepend_path('PYTHONPATH', self.spec['py-pip'].prefix.lib)
        build_env.set("SUITESPARSE_INCLUDE_DIR", self.spec['suite-sparse'].prefix.include)
        build_env.set("SUITESPARSE_LIBRARY_DIR", self.spec['suite-sparse'].prefix.lib)

    def setup_run_environment(self, run_env):
        run_env.prepend_path('PYTHONPATH', self.prefix)
        run_env.prepend_path('PYTHONPATH', self.prefix.lib)
