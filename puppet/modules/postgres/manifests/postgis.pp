define postgres::postgis($ensure, $db, $owner) {
    case $ensure {
        present: {
            exec { "postgres postgis-setup $db":
                command => "/usr/bin/psql $db -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql",
                user => "postgres",
                unless => "/usr/bin/psql -c '\\dt' $db| grep 'spatial_ref_sys  *|'",
		require => Exec["postgres lang-create plpgsql $db"]
            }
            exec { "postgres postgis-update $db":
                command => "/usr/bin/psql $db -f /usr/share/postgresql/8.4/contrib/postgis-1.5/spatial_ref_sys.sql",
                user => "postgres",
                unless => "/usr/bin/psql -c 'select count(*) from spatial_ref_sys' $db| grep '3749'",
		require => Exec["postgres postgis-setup $db"]
            }
            exec { "postgres postgis-owner db $db":
                command => "/usr/bin/psql $db -c 'ALTER TABLE spatial_ref_sys OWNER to $owner; ALTER TABLE geometry_columns OWNER to $owner'",
                user => "postgres",
                unless => "/usr/bin/psql -c '\\dt' $db| grep 'geometry_columns *| table | $owner'",
		require => Exec["postgres postgis-update $db"]
            }
        }
        absent:  {
            exec { "postgres postgis-remove $db":
                command => "/usr/bin/psql -c 'DROP TABLE spatial_ref_sys; DROP TABLE geometry_columns;' $db $db",
                onlyif => "/usr/bin/psql -c '\\dt' $db| grep 'spatial_ref_sys  *|'",
                user => "postgres"
            }
        }
        default: {
            fail "Invalid 'ensure' value '$ensure' for postgres::lang"
        }
    }
}
