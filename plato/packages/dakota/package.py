# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Dakota(CMakePackage):
    """The Dakota toolkit provides a flexible, extensible interface between
    analysis codes and iterative systems analysis methods. Dakota
    contains algorithms for:

    - optimization with gradient and non gradient-based methods;
    - uncertainty quantification with sampling, reliability, stochastic
    - expansion, and epistemic methods;
    - parameter estimation with nonlinear least squares methods;
    - sensitivity/variance analysis with design of experiments and
    - parameter study methods.

    These capabilities may be used on their own or as components within
    advanced strategies such as hybrid optimization, surrogate-based
    optimization, mixed integer nonlinear programming, or optimization
    under uncertainty.

    """

    homepage = 'https://dakota.sandia.gov/'
    url = 'https://github.com/snl-dakota/dakota/releases/download/v6.16.0/dakota-6.16.0-public-src-cli.tar.gz'

    version('6.16', sha256='51c4aaa5ab453c48b6ffae0af1b21f2efa1a719a30eaf3e3712b2693c7e9a420')
    version('6.14', sha256='c3479ce49fc7a79df529ed052e809e4af2755f907734c802ccd609bbee220f8c')
    version('6.12', sha256='4d69f9cbb0c7319384ab9df27643ff6767eb410823930b8fbd56cc9de0885bc9')
    version('6.9', sha256='989b689278964b96496e3058b8ef5c2724d74bcd232f898fe450c51eba7fe0c2')
    version('6.3', sha256='0fbc310105860d77bb5c96de0e8813d75441fca1a5e6dfaf732aa095c4488d52')

    variant('shared', default=True,
            description='Enables the build of shared libraries')
    variant('mpi', default=True, description='Activates MPI support')
    variant('use_spack_trilinos', default=True, description='Instructs dakota to link to the version of Trilinos installed by spack rather than the snapshot included in its source code')

    # Generic 'lapack' provider won't work, dakota searches for
    # 'LAPACKConfig.cmake' or 'lapack-config.cmake' on the path
    depends_on('netlib-lapack')

    depends_on('blas')
    depends_on('mpi', when='+mpi')
    depends_on('trilinos+teuchos+rol+mpi', when='+use_spack_trilinos')

    depends_on('python')
    depends_on('perl-data-dumper', type='build', when='@6.12:')
    depends_on('boost@:1.68.0', when='@:6.12')
    depends_on('boost@1.58.0:', when='@6.14:')
    depends_on('cmake@2.8.9:', type='build')

    patch('616.patch', when='@6.16:')

    def cmake_args(self):
        spec = self.spec

        args = [
            '-DBUILD_SHARED_LIBS:BOOL=%s' % (
                'ON' if '+shared' in spec else 'OFF'),
        ]

        if '+mpi' in spec:
            args.extend([
                '-DDAKOTA_HAVE_MPI:BOOL=ON',
                '-DMPI_CXX_COMPILER:STRING=%s' % join_path(spec['mpi'].mpicxx)
            ])
        if '+use_spack_trilinos' in spec:
            args.extend([
                '-DTrilinos_DIR:PATH=%s' % join_path(spec['trilinos'].prefix),
                '-DDAKOTA_NO_FIND_TRILINOS:BOOL=FALSE',
                '-DCMAKE_CXX_STANDARD=17'
            ])
        else:
            args.extend([
                '-DDAKOTA_NO_FIND_TRILINOS:BOOL=TRUE'
            ])

        return args

    def url_for_version(self, version):
        url = 'https://github.com/snl-dakota/dakota/releases/download/v{0}.0/dakota-{0}.0-public-src-cli.tar.gz'
        return url.format(version)
