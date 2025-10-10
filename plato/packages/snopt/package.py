from spack_repo.builtin.build_systems.generic import Package
from spack.package import *
import os

class Snopt(Package):
    url='file://{0}/plato-prebuilt-binaries/snopt/snopt-7.7.3.tgz'.format(os.getcwd())
    
    version('7.7.3', sha256='9a91d2fd536470af3dd0afd0496345308c26d7d2178594c62152a8860bf7526f')
    depends_on("fortran", type="build")
    depends_on("cxx", type="build")
    depends_on("c", type="build")
    depends_on('gmake', type='build')


    def install(self, spec, prefix):
        configure("--prefix={0}".format(prefix), "--with-cpp")
        make('prefix={0}'.format(self.prefix), parallel=False)
