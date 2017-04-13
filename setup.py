from setuptools import setup, find_packages

setup(
        name='KAMPER',
        version='1.0.0',
        description='kamper project',
        long_description=__doc__,
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=['Flask']
)
print("packages:", find_packages())
