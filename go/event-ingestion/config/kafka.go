package config

import (
	"github.com/spf13/viper"
	"strings"
)

func GetKafkaCluster(v *viper.Viper) []string {
	return strings.Split(v.GetString("kafka_url"), ",")
}
