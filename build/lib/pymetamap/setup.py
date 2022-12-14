from setuptools import setup

def readme():
    with open('/Users/dj_jnr_99/PycharmProjects/relationz/pymetamap/README.rst') as f:
        return f.read()

setup(name='pymetamap',
      version='0.2',
      description='Python wrapper around MetaMap',
      long_description=readme(),
      url='https://github.com/AnthonyMRios/pymetamap',
      author='Anthony Rios',
      author_email='anthonymrios@gmail.com',
      classifiers=[
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English'
      ],
      license='Apache 2.0',
      packages=['pymetamap'],
      zip_safe=False)

