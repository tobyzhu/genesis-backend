# coding=utf-8
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from baseinfo.models import Hdsysuser
from common.models import GenesisUserProfile


class Command(BaseCommand):
    help = '从 hdsysuser 同步 Django User + GenesisUserProfile（按 sys_userid 建账号）'

    def add_arguments(self, parser):
        parser.add_argument('--company', default='', help='仅同步指定公司')
        parser.add_argument(
            '--set-password',
            action='store_true',
            help='将 Django 密码设为 hdsysuser.sys_passwd（明文，仅开发/迁移用）',
        )

    def handle(self, *args, **options):
        company = (options.get('company') or '').strip()
        qs = Hdsysuser.objects.filter(flag='Y', sys_idtype='10')
        if company:
            qs = qs.filter(company=company)

        created_users = 0
        created_profiles = 0
        for h in qs:
            username = (h.sys_userid or '').strip()
            if not username:
                continue
            user, u_new = User.objects.get_or_create(
                username=username,
                defaults={
                    'is_staff': True,
                    'is_active': True,
                },
            )
            if u_new:
                created_users += 1
            if options.get('set_password') and h.sys_passwd:
                user.set_password(h.sys_passwd)
                user.save(update_fields=['password'])

            storelist = h.parse_storelist_codes()
            sl = ','.join(storelist) if storelist else ''

            profile, p_new = GenesisUserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company': h.company,
                    'default_storecode': h.storecode,
                    'storelist': sl,
                    'employee_code': h.sys_userid,
                    'display_name': h.sys_fullname or '',
                    'is_company_admin': h.is_sys_admin(),
                    'hdsysuser_uuid': h.uuid,
                    'costpriceflag': h.costpriceflag or 'N',
                },
            )
            if p_new:
                created_profiles += 1
            else:
                profile.company = h.company
                profile.default_storecode = h.storecode or profile.default_storecode
                if sl:
                    profile.storelist = sl
                profile.employee_code = h.sys_userid
                profile.display_name = h.sys_fullname or profile.display_name
                profile.is_company_admin = h.is_sys_admin()
                profile.hdsysuser_uuid = h.uuid
                profile.costpriceflag = h.costpriceflag or profile.costpriceflag
                profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                'sync done: new User=%s, new Profile=%s (total hdsysuser=%s)'
                % (created_users, created_profiles, qs.count())
            )
        )
