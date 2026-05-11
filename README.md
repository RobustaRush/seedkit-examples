# seedkit-examples

Reference Django projects scaffolded by the [seedkit](https://github.com/RobustaRush/seedkit) skill, paired with the prompts that produced them.

Each subdirectory is a fresh project generated end-to-end by `claude -p` running the matching testcase from `seedkit/testcases/`. The first section of every project's `README.md` is the verbatim `/seedkit` prompt — answers to every Foundation / add-on / production question — so the exact configuration is reproducible.

## Projects

- [`01-minimal-blog/`](01-minimal-blog/) — a tiny blog to verify the skill works end-to-end.
- [`02-shop/`](02-shop/) — small e-commerce site with admin and SMTP transactional email.
- [`03-jobs-board/`](03-jobs-board/) — job board with background email notifications and a daily digest.
- [`04-media-vault/`](04-media-vault/) — media-heavy app where uploads land in S3 and processing runs as Redis-queued background tasks.
- [`05-orbit-demo/`](05-orbit-demo/) — scratch project to exercise django-orbit and verify outbound mail flows are captured.
- [`06-silk-lab/`](06-silk-lab/) — profile a few request paths with django-silk and run a simple background email task on the DB backend.
- [`07-vps-saas/`](07-vps-saas/) — production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy.
- [`08-fly-app/`](08-fly-app/) — production app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.
- [`09-ssh-deploy/`](09-ssh-deploy/) — production app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Reproducing

From the parent repo:

```sh
cd seedkit
./run-tests.sh                  # all cases
./run-tests.sh 02 07            # specific cases
```

Output lands directly here. Per-run logs (build phase + review phase) live in `logs/`.
