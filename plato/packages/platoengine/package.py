# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Platoengine(CMakePackage, CudaPackage):
    """Plato Engine - Platform for Topology Optimization"""
    
    homepage = "https://www.sandia.gov/plato3d/"
    url      = "https://github.com/platoengine/platoengine/archive/v0.6.0.tar.gz"
    git      = "https://github.com/platoengine/platoengine.git"

    maintainers = ['rviertel', 'jrobbin']

    version('develop', branch='develop', preferred=True)
    version('release-v0.1.0', branch='release-v0.1.0')

    variant( 'platomain',      default=True,    description='Compile PlatoMain'               )
    variant( 'regression',     default=True,    description='Add regression tests'            )
    variant( 'unit_testing',   default=True,    description='Add unit testing'                )
    variant( 'albany_tests',   default=False,   description='Configure Albany tests'          )
    variant( 'esp',            default=False,   description='Turn on esp'                     )
    variant( 'expy',           default=False,   description='Compile exodus/python API'       )
    variant( 'iso',            default=False,   description='Turn on iso extraction'          )
    variant( 'platoproxy',     default=False,   description='Compile PlatoProxy'              )
    variant( 'python_app',     default=False,   description='Compile PythonInterpreter app'   )
    variant( 'prune',          default=False,   description='Turn on use of prune and refine' )
    variant( 'stk',            default=False,   description='Turn on use of stk'              )
    variant( 'tpetra_tests',   default=False,   description='Configure Tpetra tests'          )
    variant( 'dakota',         default=False,   description='Compile with Dakota'             )
    variant( 'services',       default=False,   description='Compile with services'           )
    variant( 'sierra_tests',   default=False,   description='Enable sierra testing'           )
    variant( 'optimism',       default=False,   description='Enable OptimiSM and its Plato utilities')
    variant( 'dev_build',      default=False,   description='Build with dev features such as sanitizers and clang-tidy')
    variant( 'snopt',          default=False,   description='Build with SNOPT'                )
    
    conflicts( '+expy', when='-platomain')
    conflicts( '+iso',  when='-stk')
    conflicts( '+prune',  when='-stk')
    conflicts( '@0.1.0', when='+prune')
    conflicts( '@0.2.0', when='+prune')
    conflicts( '@0.3.0', when='+prune')
    conflicts( '@0.4.0', when='+prune')
    conflicts( '@0.5.0', when='+prune')
    conflicts( '@0.6.0', when='+prune')
    conflicts( '+expy', when='+dakota')
    conflicts( '~services', when='+dakota')
    conflicts( '+optimism', when='~python_app')

    depends_on( 'mpi',            type=('build','link','run'))
    depends_on( 'cmake@3.0.0:',   type='build')
 
    depends_on( 'trilinos@16_0_0_stk_ub_fix+exodus+chaco+intrepid+shards+rol+tpetra gotype=int cxxstd=17')
    depends_on( 'trilinos+boost+stk', when='+stk')
    depends_on( 'trilinos+percept+zoltan+boost+stk', when='+prune')
    depends_on( 'trilinos+cuda+wrapper', when='+cuda')
    depends_on( 'trilinos~cuda', when='+dakota')
    depends_on( 'googletest',                                      when='+unit_testing' )
    depends_on( 'python@3.8:',    type=('build', 'link', 'run'), when='+expy'    )
    depends_on( 'nlopt',                                         when='+expy'         )
    # py-setuptools later than v44.1.0 require python 3.x
    depends_on( 'py-numpy',      when='+expy'         )

    depends_on( 'esp@124Lin', type=('build', 'link', 'run'), when='+esp')
    depends_on( 'dakota', when='+dakota')
    depends_on( 'numdiff', when='+regression')
    depends_on( 'boost+filesystem+serialization+system+program_options+regex+mpi')
    depends_on( 'boost+filesystem+serialization+system+program_options+regex+mpi+python', when='+python_app')
    depends_on( 'py-optimism', when='+optimism')

    depends_on( 'snopt', when='+snopt')
    
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
                self.define_from_variant("PLATOMAIN","platomain"),
                self.define_from_variant("PLATOPROXY","platoproxy"),
                self.define_from_variant("PYTHON_INTERPRETER_APP","python_app"),
                self.define_from_variant("UNIT_TESTING","unit_testing"),
                self.define_from_variant("ENABLE_ISO","iso"),
                self.define_from_variant("ENABLE_PRUNE","prune"),
                self.define_from_variant("STK_ENABLED","stk"),
                self.define_from_variant("PLATO_TPETRA","tpetra_tests"),
                self.define_from_variant("ENABLE_PLATO_SERVICES","services"),
                self.define_from_variant("SIERRA_TESTS_ENABLED","sierra_tests"),
                self.define_from_variant("OPTIMISM_TESTS_ENABLED","optimism"),
                self.define_from_variant("EXPY","expy"),
                self.define_from_variant("PLATO_ENABLE_SERVICES_PYTHON","expy"),
                self.define_from_variant("REGRESSION","regression"),
                self.define_from_variant("SEACAS","regression"),
                self.define_from_variant("BUILD_WITH_CLANG_TIDY","dev_build"),
                self.define_from_variant("BUILD_WITH_SANITIZER_FLAGS","dev_build")
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

        if '+dakota' in spec:
          boost_dir = spec['boost'].prefix
          options.extend(
              [
                self.define_from_variant("DAKOTADRIVER","dakota"),
                '-DBOOST_ROOT:FILEPATH={0}'.format(boost_dir),
                '-DCMAKE_CXX_COMPILER_VERSION={0}'.format(spec.compiler.version)  
              ]
            )  

        if '+expy' in self.spec or '+python_app' in self.spec:
          options.extend(
             ['-DPython3_EXECUTABLE={0}/python3'.format(self.spec['python'].prefix.bin)]
          )

        return options


    def setup_run_environment(self, run_env):
        run_env.prepend_path('LD_LIBRARY_PATH', self.spec['platoengine'].prefix.lib)

        if '+expy' in self.spec:
          run_env.prepend_path('PYTHONPATH', self.prefix.lib)
          run_env.prepend_path('PYTHONPATH', self.prefix.etc)

        run_env.prepend_path('LD_LIBRARY_PATH', self.spec['mpi'].prefix.lib)

        run_env.prepend_path('PATH', self.prefix.etc)

    def setup_build_environment(self, env):
        if '+cuda' in self.spec:
            # Overwrite mpi compiler env vars with nvcc_wrapper
            env.set("OMPI_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set("MPICH_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            env.set("MPICXX_CXX", self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)

