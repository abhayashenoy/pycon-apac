class apache {
	package { [ "apache2", "libapache2-mod-wsgi" ]:
		ensure => installed,
	}

	service { apache2:
		ensure => running,
		enable => true,
		hasstatus => true,
		subscribe => [ Package["apache2"], Package["libapache2-mod-wsgi"] ]
	}

	# always enable output compression
	apache::module { "deflate": ensure => present }

	file {
		"/etc/apache2/mods-enabled":
			ensure => directory,
			checksum => mtime;
		"/etc/apache2/sites-enabled":
			ensure => directory,
			checksum => mtime;
		"/etc/apache2/ports.conf":
			ensure => present,
			checksum => mtime;
		"/etc/apache2/sites-enabled/000-default":
			ensure => absent;
	}

	# Notify this when apache needs a reload. This is only needed when
	# sites are added or removed, since a full restart then would be
	# a waste of time. When the module-config changes, a force-reload is
	# needed.
	exec { "reload-apache":
		command => "/usr/sbin/service apache2 reload",
		refreshonly => true,
		subscribe => [ File["/etc/apache2/mods-enabled"],
			File["/etc/apache2/sites-enabled"],
			File["/etc/apache2/ports.conf"] ]
	}

	exec { "force-reload-apache":
		command => "/usr/sbin/service apache2 force-reload",
		refreshonly => true,
	}
}

# Define an apache module. Debian packages place the module config
# into /etc/apache/mods-available.
#
# You can add a custom require (string) if the module depends on 
# packages that aren't part of the default apache package. Because of 
# the package dependencies, apache will automagically be included.
define apache::module ( $ensure = 'present', $require_package = 'apache2' ) {
	$mods = "/etc/apache2/mods"
	case $ensure {
		'present' : {
			exec { "/usr/sbin/a2enmod $name":
				unless => "/bin/sh -c '[ -L ${mods}-enabled/${name}.load ] \\
					&& [ ${mods}-enabled/${name}.load -ef ${mods}-available/${name}.load ]'",
				notify => Exec["force-reload-apache"],
				require => Package[$require_package],
			}
		}
		'absent': {
			exec { "/usr/sbin/a2dismod $name":
				onlyif => "/bin/sh -c '[ -L ${mods}-enabled/${name}.load ] \\
					&& [ ${mods}-enabled/${name}.load -ef ${mods}-available/${name}.load ]'",
				notify => Exec["force-reload-apache"],
				require => Package[$require_package],
			}
		}
	}
}

define apache::site ( $ensure = 'present', $require_package = 'apache2' ) {
	$sites = "/etc/apache2/sites"
	case $ensure {
		'present' : {
			exec { "/usr/sbin/a2ensite $name":
				unless => "/bin/sh -c '[ -L ${sites}-enabled/${name} ]'",
				notify => Exec["force-reload-apache"],
				require => Package[$require_package],
			}
		}
		'absent': {
			exec { "/usr/sbin/a2dissite $name":
				onlyif => "/bin/sh -c '[ -L ${sites}-enabled/${name} ]'",
				notify => Exec["force-reload-apache"],
				require => Package[$require_package],
			}
		}
	}
}
