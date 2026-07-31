from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = "common"

    def ready(self):
        # 保证 django_site 中存在 SITE_ID 对应记录，否则 admin / get_current_site 会 DoesNotExist
        try:
            from django.contrib.sites.models import Site
            from django.db.utils import OperationalError, ProgrammingError

            sid = 1
            try:
                from django.conf import settings

                sid = int(getattr(settings, "SITE_ID", 1) or 1)
            except (TypeError, ValueError):
                sid = 1
            if not Site.objects.filter(pk=sid).exists():
                from django.db import IntegrityError

                try:
                    Site.objects.create(
                        pk=sid,
                        domain="example.com",
                        name="example.com",
                    )
                except IntegrityError:
                    # 例如 domain 已被其它站点占用时，避免阻塞启动
                    pass
        except (OperationalError, ProgrammingError):
            pass
        try:
            import common.admin  # noqa: F401 — 扩展 Django User Admin
        except Exception:
            pass
