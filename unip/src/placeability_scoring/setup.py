# from setuptools import setup, find_packages

# setup(
#   name='placeability_scoring',
#   version='0.0.0',
#   packages=['placeability_scoring', 'placeability_scoring.mapping', 'placeability_scoring.planning', 'placeability_scoring.log_data', 'placeability_scoring.reachability_maps', 'placeability_scoring.grasping', 'placeability_scoring.placeability'],
#   package_dir={'': 'src'},
#   install_requires=[],       # Add dependencies here if needed
#   author='Benno Wingender',
#   description='Placeability Scoring Module with all related components.',
#   # Add other metadata as needed
# ) 

from setuptools import find_packages, setup

package_name = 'placeability_scoring'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    # data_files=[
    #     ('share/ament_index/resource_index/packages',
    #         ['resource/' + package_name]),
    #     ('share/' + package_name, ['package.xml']),
    # ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='wingende',
    maintainer_email='s6bewing@uni-bonn.de',
    description='TODO: Package description',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'Static_Manipulation_full_pipe = placeability_scoring.Static_Manipulation_full_pipe:main'
        ],
    },
)