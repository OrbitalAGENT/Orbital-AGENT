// orbital-agent/src/storage/migrate/migrate.go
package migrate

import (
    "database/sql"
    "embed"
    "fmt"
    "io/fs"
    
    _ "github.com/lib/pq"
)

//go:embed migrations/*.sql
var migrationFiles embed.FS

func RunMigrations(db *sql.DB) error {
    files, err := fs.ReadDir(migrationFiles, "migrations")
    if err != nil {
        return fmt.Errorf("error reading migrations: %w", err)
    }

    for _, file := range files {
        content, err := fs.ReadFile(migrationFiles, "migrations/"+file.Name())
        if err != nil {
            return fmt.Errorf("error reading %s: %w", file.Name(), err)
        }

        if _, err := db.Exec(string(content)); err != nil {
            return fmt.Errorf("error executing %s: %w", file.Name(), err)
        }
    }
    
    return nil
}
