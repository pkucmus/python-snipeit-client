import html
import json

from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import mark_safe
from django_classified.admin import ItemAdmin
from django_classified.models import Item, Section, Area, Group
from markdown import markdown

from service.providers import snipeit


def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


make_active.short_description = 'Mark items as active'


def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


make_inactive.short_description = 'Mark items as inactive'


class SnipeItItemAdmin(ItemAdmin):
    change_list_template = 'snipeit/import_from_snipeit.html'
    readonly_fields = ('asset', )
    list_display = (
        'title',
        'asset',
        'group',
        'area',
        'user',
        'is_active',
        'posted',
        'updated'
    )
    actions = [make_active, make_inactive]

    def asset(self, obj):
        if obj.slug.startswith('snipeit_asset_'):
            asset_tag = obj.slug.lstrip('snipeit_asset_')
            return mark_safe((
                '<a href="{snipeit_url}/hardware/{asset_tag}">{asset_tag}</a>'
            ).format(
                snipeit_url=settings.SNIPEIT_URL,
                asset_tag=asset_tag
            ))
        else:
            return mark_safe(
                '<img '
                'src="/static/admin/img/icon-no.svg" '
                'title="not from SnipeIt">'
            )

    def get_urls(self):
        urls = super().get_urls()
        snipeit_urls = [
            path(
                'import_from_snipeit/',
                self.import_from_snipeit,
                name='import-from-snipeit'
            )
        ]
        return snipeit_urls + urls

    def get_snipeit_asset_description(self, asset_data):
        markdown_text = ''
        markdown_text += (
            '#### **{}** {}\n'.format(
                asset_data['manufacturer']['name'],
                asset_data['model']['name']
            )
        )

        if asset_data['custom_fields']['HW Info']['value']:
            hw_info = json.loads(
                html.unescape(
                    asset_data['custom_fields']['HW Info']['value']
                )
            )
            for key, value in hw_info.items():
                markdown_text += f'- {key}\n'
                for item in value:
                    if item:
                        markdown_text += f'    - {item}\n'

        return mark_safe(markdown(markdown_text))

    def get_item_title(self, asset_data):
        return '{} {}'.format(
            asset_data['manufacturer']['name'],
            asset_data['model']['name']
        )

    def import_from_snipeit(self, request):
        data = snipeit.endpoints.list_hardware({'status_id': 5})
        section, __ = Section.objects.get_or_create(title='IT')
        created_count = 0
        already_staged_count = 0
        for asset_data in data['rows']:
            item, created = Item.objects.get_or_create(
                slug='snipeit_asset_{}'.format(asset_data['asset_tag']),
                defaults={
                    'user': request.user,
                    'area': Area.objects.get_or_create(
                        title=asset_data['location']['name']
                    )[0],
                    'group': Group.objects.get_or_create(
                        title=asset_data['category']['name'],
                        defaults={
                            'section': section,
                        }
                    )[0],
                    'title': self.get_item_title(asset_data),
                    'description': self.get_snipeit_asset_description(
                        asset_data
                    ),
                    'price': 10000.00,
                    'is_active': False,
                }
            )
            if created:
                created_count += 1
            else:
                already_staged_count += 1
        self.message_user(
            request,
            (
                'Imported {} hardware assets, '
                '{} assets were already staged. '
                'Total from SnipeIt was {}.'
            ).format(created_count, already_staged_count, data['total'])
        )
        return HttpResponseRedirect('../')


admin.site.unregister(Item)
admin.site.register(Item, SnipeItItemAdmin)
