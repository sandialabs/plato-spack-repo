# Copyright 2012-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Platoengine(CMakePackage, CudaPackage):
    """Plato Engine - Platform for Topology Optimization"""
    
    homepage = "https://www.sandia.gov/plato3d/"
    url      = "https://github.com/sandialabs/platoengine.git"
    git      = "https://github.com/sandialabs/platoengine.git"

    maintainers = ['rviertel', 'jrobbin']

    version('develop', branch='develop', preferred=True)
    version('release-v0.1.0', branch='release-v0.1.0')

    
    variant( 'regression',     default=True,    description='Add regression tests'            )
    variant( 'unit_testing',   default=True,    description='Add unit testing'                )
    variant( 'esp',            default=False,   description='Turn on esp'                     )
    variant( 'sierra_tests',   default=False,   description='Enable sierra testing'           )
    variant( 'dev_build',      default=False,   description='Build with dev features such as sanitizers and clang-tidy')
    variant( 'snopt',          default=False,   description='Build with SNOPT'                )
    variant( 'python',         default=False,   description='Build and link with python. This option is needed for plugins that depend on python')
    variant( 'cubit',          default=False,   description='Build shape optimization geometry that uses Cubit library in prebuilt binaries'                )
    
    depends_on( 'mpi',            type=('build','link','run'))
    depends_on( 'cmake@3.0.0:',   type='build')
 
    trilinos_base_spec = 'trilinos@16.1.0+exodus+chaco+intrepid+shards+rol+tpetra~mumps'
    trilinos_base_add_ons = ' gotype=int cxxstd=17'
    depends_on( trilinos_base_spec + trilinos_base_add_ons)
    depends_on( trilinos_base_spec + '+boost+krino+stk+percept+zoltan' + trilinos_base_add_ons)
    depends_on( trilinos_base_spec + '+cuda+wrapper' + trilinos_base_add_ons, when='+cuda')
    depends_on( 'googletest',                                    when='+unit_testing' )
    
    depends_on( 'esp@124Lin', type=('build', 'link', 'run'), when='+esp')
    depends_on( 'numdiff', when='+regression')
    depends_on( 'boost+filesystem+serialization+system+program_options+regex+mpi+log')

    depends_on( 'snopt', when='+snopt')

    depends_on('python@3.8:', when='+python')
    depends_on('python@3.8:', when='+regression')
    depends_on('py-numpy',   when='+regression' )
    
    depends_on( 'llvm', when='+dev_build', type='build' )

    keep_werror = "all"

    def cmake_args(self):
        spec = self.spec

        options = []
        options.extend(
            [
                self.define("CMAKE_EXPORT_COMPILE_COMMANDS", "ON"),
                self.define("CMAKE_C_COMPILER", spec["mpi"].mpicc),
                self.define("CMAKE_CXX_COMPILER", spec["mpi"].mpicxx),
                self.define("CMAKE_Fortran_COMPILER", spec["mpi"].mpifc)
            ]
        )

        trilinos_dir = spec['trilinos'].prefix
        options.extend([ '-DTRILINOS_INSTALL_DIR:FILEPATH={0}'.format(trilinos_dir) ])

        options.extend(
            [
                self.define_from_variant("PLATOENGINE_ENABLE_CUDA","cuda"),
                self.define_from_variant("UNIT_TESTING","unit_testing"),
                self.define_from_variant("SIERRA_TESTS_ENABLED","sierra_tests"),
                self.define_from_variant("REGRESSION","regression"),
                self.define_from_variant("SEACAS","regression"),
                self.define_from_variant("BUILD_WITH_CLANG_TIDY","dev_build"),
                self.define_from_variant("BUILD_WITH_SANITIZER_FLAGS","dev_build"),
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

        gcc_toolchain_flag = list(filter(lambda flag: "gcc-toolchain" in flag, spec.compiler_flags["cxxflags"]))
        if gcc_toolchain_flag:
          options.extend(['-DGCC_TOOLCHAIN_PATH={0}'.format(gcc_toolchain_flag[0].split('=')[-1])])

        return options


    def setup_run_environment(self, run_env):
        run_env.prepend_path('LD_LIBRARY_PATH', self.spec['platoengine'].prefix.lib)
        run_env.prepend_path('LD_LIBRARY_PATH', self.spec['mpi'].prefix.lib)
        run_env.prepend_path('PATH', self.prefix.etc)

    def setup_build_environment(self, env):
        if '+cuda' in self.spec:
            # Overwrite mpi compiler env vars with nvcc_wrapper
            env.set("OMPI_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set("MPICH_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set("MPICXX_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
