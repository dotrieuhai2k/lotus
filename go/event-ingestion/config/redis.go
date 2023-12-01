package config

import (
	"strings"

	"github.com/spf13/viper"
)

func GetRedisURL(v *viper.Viper) string {
	if v.GetString("redis_url") != "" {
		return v.GetString("redis_url")
	}
	return "redis://localhost:6379"
}
