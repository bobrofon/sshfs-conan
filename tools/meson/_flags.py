def common_flags(settings):
    # https://github.com/bincrafters/conan-glib/blob/testing/2.62.4/conanfile.py
    defs = {}
    if str(settings.compiler) in ['gcc', 'clang']:
        if settings.arch == 'x86':
            defs['c_args'] = '-m32'
            defs['cpp_args'] = '-m32'
            defs['c_link_args'] = '-m32'
            defs['cpp_link_args'] = '-m32'
        elif settings.arch == 'x86_64':
            defs['c_args'] = '-m64'
            defs['cpp_args'] = '-m64'
            defs['c_link_args'] = '-m64'
            defs['cpp_link_args'] = '-m64'
    elif settings.compiler == 'Visual Studio':
        if settings.arch == 'x86':
            defs['c_link_args'] = '-MACHINE:X86'
            defs['cpp_link_args'] = '-MACHINE:X86'
        elif settings.arch == 'x86_64':
            defs['c_link_args'] = '-MACHINE:X64'
            defs['cpp_link_args'] = '-MACHINE:X64'

    return defs
