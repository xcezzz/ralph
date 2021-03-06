from django.contrib.auth import get_user_model
from import_export import fields, resources, widgets

from ralph.accounts.models import Region
from ralph.assets.models import assets, base
from ralph.back_office.models import (
    BackOfficeAsset,
    OfficeInfrastructure,
    Warehouse
)
from ralph.data_center.models import networks, physical
from ralph.data_importer.mixins import (
    ImportForeignKeyMeta,
    ImportForeignKeyMixin
)
from ralph.data_importer.widgets import (
    AssetServiceEnvWidget,
    BaseObjectManyToManyWidget,
    BaseObjectWidget,
    ImportedForeignKeyWidget,
    NullStringWidget,
    UserManyToManyWidget,
    UserWidget
)
from ralph.domains.models.domains import Domain
from ralph.licences.models import (
    BaseObjectLicence,
    Licence,
    LicenceType,
    LicenceUser,
    Software
)
from ralph.operations.models import Operation, OperationType
from ralph.supports.models import BaseObjectsSupport, Support, SupportType

RalphResourceMeta = type(
    'RalphResourceMeta',
    (
        ImportForeignKeyMeta,
        resources.ModelDeclarativeMetaclass,
        resources.Resource
    ),
    {}
)


class RalphModelResource(
    ImportForeignKeyMixin,
    resources.ModelResource,
    metaclass=RalphResourceMeta
):
    pass


class AssetModelResource(RalphModelResource):
    manufacturer = fields.Field(
        column_name='manufacturer',
        attribute='manufacturer',
        widget=ImportedForeignKeyWidget(assets.Manufacturer),
    )
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ImportedForeignKeyWidget(assets.Category),
    )

    class Meta:
        model = assets.AssetModel


class CategoryResource(RalphModelResource):
    parent = fields.Field(
        column_name='parent',
        attribute='parent',
        widget=ImportedForeignKeyWidget(assets.Category),
    )

    class Meta:
        model = assets.Category


class BackOfficeAssetResource(RalphModelResource):
    parent = fields.Field(
        column_name='parent',
        attribute='parent',
        widget=ImportedForeignKeyWidget(assets.Asset),
    )
    service_env = fields.Field(
        column_name='service_env',
        attribute='service_env',
        widget=AssetServiceEnvWidget(assets.ServiceEnvironment, 'name'),
    )
    model = fields.Field(
        column_name='model',
        attribute='model',
        widget=ImportedForeignKeyWidget(assets.AssetModel),
    )
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=UserWidget(get_user_model()),
    )
    owner = fields.Field(
        column_name='owner',
        attribute='owner',
        widget=UserWidget(get_user_model()),
    )
    warehouse = fields.Field(
        column_name='warehouse',
        attribute='warehouse',
        widget=ImportedForeignKeyWidget(Warehouse),
    )
    region = fields.Field(
        column_name='region',
        attribute='region',
        widget=ImportedForeignKeyWidget(Region),
    )
    property_of = fields.Field(
        column_name='property_of',
        attribute='property_of',
        widget=ImportedForeignKeyWidget(assets.AssetHolder),
    )
    budget_info = fields.Field(
        column_name='budget_info',
        attribute='budget_info',
        widget=ImportedForeignKeyWidget(assets.BudgetInfo),
    )

    class Meta:
        model = BackOfficeAsset
        prefetch_related = (
            'tags',
        )
        exclude = ('content_type', 'asset_ptr', 'baseobject_ptr',)

    def dehydrate_price(self, bo_asset):
        return str(bo_asset.price)

    def dehydrate_depreciation_rate(self, bo_asset):
        return str(bo_asset.depreciation_rate)


class ServerRoomResource(RalphModelResource):
    data_center = fields.Field(
        column_name='data_center',
        attribute='data_center',
        widget=ImportedForeignKeyWidget(physical.DataCenter),
    )

    class Meta:
        model = physical.ServerRoom


class RackResource(RalphModelResource):
    server_room = fields.Field(
        column_name='server_room',
        attribute='server_room',
        widget=ImportedForeignKeyWidget(physical.ServerRoom),
    )

    class Meta:
        model = physical.Rack


class NetworkResource(RalphModelResource):
    data_center = fields.Field(
        column_name='data_center',
        attribute='data_center',
        widget=ImportedForeignKeyWidget(physical.DataCenter),
    )
    network_environment = fields.Field(
        column_name='network_environment',
        attribute='network_environment',
        widget=ImportedForeignKeyWidget(networks.NetworkEnvironment),
    )
    kind = fields.Field(
        column_name='kind',
        attribute='kind',
        widget=ImportedForeignKeyWidget(networks.NetworkKind),
    )

    class Meta:
        model = networks.Network


