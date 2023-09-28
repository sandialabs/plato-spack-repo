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
    variant( 'platostatics',   default=True,    description='Compile PlatoStatics'            )
    variant( 'regression',     default=True,    description='Add regression tests'            )
    variant( 'unit_testing',   default=True,    description='Add unit testing'                )
    variant( 'albany_tests',   default=False,   description='Configure Albany tests'          )
    variant( 'esp',            default=False,   description='Turn on esp'                     )
    variant( 'expy',           default=False,   description='Compile exodus/python API'       )
    variant( 'iso',            default=False,   description='Turn on iso extraction'          )
    variant( 'platoproxy',     default=False,   description='Compile PlatoProxy'              )
    variant( 'python_app',     default=False,   description='Compile PythonInterpreter app'              )
    variant( 'prune',          default=False,   description='Turn on use of prune and refine' )
    variant( 'stk',            default=False,   description='Turn on use of stk'              )
    variant( 'tpetra_tests',   default=False,   description='Configure Tpetra tests'          )
    variant( 'dakota',         default=False,   description='Compile with Dakota'             )
    variant( 'services',       default=False,   description='Compile with services'           )
    variant( 'sierra_tests',   default=False,   description='Enable sierra testing'           )
    variant( 'xtk',            default=False,   description='Enable XTK'                      )
    variant( 'optimism',       default=False,   description='Enable OptimiSM and its Plato utilities')

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
    conflicts( '+xtk', when='+cuda')
    conflicts( '+optimism', when='~python_app')

    depends_on( 'mpi',            type=('build','link','run'))
    depends_on( 'cmake@3.0.0:',   type='build')
 
    depends_on( 'trilinos@14.4.0+exodus+chaco+intrepid+shards+rol gotype=int cxxstd=17')
    depends_on( 'trilinos+boost+stk', when='+stk')
    depends_on( 'trilinos+percept+zoltan+boost+stk', when='+prune')
    depends_on( 'trilinos+cuda+wrapper', when='+cuda')
    depends_on( 'trilinos~cuda', when='+dakota')

    depends_on( 'googletest',                                      when='+unit_testing' )
    depends_on( 'python@3.8:',    type=('build', 'link', 'run'), when='+expy'    )
    depends_on( 'nlopt',                                         when='+expy'         )
    # py-setuptools later than v44.1.0 require python 3.x
    depends_on( 'py-numpy',      when='+expy'         )

    depends_on( 'esp@BetaLin-2023-07-17', type=('build', 'link', 'run'), when='+esp')
    depends_on( 'dakota', when='+dakota')
    depends_on( 'numdiff', when='+regression')
    depends_on( 'boost+filesystem+serialization+system+program_options+regex')

    depends_on( 'boost+filesystem+serialization+system+program_options+regex+python', when='+python_app')

    depends_on( 'py-plato-optimism', when='+optimism')

    depends_on( 'moris cppflags=\"-Wno-error=deprecated-declarations -Wno-error=type-limits\"', when='+xtk')

    def cmake_args(self):
        spec = self.spec

        options = []
        options.extend(
            [
                self.define("CMAKE_C_COMPILER", spec["mpi"].mpicc),
                self.define("CMAKE_CXX_COMPILER", spec["mpi"].mpicxx),
                self.define("CMAKE_Fortran_COMPILER", spec["mpi"].mpifc)
            ]
        )

        trilinos_dir = spec['trilinos'].prefix
        options.extend([ '-DTRILINOS_INSTALL_DIR:FILEPATH={0}'.format(trilinos_dir) ])

        if '+platomain' in spec:
          options.extend([ '-DPLATOMAIN=ON' ])

        if '+platoproxy' in spec:
          options.extend([ '-DPLATOPROXY=ON' ])

        if '+python_app' in spec:
          options.extend([ '-DPYTHON_INTERPRETER_APP=ON' ])

        if '+platostatics' in spec:
          options.extend([ '-DPLATOSTATICS=ON' ])

        if '+expy' in spec:
          options.extend([ '-DEXPY=ON' ])
          options.extend([ '-DPLATO_ENABLE_SERVICES_PYTHON=ON' ])

        if '+regression' in spec:
          options.extend([ '-DREGRESSION=ON' ])
          options.extend([ '-DSEACAS=ON' ])
          numdiff_dir = spec['numdiff'].prefix
          options.extend([ '-DNUMDIFF_PATH:FILEPATH={0}'.format(numdiff_dir) ])

        if '+unit_testing' in spec:
          options.extend([ '-DUNIT_TESTING=ON' ])
          # gtest_dir = spec['googletest'].prefix
        else:
          options.extend([ '-DUNIT_TESTING=OFF' ])

          # options.extend([ '-DGTEST_HOME:FILEPATH={0}'.format(gtest_dir) ])

        if '+iso' in spec:
          options.extend([ '-DENABLE_ISO=ON' ])

        if '+prune' in spec:
          options.extend([ '-DENABLE_PRUNE=ON' ])

        if '+stk' in spec:
          options.extend([ '-DSTK_ENABLED=ON' ])

        if '+xtk' in spec:
          options.extend([ '-DXTK_ENABLED=ON' ])
          xtk_inc_dir = spec['moris'].prefix
          options.extend([ '-DXTK_INSTALL:PATH={0}'.format(xtk_inc_dir) ])

        if '+esp' in spec:
          options.extend([ '-DESP_ENABLED=ON' ])
          esp_lib_dir = spec['esp'].prefix+'/lib'
          esp_inc_dir = spec['esp'].prefix+'/include'
          options.extend([ '-DESP_LIB_DIR:PATH={0}'.format(esp_lib_dir) ])
          options.extend([ '-DESP_INC_DIR:PATH={0}'.format(esp_inc_dir) ])

        if '-stk' in spec:
          options.extend([ '-DSTK_ENABLED=OFF' ])

        if '+albany_tests' in spec:
          options.extend([ '-DALBANY=ON' ])
          options.extend([ '-DALBANY_BINARY=AlbanyMPMD' ])

        if '+tpetra_tests' in spec:
          options.extend([ '-DPLATO_TPETRA=ON' ])

        if '+dakota' in spec:
          options.extend([ '-DDAKOTADRIVER=ON' ])
          boost_dir = spec['boost'].prefix
          options.extend([ '-DBOOST_ROOT:FILEPATH={0}'.format(boost_dir) ])
          options.extend([ '-DCMAKE_CXX_COMPILER_VERSION={0}'.format(spec.compiler.version)])

        if '+services' in spec:
          options.extend([ '-DENABLE_PLATO_SERVICES=ON' ])

        if '+sierra_tests' in spec:
          options.extend([ '-DSIERRA_TESTS_ENABLED=ON' ])

        if '+optimism' in spec:
          options.extend([ '-DOPTIMISM_TESTS_ENABLED=ON' ])

        return options


    def setup_run_environment(self, run_env):

        if '+expy' in self.spec:
          run_env.prepend_path('PYTHONPATH', self.prefix.lib)
          run_env.prepend_path('PYTHONPATH', self.prefix.etc)

        run_env.prepend_path('LD_LIBRARY_PATH', self.spec['mpi'].prefix.lib)

        run_env.prepend_path('PATH', self.prefix.etc)
