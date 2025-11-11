# Copyright 2012-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import pathlib
from spack.package import *
from spack_repo.builtin.build_systems.cmake import CMakePackage

class Platoengine(CMakePackage):
    """Plato Engine - Platform for Topology Optimization"""
    
    homepage = "https://www.sandia.gov/plato3d/"
    url      = "https://github.com/sandialabs/platoengine.git"
    git      = "https://github.com/sandialabs/platoengine.git"

    maintainers = ['acsokol', 'bwclark', 'ralberd', 'rawildm', 'shardes']

    version('develop', branch='develop', preferred=True)
    version('2.0.2', tag='2.0.2')
    
    variant( 'regression',     default=True,    description='Add regression tests'            )
    variant( 'unit_testing',   default=True,    description='Add unit testing'                )
    variant( 'esp',            default=False,   description='Turn on esp'                     )
    variant( 'sierra_tests',   default=False,   description='Enable sierra testing'           )
    variant( 'snopt',          default=False,   description='Build with SNOPT'                )
    variant( 'python',         default=False,   description='Build and link with python. This option is needed for plugins that depend on python')
    variant( 'cubit',          default=False,   description='Build shape optimization geometry that uses Cubit library in prebuilt binaries'                )
    variant( 'cmake_preset',   values=('none', 'default', 'dev_build'), default='default', description='Chooses a cmake configuration preset, which controls build parameters such as warnings' )

    depends_on( 'cxx', type="build")
    depends_on( 'mpi', type=('build','link','run'))
    depends_on( 'cmake@3.21.0:', type='build')
    depends_on( 'googletest', when='+unit_testing' )
    depends_on( 'boost+filesystem+serialization+system+program_options+regex+mpi+log')
    depends_on( 'trilinos@16_1_0_update_krino_api+exodus+chaco+shards+rol+tpetra~epetra~epetraext~mumps+boost+percept+krino+stk gotype=int cxxstd=17' )    
    depends_on( 'esp@124Lin', type=('build', 'link', 'run'), when='+esp')
    depends_on( 'numdiff', when='+regression')
    depends_on( 'snopt', when='+snopt')
    depends_on( 'python@3.8:', when='+python')
    depends_on( 'python@3.8:', when='+regression')
    depends_on( 'py-numpy', when='+regression' )
    depends_on( 'llvm', when='cmake_preset=dev_build', type='build' )

    keep_werror = "all"

    def cmake_args(self):
        spec = self.spec

        options = []

        if self.spec.variants['cmake_preset'].value != 'none':
            options.extend(
                [
                    '--preset {}'.format(self.spec.variants['cmake_preset'].value)
                ]
            )

        options.extend(
            [
                self.define("CMAKE_C_COMPILER", spec["mpi"].mpicc),
                self.define("CMAKE_CXX_COMPILER", spec["mpi"].mpicxx),
                self.define("CMAKE_Fortran_COMPILER", spec["mpi"].mpifc),
            ]
        )

        options.extend(
            [
                self.define_from_variant("UNIT_TESTING","unit_testing"),
                self.define_from_variant("SIERRA_TESTS_ENABLED","sierra_tests"),
                self.define_from_variant("REGRESSION","regression"),
                self.define_from_variant("SEACAS","regression"),
                self.define_from_variant("LINK_WITH_PYTHON","python"),
                self.define_from_variant("CUBIT_ENABLED","cubit")
            ]
        )

        if '+esp' in spec:
          esp_lib_dir = spec['esp'].prefix+'/lib'
          esp_inc_dir = spec['esp'].prefix+'/include'
          options.extend(
              [
                self.define_from_variant("ESP_ENABLED","esp"),
                '-DESP_LIB_DIR:PATH={0}'.format(esp_lib_dir),
                '-DESP_INC_DIR:PATH={0}'.format(esp_inc_dir)   
              ]
            )
        if '+snopt' in spec:
          snopt_lib_dir = spec['snopt'].prefix+'/lib'
          snopt_inc_dir = spec['snopt'].prefix+'/include'
          options.extend(
              [
                  self.define_from_variant("SNOPT_ENABLED","snopt"),
                  '-DSNOPT_LIB_DIR:PATH={0}'.format(snopt_lib_dir),
                  '-DSNOPT_INC_DIR:PATH={0}'.format(snopt_inc_dir)
              ]
            )
        
        gcc_toolchain_flag = list(filter(lambda flag: "gcc-toolchain" in flag, self.spec.compiler_flags["cxxflags"]))
        if gcc_toolchain_flag:
            gcc_toolchain_path = gcc_toolchain_flag[0].split('=')[-1]
            options.extend(['-DGCC_TOOLCHAIN_PATH={0}'.format(gcc_toolchain_path)])
        
        return options