class IPAddressResource(RalphModelResource):

    base_object = fields.Field(
        column_name='asset',
        attribute='asset',
        widget=ImportedForeignKeyWidget(assets.BaseObject),
    )

    network = fields.Field(
        column_name='network',
        attribute='network',
        widget=ImportedForeignKeyWidget(networks.Network),
    )

    class Meta:
        model = networks.IPAddress


class DataCenterAssetResource(RalphModelResource):
    parent = fields.Field(
        column_name='parent',
        attribute='parent',
        widget=ImportedForeignKeyWidget(physical.DataCenterAsset),
    )
    service_env = fields.Field(
        column_name='service_env',
        attribute='service_env',
        widget=AssetServiceEnvWidget(assets.ServiceEnvironment, 'name'),
    )
    model = fields.Field(
        column_name='model',
        attribute='model',
        widget=ImportedForeignKeyWidget(assets.AssetModel),
    )
    rack = fields.Field(
        column_name='rack',
        attribute='rack',
        widget=ImportedForeignKeyWidget(physical.Rack),
    )
    budget_info = fields.Field(
        column_name='budget_info',
        attribute='budget_info',
        widget=ImportedForeignKeyWidget(assets.BudgetInfo),
    )
    management_ip = fields.Field(
        column_name='management_ip',
        attribute='management_ip',
        widget=NullStringWidget(),
    )

    class Meta:
        model = physical.DataCenterAsset
        select_related = (
            'service_env__service', 'service_env__environment',
            'rack__server_room__data_center',
        )
        prefetch_related = (
            'tags',
        )
        exclude = ('content_type', 'asset_ptr', 'baseobject_ptr', 'connections')

    def dehydrate_price(self, dc_asset):
        return str(dc_asset.price)

    def dehydrate_depreciation_rate(self, dc_asset):
        return str(dc_asset.depreciation_rate)


class ConnectionResource(RalphModelResource):
    outbound = fields.Field(
        column_name='outbound',
        attribute='outbound',
        widget=ImportedForeignKeyWidget(physical.DataCenterAsset),
    )
    inbound = fields.Field(
        column_name='outbound',
        attribute='outbound',
        widget=ImportedForeignKeyWidget(physical.DataCenterAsset),
    )

    class Meta:
        model = physical.Connection


class LicenceResource(RalphModelResource):
    manufacturer = fields.Field(
        column_name='manufacturer',
        attribute='manufacturer',
        widget=ImportedForeignKeyWidget(assets.Manufacturer),
    )
    licence_type = fields.Field(
        column_name='licence_type',
        attribute='licence_type',
        widget=ImportedForeignKeyWidget(LicenceType),
    )
    software = fields.Field(
        column_name='software',
        attribute='software',
        widget=ImportedForeignKeyWidget(Software),
    )
    region = fields.Field(
        column_name='region',
        attribute='region',
        widget=ImportedForeignKeyWidget(Region),
    )
    office_infrastructure = fields.Field(
        column_name='office_infrastructure',
        attribute='office_infrastructure',
        widget=ImportedForeignKeyWidget(OfficeInfrastructure),
    )

    class Meta:
        model = Licence
        prefetch_related = (
            'tags', 'users', 'licenceuser_set__user',
            'baseobjectlicence_set__base_object'
        )
        exclude = ('content_type', 'baseobject_ptr', )

    def dehydrate_price(self, licence):
        return str(licence.price)


class SupportTypeResource(RalphModelResource):

    class Meta:
        model = SupportType


class SupportResource(RalphModelResource):
    support_type = fields.Field(
        column_name='support_type',
        attribute='support_type',
        widget=ImportedForeignKeyWidget(SupportType),
    )
    base_objects = fields.Field(
        column_name='base_objects',
        attribute='base_objects',
        widget=BaseObjectManyToManyWidget(base.BaseObject),
    )
    region = fields.Field(
        column_name='region',
        attribute='region',
        widget=ImportedForeignKeyWidget(Region),
    )
    budget_info = fields.Field(
        column_name='budget_info',
        attribute='budget_info',
        widget=ImportedForeignKeyWidget(assets.BudgetInfo),
    )
    property_of = fields.Field(
        column_name='property_of',
        attribute='property_of',
        widget=ImportedForeignKeyWidget(assets.AssetHolder),
    )

    class Meta:
        model = Support

    def dehydrate_price(self, support):
        return str(support.price)


