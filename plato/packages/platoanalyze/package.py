##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *


class Platoanalyze(CMakePackage, CudaPackage):
    """Plato Analyze"""

    homepage = "https://github.com/platoengine/platoanalyze"
    url      = "https://github.com/platoengine/platoanalyze"
    git      = "https://github.com/platoengine/platoanalyze.git"

    maintainers = ['rviertel', 'jrobbin']

    version('develop', branch='develop', submodules=True, preferred=True)
    version('release-v0.1.0', branch='release-v0.1.0', submodules=True)

    variant( 'cuda',       default=True,     description='Compile with Nvidia CUDA'     )
    variant( 'amgx',       default=True,     description='Compile with AMGX'            )
    variant( 'meshmap',    default=True,     description='Compile with MeshMap'         )
    variant( 'mpmd',       default=True,     description='Compile with mpmd'            )
    variant( 'physics',    default=True,     description='Compile with all Physics'      )
    variant( 'helmholtz',  default=True,     description='Compile with Helmholtz filter' )
    variant( 'unittests',  default=True,     description='Compile with unit tests' )
    variant( 'enginemesh', default=True,     description='Compile with enginemesh as default' )
    variant( 'omega-h',    default=False,    description='Compile with enginemesh as default' )
    variant( 'esp',        default=False,    description='Compile with ESP'             )
    variant( 'openmp',     default=False,    description='Compile with openmp'          )
    variant( 'python',     default=False,    description='Compile with python'          )
    variant( 'tpetra',     default=False,    description='Compile with Tpetra'          )
    variant( 'tacho',      default=False,    description='Compile with Tacho'           )
    variant( 'umfpack',    default=False,    description='Compile with UMFPACK'         )
    variant( 'epetra',     default=True,     description='Compile with Epetra'          )

    variant( 'integration_tests', default=True, description='Compile with engine integration tests')
    variant( 'dakota_tests', default=False, description='Compile with Dakota integration tests')
    variant( 'verificationtests', default=True, description='Compile with verification tests' )
    variant( 'verificationdoc', default=False,  description='Compile with VerificationDoc target' )
    variant( 'hex_elements', default=False, description='Compile with hex elements' ) 
    variant( 'micromorphic', default=False, description='Compile with micromorphic physics' ) 
    variant( 'all_penalty', default=False, description='Compile with all penalization schemes, including RAMP and Heaviside' )

    depends_on('trilinos@15.0.0+kokkos+kokkoskernels+exodus gotype=int cxxstd=17')
    depends_on('trilinos+cuda+wrapper', when='+cuda')
    depends_on('trilinos+openmp', when='+openmp')
    depends_on('trilinos+tacho', when='+tacho')
    depends_on('suite-sparse', when='+umfpack')
    depends_on('trilinos+tpetra+belos+ifpack2+amesos2+muelu+zoltan2',             when='+tpetra')
    depends_on('trilinos~tpetra~amesos2~ifpack2~belos~muelu~zoltan2',             when='~tpetra')
    depends_on('trilinos~epetra',                                                 when='~epetra')

    depends_on('kokkos-nvcc-wrapper@4.0.01', when='+cuda')

    depends_on('platoengine~dakota',                                              when='+cuda+mpmd')
    depends_on('platoengine+dakota',                                              when='+dakota_tests')

    depends_on('cmake@3.0.0:', type='build')
    depends_on('python @3.8:',                               when='+python')
    depends_on('platoengine+expy',                           when='+python')
    depends_on('platoengine+expy',                           when='+verificationtests')

    depends_on('arborx~mpi~cuda~serial @v1.1',              when='+meshmap')
    depends_on('amgx@2.2',                                  when='+amgx')
    depends_on('esp@BetaLin-2023-11-09', type=('build', 'link', 'run'),        when='+esp')
    depends_on('platoengine+esp',                           when='+esp')
    depends_on('numdiff',                                   when='+integration_tests')
    depends_on('py-numpy',                                  when='+dakota_tests')

    # omega-h writes vtk files so paraview is required for verification tests
    # remove this dependency when omega-h is no longer a variant
    depends_on('paraview+python build_edition=canonical',  when='+verificationtests~enginemesh')

    depends_on('paraview+python build_edition=canonical',  when='+verificationdoc')
    depends_on('gnuplot',  when='+verificationdoc')
    depends_on('doxygen',  when='+verificationdoc')

    conflicts('+enginemesh', when='~mpmd')
    conflicts('+meshmap',  when='~mpmd')
    conflicts('+amgx',     when='~cuda')
    conflicts('+openmp',   when='+cuda')
    depends_on('omega-h@develop_bb6b', type=('build', 'link', 'run'), when='+omega-h')
    depends_on('omega-h+cuda',                              when='+cuda+omega-h')

    conflicts('~epetra',    when='~tpetra')
    conflicts('~omega-h',   when='~enginemesh')
    conflicts('+omega-h',   when='+enginemesh')
    conflicts('+unittests', when='~physics')

    def cmake_args(self):
        spec = self.spec
        options = []

        options.extend([ '-DBUILD_SHARED_LIBS:BOOL=ON' ])

        trilinos_dir = spec['trilinos'].prefix
        options.extend([ '-DTrilinos_PREFIX:PATH={0}'.format(trilinos_dir) ])

        if '+mpmd' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_MPMD=ON' ])

          platoengine_dir = spec['platoengine'].prefix
          options.extend([ '-DPLATOENGINE_PREFIX:PATH={0}'.format(platoengine_dir) ])

        else:
          options.extend([ '-DPLATOANALYZE_ENABLE_MPMD=OFF' ])

        if '+omega-h' in spec:
          omega_h_dir = spec['omega-h'].prefix
          options.extend([ '-DOMEGA_H_PREFIX:PATH={0}'.format(omega_h_dir) ])

        if '+python' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_PYTHON=ON' ])

        if '+enginemesh' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_ENGINEMESH=ON' ])
        else:
          options.extend([ '-DPLATOANALYZE_ENABLE_ENGINEMESH=OFF' ])

        if '+cuda' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_CUDA=ON' ])

        if '+meshmap' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_MESHMAP=ON' ])

        if '+tpetra' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_TPETRA=ON' ])

        if '+tacho' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_TACHO=ON' ])

        if '+umfpack' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_UMFPACK=ON' ])
          umfpack_lib_dir = spec['suite-sparse'].prefix.lib
          umfpack_inc_dir = spec['suite-sparse'].prefix.include
          options.extend([ '-DUMFPACK_LIB_DIR:PATH={0}'.format(umfpack_lib_dir) ])
          options.extend([ '-DUMFPACK_INC_DIR:PATH={0}'.format(umfpack_inc_dir) ])

        if '+epetra' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_EPETRA=ON' ])

        if '+esp' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_ESP=ON' ])
          esp_lib_dir = spec['esp'].prefix+'/lib'
          esp_inc_dir = spec['esp'].prefix+'/include'
          options.extend([ '-DESP_LIB_DIR:PATH={0}'.format(esp_lib_dir) ])
          options.extend([ '-DESP_INC_DIR:PATH={0}'.format(esp_inc_dir) ])

        if '+amgx' in spec:
          amgx_dir = spec['amgx'].prefix
          options.extend([ '-DAMGX_PREFIX:PATH={0}'.format(amgx_dir) ])
          options.extend([ '-DPLATOANALYZE_ENABLE_AMGX=ON' ])
          
        if '~physics' in spec:
          options.extend([ '-DELLIPTIC=OFF' ])
          options.extend([ '-DPARABOLIC=OFF' ])
          options.extend([ '-DHYPERBOLIC=OFF' ])
          options.extend([ '-DSTABILIZED=OFF' ])
          options.extend([ '-DPLASTICITY=OFF' ])

        if '+helmholtz' in spec:
          options.extend([ '-DHELMHOLTZ=ON' ])

        if '~helmholtz' in spec:
          options.extend([ '-DHELMHOLTZ=OFF' ])

        if '~unittests' in spec:
          options.extend([ '-DPLATOANALYZE_UNIT_TEST=OFF' ])

        if '+integration_tests' in spec:
          options.extend([ '-DPLATOANALYZE_INTEGRATION_TESTS=ON' ])

        if '+dakota_tests' in spec:
          options.extend([ '-DPLATOANALYZE_DAKOTA_TESTS=ON' ])

        if '+services' in spec['platoengine']:
            options.extend(['-DPLATOANALYZE_PE_SERVICES=ON'])

        if '+stk' in spec['platoengine']:
          options.extend([ '-DPLATOANALYZE_STK_ENABLED=ON' ])

        if '+expy' in spec['platoengine']:
          options.extend([ '-DEXPY=ON' ])

        if '+iso' in spec['platoengine']:
          options.extend([ '-DENABLE_ISO=ON' ])

        if '+verificationtests' in spec:
          options.extend(['-DPLATOANALYZE_SMOKE_TESTS=ON'])
        elif '~verificationtests' in spec:
          options.extend(['-DPLATOANALYZE_SMOKE_TESTS=OFF'])

        if '+hex_elements' in spec:
            options.extend(['-DHEX_ELEMENTS=ON'])
        else:
            options.extend(['-DHEX_ELEMENTS=OFF'])

        if '+micromorphic' in spec:
            options.extend(['-DMICROMORPHIC=ON'])
        else:
            options.extend(['-DMICROMORPHIC=OFF'])

        if '+all_penalty' in spec:
            options.extend(['-DALL_PENALTY=ON'])

        return options

    def setup_run_environment(self, run_env):
        run_env.prepend_path('LD_LIBRARY_PATH', self.spec['platoanalyze'].prefix.lib)
        if '+python' in self.spec:
          run_env.prepend_path('PYTHONPATH', self.prefix.lib)
