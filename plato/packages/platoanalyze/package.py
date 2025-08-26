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
    variant( 'physics',    default=True,     description='Compile with all Physics'      )
    variant( 'helmholtz',  default=True,     description='Compile with Helmholtz filter' )
    variant( 'unittests',  default=True,     description='Compile with unit tests' )
    variant( 'enginemesh', default=True,     description='Compile with enginemesh as default' )
    variant( 'omega-h',    default=False,    description='Compile with enginemesh as default' )
    variant( 'openmp',     default=False,    description='Compile with openmp'          )
    variant( 'tpetra',     default=False,    description='Compile with Tpetra'          )
    variant( 'tacho',      default=False,    description='Compile with Tacho'           )
    variant( 'umfpack',    default=False,    description='Compile with UMFPACK'         )
    variant( 'dev_build',  default=False,    description='Build with dev features such as sanitizers')

    variant( 'integration_tests', default=True, description='Compile with engine integration tests')
    variant( 'verificationtests', default=True, description='Compile with verification tests' )
    variant( 'verificationdoc', default=False,  description='Compile with VerificationDoc target' )
    variant( 'hex_elements', default=False, description='Compile with hex elements' ) 
    variant( 'micromorphic', default=False, description='Compile with micromorphic physics' ) 
    variant( 'all_penalty', default=False, description='Compile with all penalization schemes, including RAMP and Heaviside' )


    depends_on('platoengine')
    depends_on('trilinos@16.1.0+kokkos+kokkoskernels+exodus gotype=int cxxstd=17')
    depends_on('trilinos+cuda+wrapper', when='+cuda')
    depends_on('trilinos+openmp', when='+openmp')
    depends_on('trilinos+tacho', when='+tacho')
    depends_on('suite-sparse', when='+umfpack')
    depends_on('trilinos+tpetra+belos+ifpack2+amesos2+muelu+zoltan2',             when='+tpetra')
    depends_on('trilinos~tpetra~amesos2~ifpack2~belos~muelu~zoltan2',             when='~tpetra')

    depends_on('kokkos-nvcc-wrapper@4.0.01', when='+cuda')

    depends_on('cmake@3.0.0:', type='build')   
    
    depends_on( 'python@3.8:',    type=('build', 'link', 'run'), when='+verificationtests'    )
    depends_on( 'python@3.8:',    type=('build', 'link', 'run'), when='+integration_tests'    )
    depends_on( 'py-numpy',      when='+verificationtests'         )
    depends_on( 'py-numpy',      when='+integration_tests'         )
    depends_on('platoengine+unit_testing', when='+integration_tests'    )
    depends_on('platoengine+unit_testing', when='+verificationtests'    )
    depends_on('arborx~mpi~cuda~serial @v1.1',              when='+meshmap')
    depends_on('amgx',                                      when='+amgx')
    depends_on('numdiff',                                   when='+integration_tests')
    
    # omega-h writes vtk files so paraview is required for verification tests
    # remove this dependency when omega-h is no longer a variant
    depends_on('paraview+python build_edition=canonical',  when='+verificationtests~enginemesh')
    depends_on('paraview+python build_edition=canonical',  when='+verificationdoc')
    depends_on('gnuplot',  when='+verificationdoc')
    depends_on('doxygen',  when='+verificationdoc')

    conflicts('+amgx',     when='~cuda')
    conflicts('+openmp',   when='+cuda')
    depends_on('omega-h@develop_bb6b', type=('build', 'link', 'run'), when='+omega-h')
    depends_on('omega-h+cuda',                              when='+cuda+omega-h')

    conflicts('~omega-h',   when='~enginemesh')
    conflicts('+omega-h',   when='+enginemesh')
    conflicts('+unittests', when='~physics')

    keep_werror = "all"
    
    def cmake_args(self):
        spec = self.spec
        options = []

        options.extend([
          self.define("CMAKE_EXPORT_COMPILE_COMMANDS", "ON"),
          self.define("CMAKE_C_COMPILER", spec["mpi"].mpicc),
          self.define("CMAKE_CXX_COMPILER", spec["mpi"].mpicxx),
          self.define("CMAKE_Fortran_COMPILER", spec["mpi"].mpifc),
          self.define("BUILD_SHARED_LIBS", "ON")
        ])

        trilinos_dir = spec['trilinos'].prefix
        options.extend([ '-DTrilinos_PREFIX:PATH={0}'.format(trilinos_dir) ])

        options.extend(
            [
                self.define_from_variant("PLATOANALYZE_ENABLE_ENGINEMESH","enginemesh"),
                self.define_from_variant("PLATOANALYZE_ENABLE_CUDA","cuda"),
                self.define_from_variant("PLATOANALYZE_ENABLE_MESHMAP","meshmap"),
                self.define_from_variant("PLATOANALYZE_ENABLE_TPETRA","tpetra"),
                self.define_from_variant("PLATOANALYZE_ENABLE_TACHO","tacho"),
                self.define_from_variant("HELMHOLTZ","helmholtz"),
                self.define_from_variant("PLATOANALYZE_UNIT_TEST","unittests"),
                self.define_from_variant("PLATOANALYZE_INTEGRATION_TESTS","integration_tests"),
                self.define_from_variant("PLATOANALYZE_SMOKE_TESTS","verificationtests"),
                self.define_from_variant("HEX_ELEMENTS","hex_elements"),
                self.define_from_variant("MICROMORPHIC","micromorphic"),
                self.define_from_variant("ALL_PENALTY","all_penalty"),
                self.define_from_variant("BUILD_WITH_SANITIZER_FLAGS","dev_build")
            ]
        )

        platoengine_dir = spec['platoengine'].prefix
        options.extend([ '-DPLATOENGINE_PREFIX:PATH={0}'.format(platoengine_dir) ])

        if '+omega-h' in spec:
          omega_h_dir = spec['omega-h'].prefix
          options.extend([ '-DOMEGA_H_PREFIX:PATH={0}'.format(omega_h_dir) ])

        if '+umfpack' in spec:
          options.extend([ '-DPLATOANALYZE_ENABLE_UMFPACK=ON' ])
          umfpack_lib_dir = spec['suite-sparse'].prefix.lib
          umfpack_inc_dir = spec['suite-sparse'].prefix.include
          options.extend([ '-DUMFPACK_LIB_DIR:PATH={0}'.format(umfpack_lib_dir) ])
          options.extend([ '-DUMFPACK_INC_DIR:PATH={0}'.format(umfpack_inc_dir) ])
        
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

        if '+cubit' in spec['platoengine']:
          options.extend([ '-DPLATOANALYZE_CUBIT_ENABLED=ON' ])

        if '+verificationtests' in self.spec or '+integration_tests' in self.spec:
          options.extend(
             ['-DPython3_EXECUTABLE={0}/python3'.format(self.spec['python'].prefix.bin)]
          )

        return options

    def setup_run_environment(self, run_env):
        run_env.prepend_path('LD_LIBRARY_PATH', self.spec['platoanalyze'].prefix.lib)
        if '+verificationtests' in self.spec or '+integration_tests' in self.spec:
          run_env.prepend_path('PYTHONPATH', self.prefix.lib)
          run_env.prepend_path('PYTHONPATH', self.prefix.etc)


    def setup_build_environment(self, env):
        if '+cuda' in self.spec:
            # Overwrite mpi compiler env vars with nvcc_wrapper
            env.set("OMPI_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set("MPICH_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set("MPICXX_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
