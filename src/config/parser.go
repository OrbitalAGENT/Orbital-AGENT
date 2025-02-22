// orbital-agent/src/config/parser.go
package config

import (
    "os"
    "gopkg.in/yaml.v3"
)

type ServerConfig struct {
    Host     string `yaml:"host"`
    Port     int    `yaml:"port"`
    LogLevel string `yaml:"log_level"`
}

func LoadConfig(path string) (*ServerConfig, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }

    var cfg ServerConfig
    if err := yaml.Unmarshal(data, &cfg); err != nil {
        return nil, err
    }
    
    return &cfg, nil
}
