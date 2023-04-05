from setuptools import setup, find_packages
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))
exec(open(moduleDirectory + "/gocart/__version__.py").read())


def readme():
    with open(moduleDirectory + '/README.md') as f:
        return f.read()


install_requires = [
    'pyyaml',
    'fundamentals',
    'astropy==5.1.0',
    'astropy-healpix',
    'numpy',
    'matplotlib',
    'healpy',
    'pandas',
    'tabulate',
    'ligo.skymap',
    'gcn-kafka'
]

# READ THE DOCS SERVERS
exists = os.path.exists("/home/docs/")
if exists:
    install_requires = ['fundamentals']
    c_exclude_list = ['healpy', 'astropy',
                      'numpy', 'sherlock', 'wcsaxes', 'HMpTy', 'ligo-gracedb', 'ligo.skymap', 'astropy==5.1.0', 'gcn-kafka', 'astropy_healpix']
    for e in c_exclude_list:
        try:
            install_requires.remove(e)
        except:
            pass

setup(name="gocart",
      version=__version__,
      description="Listen for, collect and convert multimessenger skymaps",
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.11',
          'Topic :: Utilities',
      ],
      keywords=['astronomy'],
      url='https://github.com/thespacedoctor/gocart',
      download_url='https://github.com/thespacedoctor/gocart/archive/v%(__version__)s.zip' % locals(
      ),
      author='David Young',
      author_email='d.r.young@qub.ac.uk',
      license='MIT',
      packages=find_packages(exclude=["*tests*"]),
      include_package_data=True,
      install_requires=install_requires,
      test_suite='nose2.collector.collector',
      tests_require=['nose2', 'cov-core'],
      entry_points={
          'console_scripts': ['gocart=gocart.cl_utils:main'],
      },
      zip_safe=False)
