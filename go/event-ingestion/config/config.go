package config

import (
	"fmt"

	"github.com/spf13/viper"
)

type Config struct {
	DatabaseURL                       string
	Port                              uint
	KafkaURL                          []string
	KafkaTopic                        string
	KafkaSASLUsername                 string
	KafkaSASLPassword                 string
	RedisURL                          string
	RedisMaster                       string
	RedisSentinels                    []string
	RedisUseSentinel                  bool
	RedisSentinelEnableAuthentication bool
	RedisSentinelPassword             string
	RedisCachingDatabase              int
}

var Conf Config

func GetConfig() Config {
	v := viper.New()

	v.SetDefault("port", 7998)

	// Kafka defaults
	v.SetDefault("kafka_url", "localhost:9092")
	v.SetDefault("kafka_topic", "test-topic")
	v.SetDefault("kafka_sasl_username", "")
	v.SetDefault("kafka_sasl_password", "")

	// Postgres defaults
	v.SetDefault("postgres_user", "lotus")
	v.SetDefault("postgres_password", "lotus")
	v.SetDefault("postgres_db", "lotus")

	// Redis defaults
	v.SetDefault("redis_use_sentinel", false)
	v.SetDefault("redis_sentinel_enable_authentication", false)
	v.SetDefault("redis_sentinel_password", "password")
	v.SetDefault("redis_caching_database", 0)

	v.BindEnv("database_url", "DATABASE_URL")
	v.BindEnv("postgres_user", "POSTGRES_USER")
	v.BindEnv("postgres_password", "POSTGRES_PASSWORD")
	v.BindEnv("postgres_port", "POSTGRES_PORT")
	v.BindEnv("postgres_host", "POSTGRES_HOST")
	v.BindEnv("postgres_db", "POSTGRES_DB")
	v.BindEnv("port", "PORT")
	v.BindEnv("kafka_url", "KAFKA_URL")
	v.BindEnv("kafka_topic", "EVENTS_TOPIC")
	v.BindEnv("kafka_sasl_username", "KAFKA_SASL_USERNAME")
	v.BindEnv("kafka_sasl_password", "KAFKA_SASL_PASSWORD")
	v.BindEnv("redis_url", "REDIS_TLS_URL", "REDIS_URL")
	v.BindEnv("redis_use_sentinel", "REDIS_USE_SENTINEL")
	v.BindEnv("redis_sentinel_service", "REDIS_SENTINEL_SERVICE")
	v.BindEnv("redis_sentinels", "REDIS_SENTINELS")
	v.BindEnv("redis_sentinel_enable_authentication", "REDIS_SENTINEL_ENABLE_AUTHENTICATION")
	v.BindEnv("redis_sentinel_password", "REDIS_SENTINEL_PASSWORD")
	v.BindEnv("redis_caching_database", "CACHING_REDIS_DATABASE")

	conf := Config{
		DatabaseURL:                       GetDatabaseURL(v),
		Port:                              v.GetUint("port"),
		KafkaURL:                          GetKafkaCluster(v),
		KafkaTopic:                        v.GetString("kafka_topic"),
		KafkaSASLUsername:                 v.GetString("kafka_sasl_username"),
		KafkaSASLPassword:                 v.GetString("kafka_sasl_password"),
		RedisURL:                          GetRedisURL(v),
		RedisUseSentinel:                  v.GetBool("redis_use_sentinel"),
		RedisMaster:                       v.GetString("redis_sentinel_service"),
		RedisSentinels:                    GetRedisSentinels(v),
		RedisSentinelEnableAuthentication: v.GetBool("redis_sentinel_enable_authentication"),
		RedisSentinelPassword:             v.GetString("redis_sentinel_password"),
		RedisCachingDatabase:              v.GetInt("redis_caching_database"),
	}
	fmt.Printf("Config: %+v", conf)

	return conf
}

func init() {
	Conf = GetConfig()
}
