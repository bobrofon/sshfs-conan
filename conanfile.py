from conans import ConanFile, tools, Meson

import tools.meson as meson_tools

from tools import append_value


class SshfsConan(ConanFile):
    name = 'sshfs'
    version = '3.5.2'
    license = 'GPLv2'
    author = 'bobrofon@gmail.com'
    url = 'https://github.com/bobrofon/sshfs-conan'
    description = 'A network filesystem client to connect to SSH servers'
    requires = ('glib/2.58.3@bincrafters/stable', 'fuse3/3.7.0@bobrofon/stable')
    topics = ('ssh', 'fuse', 'fs')
    settings = ('os', 'compiler', 'build_type', 'arch')
    options = {'shared': [True, False]}
    default_options = {'shared': False}
    generators = 'pkg_config'
    build_requires = 'meson_installer/0.51.0@bincrafters/stable'

    exports = 'tools/*.py'  # for import tools module

    cross_file_name = 'cross_file.txt'

    meson = None

    def source(self):
        git_tag = '{}-{}'.format(self.name, self.version)

        git = tools.Git(folder='sshfs')
        git.clone('https://github.com/libfuse/sshfs.git', git_tag)

        # use conan generated pc files instead of package default pc files
        tools.replace_in_file('sshfs/meson.build',
                              "dependency('glib-2.0')",
                              "dependency('glib')")
        tools.replace_in_file('sshfs/meson.build',
                              "dependency('gthread-2.0')",
                              "dependency('glib')")

    def build(self):
        defs = meson_tools.common_flags(self.settings)

        if not self.options.shared:
            append_value(defs, 'c_link_args', '-static')

        args = []

        if tools.cross_building(self.settings):
            meson_tools.write_cross_file(self.cross_file_name, self)
            args += ['--cross-file', self.cross_file_name]

        # there is no usage of native compiler but we had to trick
        # meson's sanity check somehow
        meson_env = (meson_tools.with_fake_compiler()
                     if tools.cross_building(self.settings)
                     else tools.no_op())
        self.meson = Meson(self)
        with meson_env:
            self.meson.configure(source_folder='sshfs', build_folder='build',
                                 defs=defs, args=args)
        self.meson.build()

    def package(self):
        self.meson.install()
