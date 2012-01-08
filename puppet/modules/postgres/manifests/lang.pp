define postgres::lang($ensure, $db) {
    case $ensure {
        present: {
            exec { "postgres lang-create $name $db":
                command => "/usr/bin/createlang $name $db",
                user => "postgres",
                unless => "/usr/bin/createlang -l $db| grep '$name  *|'",
		require => Exec["postgres db-create $db"]
            }
        }
        absent:  {
            exec { "postgres lang-remove $name $db":
                command => "/usr/bin/droplang $name $db",
                onlyif => "/usr/bin/createlang -l $db| grep '$name  *|'",
                user => "postgres"
            }
        }
        default: {
            fail "Invalid 'ensure' value '$ensure' for postgres::lang"
        }
    }
}
