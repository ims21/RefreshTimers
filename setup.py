from distutils.core import setup
import setup_translate

pkg = 'Extensions.RefreshTimers'
setup (name = 'enigma2-plugin-extensions-refreshtimers',
	version = '0.48',
	description = 'plugin for refresh event timers',
	packages = [pkg],
	package_dir = {pkg: 'plugin'},
	package_data = {pkg: ['locale/*.pot', 'locale/*/LC_MESSAGES/*.mo']},
	cmdclass = setup_translate.cmdclass, # for translation
	)
