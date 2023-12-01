package config

import (
	"fmt"
	"strings"

	"github.com/spf13/viper"
)

func GetDatabaseURL(v *viper.Viper) string {
	if v.GetString("database_url") != "" {
		return v.GetString("database_url")
	}
	postgresUser := v.GetString("postgres_user")
	postgresPassword := v.GetString("postgres_password")
	postgresHost := v.GetString("postgres_host")
	postgresPort := v.GetInt("postgres_port")
	postgresDB := v.GetString("postgres_db")

	return fmt.Sprintf("postgres://%s:%s@%s:%d/%s?sslmode=disable", postgresUser, postgresPassword, postgresHost, postgresPort, postgresDB)
}
