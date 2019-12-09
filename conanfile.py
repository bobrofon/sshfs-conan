import os

from conans import ConanFile, tools, Meson


class SshfsConan(ConanFile):
    name = "sshfs"
    version = "3.5.2"
    license = "GPLv2"
    author = "bobrofon@gmail.com"
    url = "https://github.com/bobrofon/sshfs-conan"
    description = "A network filesystem client to connect to SSH servers"
    requires = ["glib/2.58.3@bincrafters/stable", "fuse3/3.7.0@bobrofon/stable"]
    topics = ("ssh", "fuse", "fs")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "pkg_config"
    build_requires = "meson_installer/0.51.0@bincrafters/stable"

    def source(self):
        git = tools.Git(folder="sshfs")
        git.clone("https://github.com/libfuse/sshfs.git", "sshfs-3.5.2")

        # use conan generated pc files instead of package default pc files
        tools.replace_in_file("sshfs/meson.build", "dependency('glib-2.0')", "dependency('glib')")
        tools.replace_in_file("sshfs/meson.build", "dependency('gthread-2.0')", "dependency('glib')")
        tools.replace_in_file("sshfs/meson.build", "subdir('test')", "")

    def build(self):
        # disable osx frameworks support in conan pkgconfig generator
        try:
            tools.replace_in_file("glib.pc", " -framework Foundation -framework CoreServices -framework CoreFoundation", "")
        except:
            pass

        static = ["-D", "c_link_args=-static"] if not self.options.shared else []
        meson = Meson(self)
        meson.configure(source_folder="sshfs", build_folder="build",
                        args=static)
        meson.build()

    def package(self):
        self.copy("build/sshfs", dst="bin", keep_path=False)
