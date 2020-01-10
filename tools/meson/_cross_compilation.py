import os

from configparser import ConfigParser
from typing import Mapping, Optional, Union

from conans import ConanFile, tools
from conans.client.build.autotools_environment import AutoToolsBuildEnvironment
from conans.model.settings import Settings


def write_cross_file(path: str, conan: ConanFile) -> None:
    with tools.environment_append(AutoToolsBuildEnvironment(conan).vars):
        _write_cross_file(path, conan.settings)


def _write_cross_file(path: str, settings: Settings) -> None:
    cross_config = create_cross_config(settings)
    parser = ConfigParser()
    parser.update(cross_config)
    with open(path, 'w') as config_file:
        parser.write(config_file)


ConfigValue = Union[str, int]
ConfigSection = Mapping[str, ConfigValue]
CrossConfig = Mapping[str, ConfigSection]


def create_cross_config(settings: Settings) -> CrossConfig:
    config = {
        'binaries': {
            'c': os.getenv('CC'),
            'cpp': os.getenv('CXX'),
            'ld': os.getenv('LD'),
            'ar': os.getenv('AR'),
            'strip': os.getenv('STRIP'),
            'chost': os.getenv('CHOST'),
            'as': os.getenv('AS'),
            'ranlib': os.getenv('RANLIB'),
            'pkgconfig': tools.which('pkg-config')
        },
        'properties': {
            'c_args': os.getenv('CFLAGS'),
            'cpp_args': os.getenv('CXXFLAGS'),
            'c_link_args': os.getenv('LDFLAGS'),
            'cpp_link_args': os.getenv('LDFLAGS'),
            'needs_exe_wrapper': tools.cross_building(settings),
        },
        'host_machine': {
            'system': str(settings.os).lower(),
            'cpu_family': cpu_family(str(settings.arch)),
            'cpu': str(settings.arch),
            'endian': endian(str(settings.arch)),
        },
        'paths': {},
    }

    return to_cross_config(config)


RawConfigValue = Union[int, bool, str]
PartialDefinedConfigSection = Mapping[str, Optional[RawConfigValue]]
PartialDefinedCrossConfig = Mapping[str, PartialDefinedConfigSection]


def to_cross_config(config: PartialDefinedCrossConfig) -> CrossConfig:
    return to_ini(filter_undefined(config))


RawCrossConfigSection = Mapping[str, RawConfigValue]
RawCrossConfig = Mapping[str, RawCrossConfigSection]


def filter_undefined(config: PartialDefinedCrossConfig) -> RawCrossConfig:
    return {section_name: {key: value for key, value in section.items()
                           if value is not None}
            for section_name, section in config.items()}


def to_ini(config: RawCrossConfig) -> CrossConfig:
    return {section_name: {key: to_ini_value(value)
                           for key, value in section.items()}
            for section_name, section in config.items()}


def to_ini_value(value: RawConfigValue) -> ConfigValue:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        return "'{}'".format(value)
    return value


def cpu_family(arch: str) -> str:
    # TODO: Add proper cpu family detection
    return 'x86' if arch.startswith('x') or arch.startswith('i') else 'arm'


def endian(arch: str) -> str:
    # TODO: Add big endian detection/support
    return 'little'
