module.exports = {
  apps: [{
    name: "oi_collection_daemon",
    script: "./scripts/collection_daemon.py",
    interpreter: "./.venv/bin/python",
    cwd: "/Users/suryavardhanchaluvadi/Desktop/Stock-Market-Project",
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: "production",
      PYTHONPATH: "."
    },
    error_file: "./logs/oi_collection_error.log",
    out_file: "./logs/oi_collection_out.log",
    merge_logs: true,
    time: true
  }]
}
