import glob

from conans import ConanFile, tools, Meson

import tools.meson as meson_tools

from tools import append_value


class SshfsConan(ConanFile):
    name = 'sshfs'
    version = '3.7.0'
    license = 'GPLv2'
    author = 'bobrofon@gmail.com'
    url = 'https://github.com/bobrofon/sshfs-conan'
    description = 'A network filesystem client to connect to SSH servers'
    requires = ('glib/2.64.0@bobrofon/stable', 'fuse3/3.9.1@bobrofon/stable')
    topics = ('ssh', 'fuse', 'fs')
    settings = ('os', 'compiler', 'build_type', 'arch')
    options = {'shared': [True, False]}
    default_options = {'shared': False,
                       'glib:with_elf': False}
    generators = 'pkg_config'
    build_requires = ('meson/0.54.0',
                      'pkg-config_installer/0.29.2@bincrafters/stable')

    patches = 'patches/*.patch'
    exports = 'tools/*.py', patches
    src_repo_folder = 'sshfs'

    cross_file_name = 'cross_file.txt'

    meson = None

    def configure(self):
        if self.options.shared == False:
            self.options['glib'].shared = False
            self.options['fuse3'].shared = False

    def source(self):
        git_tag = '{}-{}'.format(self.name, self.version)

        git = tools.Git(folder=self.src_repo_folder)
        git.clone('https://github.com/libfuse/sshfs.git', git_tag)

    @classmethod
    def apply_patches(cls):
        for patch in sorted(glob.glob(cls.patches)):
            print('Apply patch {}'.format(patch))
            tools.patch(base_path=cls.src_repo_folder, patch_file=patch)

    def build(self):
        self.apply_patches()
        tools.replace_in_file('glib.pc', ' -lresolv ', ' ')
        tools.replace_in_file('glib.pc', ' -lgio-2.0 ', ' ')
        tools.replace_in_file('glib.pc', ' -lgmodule-2.0 ', ' ')
        tools.replace_in_file('glib.pc', ' -lgobject-2.0 ', ' ')

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
            self.meson.configure(source_folder=self.src_repo_folder,
                                 build_folder='build',
                                 defs=defs, args=args)
        self.meson.build()

    def package(self):
        self.meson.install()
