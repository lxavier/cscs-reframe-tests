# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn


class CudaCheck(rfm.RegressionTest):
    def __init__(self):
        self.valid_systems = ['daint:gpu', 'dom:gpu', 'kesch:cn', 'tiger:gpu',
                              'arolla:cn', 'tsa:cn']
        self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu']
        if self.current_system.name == 'kesch':
            self.valid_prog_environs += ['PrgEnv-cray-nompi',
                                         'PrgEnv-gnu-nompi']
        elif self.current_system.name in ['arolla', 'tsa']:
            self.valid_prog_environs += ['PrgEnv-gnu-nompi']

        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'CUDA', 'essentials')

        if self.current_system.name == 'kesch':
            self.modules = ['cudatoolkit/8.0.61']
        elif self.current_system.name in ['arolla', 'tsa']:
            self.modules = ['cuda/10.1.243']
        else:
            self.modules = ['craype-accel-nvidia60']

        self.num_gpus_per_node = 1
        self.nvidia_sm = '60'
        if self.current_system.name == 'kesch':
            self.exclusive_access = True
            self.nvidia_sm = '37'
        elif self.current_system.name in ['arolla', 'tsa']:
            self.exclusive_access = True
            self.nvidia_sm = '70'

        self.maintainers = ['AJ', 'SK']
        self.tags = {'production', 'craype', 'external-resources'}


@rfm.required_version('>=2.14')
@rfm.simple_test
class CudaMatrixmulCublasCheck(CudaCheck):
    def __init__(self):
        super().__init__()
        self.descr = 'Implements matrix multiplication using CUBLAS'
        self.sourcepath = 'matrixmulcublas.cu'
        self.build_system = 'SingleSource'
        self.build_system.cxxflags = ['-I.', '-ccbin g++', '-m64',
                                      '-arch=sm_%s' % self.nvidia_sm]
        self.build_system.ldflags = ['-lcublas']
        self.sanity_patterns = sn.assert_found(
            r'Comparing CUBLAS Matrix Multiply with CPU results: PASS',
            self.stdout)


@rfm.required_version('>=2.14')
@rfm.simple_test
class CudaDeviceQueryCheck(CudaCheck):
    def __init__(self):
        super().__init__()
        self.descr = 'Queries the properties of the CUDA devices'
        self.sourcepath = 'devicequery.cu'
        self.build_system = 'SingleSource'
        self.build_system.cxxflags = ['-I.', '-ccbin g++', '-m64',
                                      '-arch=sm_%s' % self.nvidia_sm]
        self.sanity_patterns = sn.assert_found(r'Result = PASS', self.stdout)


@rfm.required_version('>=2.14')
@rfm.simple_test
class CudaConcurrentKernelsCheck(CudaCheck):
    def __init__(self):
        super().__init__()
        self.descr = 'Use of streams for concurrent execution'
        self.sourcepath = 'concurrentkernels.cu'
        self.build_system = 'SingleSource'
        self.build_system.cxxflags = ['-I.', '-ccbin g++', '-m64',
                                      '-arch=sm_%s' % self.nvidia_sm]
        self.build_system.ldflags = ['-lcublas']
        self.sanity_patterns = sn.assert_found(r'Test passed', self.stdout)


@rfm.required_version('>=2.14')
@rfm.simple_test
class CudaSimpleMPICheck(CudaCheck):
    def __init__(self):
        super().__init__()
        self.descr = 'Simple example demonstrating how to use MPI with CUDA'
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'CUDA', 'simplempi')
        self.executable = './simplempi'
        self.num_tasks = 2
        self.num_tasks_per_node = 2
        self.sanity_patterns = sn.assert_found(r'Result = PASS', self.stdout)
        if self.current_system.name == 'kesch':
            self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu']
            self.variables = {'G2G': '0'}
            self.num_gpus_per_node = 2
        elif self.current_system.name in ['arolla', 'tsa']:
            self.valid_prog_environs = ['PrgEnv-gnu']
            self.num_gpus_per_node = 2
        else:
            self.variables = {'CRAY_CUDA_MPS': '1'}

        self.build_system = 'Make'
        self.build_system.cxxflags = ['-I.', '-ccbin g++', '-m64',
                                      '-arch=sm_%s' % self.nvidia_sm]
        self.build_system.ldflags = ['-lcublas']
