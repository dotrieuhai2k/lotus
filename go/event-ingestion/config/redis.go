package config

import (
	"github.com/spf13/viper"
	"strings"
)

func GetRedisURL(v *viper.Viper) string {
	if v.GetString("redis_url") != "" {
		return v.GetString("redis_url")
	}
	return "redis://localhost:6379"
}
func GetRedisSentinels(v *viper.Viper) []string {
	return strings.Split(v.GetString("redis_sentinels"), ",")
}
