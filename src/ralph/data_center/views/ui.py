# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from ralph.admin.views.extra import RalphDetailView
from ralph.admin.views.extra import RalphDetailViewAdmin
from ralph.security.models import SecurityScan

from ralph.admin import RalphAdmin, RalphTabularInline, register

from ralph.assets.models.assets import (
    AssetExtra,
)

class DataCenterAssetSecurityInfo(
    RalphDetailView
):

    icon = 'lock'
    label = 'Security Info'
    name = 'security_info'
    url_name = 'datacenter_asset_security_info'

    def get_context_data(self, **kwargs):
        context = super(DataCenterAssetSecurityInfo, self).get_context_data(
            **kwargs
        )
        context['security_scan'] = SecurityScan.objects.filter(
            base_object=self.object).last()
        return context


class DataCenterAssetExtraInfo(
    RalphDetailView
):

    icon = 'refresh'
    name = 'extra_info'
    label = _('Extra Data')
    url_name = 'datacenter_asset_extra_info'

    def get_context_data(self, **kwargs):
        context = super(DataCenterAssetExtraInfo, self).get_context_data(
            **kwargs
        )
        context['asset_extras'] = AssetExtra.objects.filter(parent=self.object).all()

        # context['security_scan'] = SecurityScan.objects.filter(
        #     base_object=self.object).last()
        return context
