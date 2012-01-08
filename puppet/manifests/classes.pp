stage { "first": before => Stage[main] }
stage { "last": require => Stage[main] }

class pycon {
	package { [vim, wajig, mercurial, tree, vim-puppet, "python2.6", "python2.6-dev" ]:
		ensure => installed,
	}
	user { pycon:
		ensure => present,
		gid => pycon,
		uid => 1001,
		home => "/home/pycon",
		shell => "/bin/bash",
		require => Group[pycon]
	}
	group { pycon:
		ensure => present,
		gid => 1001,
	}
	file { "/home/pycon":
		ensure => directory,
		owner => pycon,
		group => pycon,
		require => [ User[pycon], Group[pycon] ],
	}
}

class web {
	include apache
	$run = "/var/run/pycon"
	$co = "/var/www/pycon"
	$bin = "$co/bin"
	$hostname = "ec2-122-248-199-190.ap-southeast-1.compute.amazonaws.com"
	vcsrepo { "$co":
		path => "$co",
		ensure => latest,
		provider => hg,
		source => "/home/ubuntu/repo/pycon",
		revision => tip,
		require => File["$co"],
		owner => 'www-data',
		group => 'www-data',
		notify => File["$co/web2py"];
	}
	file { 
		"/var/www":
			owner => "www-data",
			group => "www-data";
		"$run":
			ensure => directory,
			owner => "www-data",
			group => "www-data";
		"$run/cache":
			ensure => directory,
			owner => "www-data",
			group => "www-data",
			require => File["$run"];
		"$run/sessions":
			ensure => directory,
			owner => "www-data",
			group => "www-data",
			require => File["$run"];
		"/var/log/pycon":
			ensure => directory,
			owner => 'www-data',
			group => 'www-data';
		"$co":
			ensure => directory,
			owner => 'www-data',
			group => 'www-data';
		"$co/web2py":
			ensure => directory,
			recurse => true,
			owner => 'www-data',
			group => 'www-data';
		"/etc/apache2/sites-available/pycon":
			ensure => present,
			owner => root,
			group => root,
			content => template("apache-site.erb"),
			notify => Service[apache2];
	}
	exec { 
		"virtualenv":
			command => "/usr/bin/python2.6 virtualenv.py --no-site-packages --distribute .",
			cwd => "$co",
			creates => "$bin/python",
			require => Vcsrepo["$co"],
			user => "www-data";
		"psycopg2":
			command => "$co/bin/pip install psycopg2",
			cwd => "$co",
			creates => "$co/lib/python2.7/site-packages/psycopg2",
			require => Exec["virtualenv"],
			user => "www-data";
	}
	apache::site { pycon:
		ensure => present,
		require => [ File["/etc/apache2/sites-available/pycon"] ]
	}
}

class db {
	include postgres
	postgres::role { pycon:
		ensure => present,
		password => pycon
	}
	postgres::database { pycon:
		ensure => present,
		owner => pycon
	}
}

class {
	"pycon": stage => first;
	"db": stage => main;
	"web": stage => last;
}
