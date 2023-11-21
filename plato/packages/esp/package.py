from distutils.dir_util import copy_tree
from spack import *

class Esp(Package):
    """Engineering SketchPad by Bob Haimes at MIT"""

    homepage = "https://acdl.mit.edu/ESP/"

    version('BetaLin-2023-11-09', sha256='a63df74f90c926c6ca127cb8e973a61502739b94bb7c0d2579668a888c050c94', url='https://acdl.mit.edu/ESP/archive/ESPbeta-linux-x86_64_2023-11-13.tgz')
    version('BetaLin-2023-10-11', sha256='5798cdc86712e6ae131d72077a12a4612a5bf74a6f73b82797baf2293fd85493', url='https://acdl.mit.edu/ESP/archive/ESPbeta-linux-x86_64_2023-10-11.tgz')
    version('BetaLin-2023-07-17', sha256='483edb0d48e3be659bfa927e6424eb7c0502fd1b7ad6cefaeee69a65808dc048', url='https://acdl.mit.edu/ESP/archive/ESPbeta-linux-x86_64_2023-07-17.tgz')
    version('123Lin', sha256='06a3417594af180daa4c18cdceb82ba8885c1350b05c21dde466320dcab4d286', url='https://acdl.mit.edu/ESP/PreBuilts/ESP123-linux-x86_64.tgz',preferred=True)
    version('122Lin', sha256='a629c089f488ca9ce2da9fcaed0fdcba60bb4f2e9287cd3725b296e0fa6af197', url='https://acdl.mit.edu/ESP/archive/ESP122Lin.tgz')
    version('121Lin', sha256='c9ed01f6acf2cc1b0d2a035a563efa8e0ab5b857269fdd6776596abffc98dc89', url='https://acdl.mit.edu/ESP/PreBuilts/ESP121Lin.tgz')
    version('120Lin', sha256='d16c7d90d4e1b46973113e47f474b59057df35f9bd55680c3430aface1571ba9', url='https://acdl.mit.edu/ESP/archive/ESP120Lin.tgz')
    version('117Lin', sha256='bd6418ee9dafabdc17c58449c379535f4f148f1f67730074297c605b5e10e1a0', url='https://acdl.mit.edu/ESP/archive/ESP117Lin.tgz')

    depends_on( 'python@2.6:', type=('run'), when='@117Lin' )
    depends_on( 'python@3.8:', type=('run'), when='@120Lin' )
    depends_on( 'python@3.8:', type=('run'), when='@121Lin' )
    depends_on( 'python@3.8:', type=('run'), when='@122Lin' )
    depends_on( 'python@3.9.13', type=('run'), when='@123Lin' )
    depends_on( 'python@3.10.6', type=('run'), when='@BetaLin-2023-07-17' )
    depends_on( 'python@3.10.6', type=('run'), when='@BetaLin-2023-10-11' )
    depends_on( 'python@3.10.6', type=('run'), when='@BetaLin-2023-11-09' )

    phases = ['install']


    def install(self, spec, prefix):

      copy_tree('EngSketchPad/lib', prefix.lib)

      if (spec.satisfies('@122Lin')):
        copy_tree('OpenCASCADE-7.6.0/lib', prefix.lib)
        copy_tree('EngSketchPad/pyESP', prefix.pyESP)
      elif (spec.satisfies('@121Lin')):
        copy_tree('OpenCASCADE-7.6.0/lib', prefix.lib)
        copy_tree('EngSketchPad/pyESP', prefix.pyESP)
      elif (spec.satisfies('@120Lin')):
        copy_tree('OpenCASCADE-7.4.1/lib', prefix.lib)
        copy_tree('EngSketchPad/pyESP', prefix.pyESP)
      elif (spec.satisfies('@117Lin')):
        copy_tree('OpenCASCADE-7.3.1/lib', prefix.lib)
      else:
        copy_tree('OpenCASCADE-7.7.0/lib', prefix.lib)
        copy_tree('EngSketchPad/pyESP', prefix.pyESP)

      copy_tree('EngSketchPad/include', prefix.include)

      copy_tree('EngSketchPad/bin', prefix.bin)

      copy_tree('EngSketchPad/src', prefix.src)

      copy_tree('EngSketchPad/ESP', prefix.ESP)

    def setup_run_environment(self, run_env):

      run_env.prepend_path('LD_LIBRARY_PATH', self.prefix.lib)

      if (self.spec.satisfies('@117Lin')):
        run_env.prepend_path('PYTHONPATH', self.prefix.lib)
      else:
        run_env.prepend_path('PYTHONPATH', self.prefix.pyESP)

      run_env.set('ESP_START', 'google-chrome '+self.prefix.ESP+'/ESP-localhost7681.html')
      run_env.set('UDUNITS2_XML_PATH', self.prefix+'/src/CAPS/udunits/udunits2.xml')
      run_env.set('ESP_ROOT', self.prefix)
      run_env.set('ESP_ARCH', 'LINUX64')
      if (self.spec.satisfies('@117Lin')):
        run_env.set('CASREV', '7.3')
      elif (self.spec.satisfies('@120Lin')):
        run_env.set('CASREV', '7.4')
      elif (self.spec.satisfies('@121Lin')):
        run_env.set('CASREV', '7.6')
      elif (self.spec.satisfies('@122Lin')):
        run_env.set('CASREV', '7.6')
      else:
        run_env.set('CASREV', '7.7')