class ProfitCenterResource(RalphModelResource):
    business_segment = fields.Field(
        column_name='business_segment',
        attribute='business_segment',
        widget=ImportedForeignKeyWidget(assets.BusinessSegment),
    )

    class Meta:
        model = assets.ProfitCenter


class ServiceResource(RalphModelResource):
    profit_center = fields.Field(
        column_name='profit_center',
        attribute='profit_center',
        widget=ImportedForeignKeyWidget(assets.ProfitCenter),
    )
    business_owners = fields.Field(
        column_name='business_owners',
        attribute='business_owners',
        widget=UserManyToManyWidget(get_user_model()),
    )
    technical_owners = fields.Field(
        column_name='technical_owners',
        attribute='technical_owners',
        widget=UserManyToManyWidget(get_user_model()),
    )

    class Meta:
        model = assets.Service


class ServiceEnvironmentResource(RalphModelResource):
    service = fields.Field(
        column_name='service',
        attribute='service',
        widget=ImportedForeignKeyWidget(assets.Service),
    )
    environment = fields.Field(
        column_name='environment',
        attribute='environment',
        widget=ImportedForeignKeyWidget(assets.Environment),
    )

    class Meta:
        model = assets.ServiceEnvironment


class BaseObjectLicenceResource(RalphModelResource):
    licence = fields.Field(
        column_name='licence',
        attribute='licence',
        widget=ImportedForeignKeyWidget(Licence),
    )
    base_object = fields.Field(
        column_name='base_object',
        attribute='base_object',
        widget=BaseObjectWidget(base.BaseObject),
    )

    class Meta:
        model = BaseObjectLicence


class LicenceUserResource(RalphModelResource):
    licence = fields.Field(
        column_name='licence',
        attribute='licence',
        widget=ImportedForeignKeyWidget(Licence),
    )
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=UserWidget(get_user_model()),
    )

    class Meta:
        model = LicenceUser


class BaseObjectsSupportResource(RalphModelResource):
    support = fields.Field(
        column_name='support',
        attribute='support',
        widget=ImportedForeignKeyWidget(Support),
    )
    baseobject = fields.Field(
        column_name='baseobject',
        attribute='baseobject',
        widget=BaseObjectWidget(base.BaseObject),
    )

    class Meta:
        model = BaseObjectsSupport


class RackAccessoryResource(RalphModelResource):
    accessory = fields.Field(
        column_name='accessory',
        attribute='accessory',
        widget=ImportedForeignKeyWidget(physical.Accessory),
    )
    rack = fields.Field(
        column_name='rack',
        attribute='rack',
        widget=ImportedForeignKeyWidget(physical.Rack),
    )

    class Meta:
        model = physical.RackAccessory


class RegionResource(RalphModelResource):
    users = fields.Field(
        column_name='users',
        attribute='users',
        widget=UserManyToManyWidget(get_user_model()),
    )

    class Meta:
        model = Region


class AssetHolderResource(RalphModelResource):

    class Meta:
        model = assets.AssetHolder


class OfficeInfrastructureResource(RalphModelResource):

    class Meta:
        model = OfficeInfrastructure


class BudgetInfoResource(RalphModelResource):

    class Meta:
        model = assets.BudgetInfo


class DomainResource(RalphModelResource):
    business_segment = fields.Field(
        column_name='business_segment',
        attribute='business_segment',
        widget=widgets.ForeignKeyWidget(assets.BusinessSegment),
    )
    business_owner = fields.Field(
        column_name='business_owner',
        attribute='business_owner',
        widget=UserWidget(get_user_model()),
    )
    technical_owner = fields.Field(
        column_name='technical_owner',
        attribute='technical_owner',
        widget=UserWidget(get_user_model()),
    )
    domain_holder = fields.Field(
        column_name='domain_holder',
        attribute='domain_holder',
        widget=widgets.ForeignKeyWidget(assets.AssetHolder),
    )
    service_env = fields.Field(
        column_name='service_env',
        attribute='service_env',
        widget=AssetServiceEnvWidget(assets.ServiceEnvironment),
    )

    class Meta:
        model = Domain


class OperationTypeResource(RalphModelResource):
    parent = fields.Field(
        column_name='parent',
        attribute='parent',
        widget=ImportedForeignKeyWidget(OperationType),
    )

    class Meta:
        model = OperationType


class OperationResource(RalphModelResource):
    type = fields.Field(
        column_name='type',
        attribute='type',
        widget=ImportedForeignKeyWidget(OperationType),
    )

    class Meta:
        model = Operation
