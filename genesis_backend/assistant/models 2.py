#coding = utf-8
from django.conf import settings
from django.db import models


class AssistantThread(models.Model):
    """智能助手会话（按登录用户隔离）。"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assistant_threads",
    )
    title = models.CharField(max_length=200, blank=True, default="")
    company = models.CharField(max_length=16, blank=True, default="")
    storecode = models.CharField(max_length=16, blank=True, default="")
    agent_id = models.CharField(max_length=32, default="deepseek")
    profile_id = models.CharField(max_length=32, default="general")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assistant_thread"
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return self.title or f"Thread #{self.pk}"


class AssistantMessage(models.Model):
    """会话内一条消息（用户或助手）。"""

    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    thread = models.ForeignKey(
        AssistantThread,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=16)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    sequence = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "assistant_message"
        ordering = ("sequence", "id")


class VipLifecycleSnapshot(models.Model):
    """客户生命周期快照（按日、按会员），用于观察 active→at_risk→sleeping 迁移。"""

    company = models.CharField(max_length=16, db_index=True)
    storecode = models.CharField(max_length=16, db_index=True)
    snapshot_date = models.DateField(db_index=True)
    vipuuid = models.CharField(max_length=36)
    segment = models.CharField(max_length=32)
    sleeping_grade = models.CharField(max_length=32, blank=True, default="")
    days_since_last_visit = models.IntegerField(null=True, blank=True)
    vip_status = models.CharField(max_length=8, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vip_lifecycle_snapshot"
        unique_together = (("company", "storecode", "snapshot_date", "vipuuid"),)
        indexes = [
            models.Index(fields=["company", "storecode", "snapshot_date", "segment"]),
        ]


class VipLifecycleSnapshotSummary(models.Model):
    """门店每日生命周期分级汇总。"""

    company = models.CharField(max_length=16)
    storecode = models.CharField(max_length=16)
    snapshot_date = models.DateField()
    segment_counts = models.JSONField(default=dict, blank=True)
    total_vips = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vip_lifecycle_snapshot_summary"
        unique_together = (("company", "storecode", "snapshot_date"),)
