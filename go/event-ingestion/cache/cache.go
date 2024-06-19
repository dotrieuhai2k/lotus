package cache

import (
	"context"
	"errors"
	"time"

	"github.com/redis/go-redis/v9"
	"github.com/uselotus/lotus/go/event-ingestion/config"
)

type Cache interface {
	Get(key string) (string, error)
	Set(key string, value interface{}, expiration *time.Duration) error
}

type RedisCache struct {
	rdb               *redis.Client
	defaultExpiration time.Duration
}

var ctx = context.Background()

func (c *RedisCache) Get(key string) (string, error) {
	val, err := c.rdb.Get(ctx, key).Result()
	if err == redis.Nil {
		return "", nil
	}

	if err != nil {
		return "", err
	}

	return val, nil
}

func (c *RedisCache) Set(key string, value interface{}, expiration *time.Duration) error {
	var realExpiration time.Duration
	if expiration == nil {
		realExpiration = c.defaultExpiration
	} else {
		realExpiration = *expiration
	}
	return c.rdb.Set(ctx, key, value, realExpiration).Err()
}

func New(config config.Config) (Cache, error) {

	useSentinel := config.RedisUseSentinel
	var rdb redis.Client
	if useSentinel == true {
		redisSentinels := config.RedisSentinels
		if len(redisSentinels) == 0 {
			return nil, errors.New("redis sentinels is empty")
		}

		var opt redis.FailoverOptions
		enableAuthentication := config.RedisSentinelEnableAuthentication
		masterName := config.RedisMaster
		db := config.RedisCachingDatabase
		if enableAuthentication == true {
			sentinelPassword := config.RedisSentinelPassword
			if sentinelPassword == "" {
				return nil, errors.New("must set REDIS_SENTINEL_PASSWORD when enable redis sentinel authentication")
			} else {
				opt = redis.FailoverOptions{MasterName: masterName, SentinelAddrs: redisSentinels, SentinelPassword: sentinelPassword, DB: db}
			}
		} else {
			opt = redis.FailoverOptions{MasterName: masterName, SentinelAddrs: redisSentinels, DB: db}
		}

		rdb = *redis.NewFailoverClient(&opt)
	} else {
		address := config.RedisURL
		if address == "" {
			return nil, errors.New("redis url is empty")
		}
		opt, err := redis.ParseURL(address)
		if err != nil {
			return nil, err
		}
		rdb = *redis.NewClient(opt)
	}
	cache := &RedisCache{
		rdb:               &rdb,
		defaultExpiration: 10 * time.Second,
	}

	return cache, nil
}
