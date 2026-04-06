#!/bin/bash
# Docker 内启动 Jekyll：先把依赖装进挂载目录下的 vendor/bundle（.gitignore 已忽略），
# 避免与镜像预装 gem / 宿主机 Gemfile.lock 不一致导致的 Bundler::GemNotFound。
set -e
cd /srv/jekyll

bundle config set --local path "vendor/bundle"

CONFIG_FILE=_config.yml

echo "Entry point: bundle install + jekyll serve (gems -> vendor/bundle)"

/bin/bash -c "bundle config set --local path 'vendor/bundle' && bundle install --jobs 4 --retry 3 && exec bundle exec jekyll serve --watch --port=8080 --host=0.0.0.0 --livereload --verbose --trace --force_polling" &

while true; do
  inotifywait -q -e modify,move,create,delete "$CONFIG_FILE"

  if [ $? -eq 0 ]; then
    echo "Change detected to $CONFIG_FILE, restarting Jekyll"
    jekyll_pid=$(pgrep -f jekyll || true)
    if [ -n "$jekyll_pid" ]; then
      kill -KILL "$jekyll_pid" 2>/dev/null || true
    fi
    # 仅改 _config 时不必重复 bundle install
    /bin/bash -c "bundle config set --local path 'vendor/bundle' && exec bundle exec jekyll serve --watch --port=8080 --host=0.0.0.0 --livereload --verbose --trace --force_polling" &
  fi
done
